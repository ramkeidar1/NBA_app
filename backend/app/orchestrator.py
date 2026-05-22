import asyncio
import importlib
import json
import logging
from pathlib import Path
from typing import AsyncGenerator

import aiofiles

from app.schemas import AgentError, GameContext, SSEEvent

logger = logging.getLogger(__name__)

MOCK_DATA_DIR = Path(__file__).parent / "mock_data"


def _parse_game_id(game_id: str) -> tuple[str, str, str]:
    """'LAL_GSW_22_5_26' → ('LAL', 'GSW', '22_5_26')"""
    parts = game_id.split("_")
    return parts[0], parts[1], "_".join(parts[2:])


async def _read_file(path: Path) -> str:
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        return await f.read()


async def _load_context(game_id: str) -> tuple[GameContext, dict[str, str]]:
    home_id, away_id, date_suffix = _parse_game_id(game_id)

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
        "home_form": MOCK_DATA_DIR / "form" / f"{home_id}_{date_suffix}.txt",
        "away_form": MOCK_DATA_DIR / "form" / f"{away_id}_{date_suffix}.txt",
        "matchup":   MOCK_DATA_DIR / "matchups" / f"{home_id}_{away_id}_{date_suffix}.txt",
        "odds_risk": MOCK_DATA_DIR / "odds_and_risk" / f"{home_id}_{away_id}_{date_suffix}.txt",
    }

    for key, path in file_map.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing mock data file: {path.name}")

    texts = {key: await _read_file(path) for key, path in file_map.items()}
    return ctx, texts


def _get_workflow_fn(module_path: str, fn_name: str = "run"):
    """Import a workflow run function; returns None if not yet implemented."""
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, fn_name, None)
    except ImportError:
        return None


async def _not_impl(agent_name: str):
    raise NotImplementedError(f"{agent_name} is not yet implemented")


async def run_pipeline(game_id: str) -> AsyncGenerator[SSEEvent, None]:
    yield SSEEvent(event_name="status", payload={"message": "Loading game context..."})

    try:
        ctx, texts = await _load_context(game_id)
    except Exception as e:
        yield SSEEvent(event_name="error", payload={"message": str(e)})
        return

    yield SSEEvent(event_name="context_loaded", payload=ctx.model_dump())
    yield SSEEvent(event_name="status", payload={"message": "Dispatching parallel agents..."})

    form_run = _get_workflow_fn("app.workflows.form_workflow")
    matchup_run = _get_workflow_fn("app.workflows.matchup_workflow")
    odds_run = _get_workflow_fn("app.workflows.odds_risk_workflow")

    home_form_coro = (
        form_run(ctx, texts["home_form"], ctx.home_team_id)
        if form_run else _not_impl("form_workflow_home")
    )
    away_form_coro = (
        form_run(ctx, texts["away_form"], ctx.away_team_id)
        if form_run else _not_impl("form_workflow_away")
    )
    matchup_coro = (
        matchup_run(ctx, texts["matchup"])
        if matchup_run else _not_impl("matchup_workflow")
    )
    odds_coro = (
        odds_run(ctx, texts["odds_risk"])
        if odds_run else _not_impl("odds_risk_workflow")
    )

    raw_results = await asyncio.gather(
        home_form_coro,
        away_form_coro,
        matchup_coro,
        odds_coro,
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
                matchup = result
            elif label == "odds_risk_workflow":
                odds_risk = result

    if partial_telemetry:
        yield SSEEvent(
            event_name="status",
            payload={"message": "Partial telemetry — some agents failed. Proceeding with available data."},
        )

    yield SSEEvent(event_name="status", payload={"message": "Running final prediction agent..."})

    prediction_run = _get_workflow_fn("app.agents.final_prediction")
    if prediction_run is None:
        yield SSEEvent(
            event_name="agent_error",
            payload=AgentError(
                agent_name="final_prediction",
                error_type="NotImplementedError",
                error_message="final_prediction agent is not yet implemented.",
            ).model_dump(mode="json"),
        )
    else:
        try:
            prediction = await prediction_run(
                ctx=ctx,
                home_form=home_form,
                away_form=away_form,
                matchup=matchup,
                odds_risk=odds_risk,
                partial_telemetry=partial_telemetry,
            )
            yield SSEEvent(event_name="final_prediction", payload=prediction.model_dump())
        except Exception as e:
            logger.error("final_prediction agent failed: %s", e)
            yield SSEEvent(
                event_name="agent_error",
                payload=AgentError(
                    agent_name="final_prediction",
                    error_type=type(e).__name__,
                    error_message=str(e),
                ).model_dump(mode="json"),
            )

    yield SSEEvent(event_name="done", payload={})
