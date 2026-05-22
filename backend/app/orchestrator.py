import asyncio
import json
import logging
from pathlib import Path
from typing import AsyncGenerator

import aiofiles

from app.schemas import AgentError, GameContext, SSEEvent
from app.workflows import form_workflow, matchup_workflow, odds_risk_workflow
from app.agents import final_prediction

logger = logging.getLogger(__name__)

MOCK_DATA_DIR = Path(__file__).parent / "mock_data"


def _parse_game_id(game_id: str) -> tuple[str, str]:
    """'LAL_GSW' or 'LAL_GSW_22_5_26' → ('LAL', 'GSW')"""
    parts = game_id.split("_")
    if len(parts) < 2:
        raise ValueError(f"Invalid game_id format '{game_id}': expected 'HOME_AWAY[_...]'")
    return parts[0], parts[1]


def _find_mock_file(directory: Path, name: str) -> Path:
    path = directory / name
    if not path.exists():
        raise FileNotFoundError(f"Missing mock data file: {directory.name}/{name}")
    return path


async def _read_file(path: Path) -> str:
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        return await f.read()


async def _load_context(game_id: str) -> tuple[GameContext, dict[str, str]]:
    home_id, away_id = _parse_game_id(game_id)

    raw = await _read_file(MOCK_DATA_DIR / "games.json")
    games = json.loads(raw)

    fixture = next(
        (g for g in games
         if g["Home team"]["id"] == home_id and g["Away team"]["id"] == away_id),
        None,
    )
    if fixture is None:
        raise ValueError(f"No fixture found for {home_id} vs {away_id}")

    ctx = GameContext(
        game_id=game_id,
        home_team_id=home_id,
        away_team_id=away_id,
        game_date=fixture["Time"][:10],
        venue=f"{fixture['Home team']['name']} Home Court",
    )

    file_map: dict[str, Path] = {
        "home_form": _find_mock_file(MOCK_DATA_DIR / "form",          f"{home_id}.txt"),
        "away_form": _find_mock_file(MOCK_DATA_DIR / "form",          f"{away_id}.txt"),
        "matchup":   _find_mock_file(MOCK_DATA_DIR / "matchups",      f"{home_id}_{away_id}.txt"),
        "odds_risk": _find_mock_file(MOCK_DATA_DIR / "odds_and_risk", f"{home_id}_{away_id}.txt"),
    }

    keys = list(file_map.keys())
    contents = await asyncio.gather(*[_read_file(p) for p in file_map.values()])
    texts = dict(zip(keys, contents))
    return ctx, texts


async def run_pipeline(game_id: str) -> AsyncGenerator[SSEEvent, None]:
    yield SSEEvent(event_name="status", payload={"message": "Loading game context..."})

    try:
        ctx, texts = await _load_context(game_id)
    except Exception as e:
        yield SSEEvent(event_name="error", payload={"message": str(e)})
        return

    yield SSEEvent(event_name="context_loaded", payload=ctx.model_dump())
    yield SSEEvent(event_name="status", payload={"message": "Dispatching parallel agents..."})

    raw_results = await asyncio.gather(
        form_workflow.run(ctx, texts["home_form"], ctx.home_team_id),
        form_workflow.run(ctx, texts["away_form"], ctx.away_team_id),
        matchup_workflow.run(ctx, texts["matchup"]),
        odds_risk_workflow.run(ctx, texts["odds_risk"]),
        return_exceptions=True,
    )

    labels = ["form_workflow_home", "form_workflow_away", "matchup_workflow", "odds_risk_workflow"]
    home_form = away_form = matchup = odds_risk = None
    partial_telemetry = False

    for label, result in zip(labels, raw_results):
        if isinstance(result, Exception):
            partial_telemetry = True
            err = AgentError(
                agent_name=label,
                error_type=type(result).__name__,
                error_message=str(result),
            )
            yield SSEEvent(event_name="agent_error", payload=err.model_dump(mode="json"))
            logger.warning("Agent %s failed: %s", label, result)
        else:
            yield SSEEvent(
                event_name="agent_update",
                payload={"agent": label, "data": result.model_dump()},
            )
            if label == "form_workflow_home":
                home_form = result
            elif label == "form_workflow_away":
                away_form = result
            elif label == "matchup_workflow":
                # print("Matchup JSON Output:")
                # print(json.dumps(result.model_dump(), indent=2))
                matchup = result
            elif label == "odds_risk_workflow":
                odds_risk = result

    if partial_telemetry:
        yield SSEEvent(
            event_name="status",
            payload={"message": "Partial telemetry — some agents failed. Proceeding with available data."},
        )

    yield SSEEvent(event_name="status", payload={"message": "Running final prediction agent..."})

    try:
        use_extended_thinking = partial_telemetry or (
            home_form is None or away_form is None or matchup is None or odds_risk is None
        )
        prediction = await final_prediction.run(
            ctx=ctx,
            home_form=home_form,
            away_form=away_form,
            matchup=matchup,
            odds_risk=odds_risk,
            partial_telemetry=partial_telemetry,
            extended_thinking=use_extended_thinking,
        )
        yield SSEEvent(event_name="final_prediction", payload=prediction.model_dump())
    except Exception as e:
        logger.exception("final_prediction agent failed")
        yield SSEEvent(
            event_name="agent_error",
            payload=AgentError(
                agent_name="final_prediction",
                error_type=type(e).__name__,
                error_message=str(e),
            ).model_dump(mode="json"),
        )

    yield SSEEvent(event_name="done", payload={})
