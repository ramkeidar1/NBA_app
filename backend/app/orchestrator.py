import asyncio
import importlib
import json
import logging
from pathlib import Path
from typing import AsyncGenerator, Literal

import aiofiles

from app.cache.db import (
    fetch_form,
    fetch_matchup,
    save_form,
    save_match,
    save_matchup,
    save_odds_snapshot,
    save_recommendation,
)
from app.cache.memory import form_cache, matchup_cache
from app.config import DUMMY_MODE
from app.schemas import AgentError, GameContext, SSEEvent

logger = logging.getLogger(__name__)

MOCK_DATA_DIR = Path(__file__).parent / "mock_data"


def _parse_game_id(game_id: str) -> tuple[str, str]:
    """'LAL_GSW' or 'LAL_GSW_22_5_26' → ('LAL', 'GSW')"""
    parts = game_id.split("_")
    return parts[0], parts[1]


def _find_mock_file(directory: Path, name: str) -> Path:
    path = directory / name
    if not path.exists():
        raise FileNotFoundError(f"Missing mock data file: {directory.name}/{name}")
    return path


async def _read_file(path: Path) -> str:
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        return await f.read()


async def _load_context(game_id: str) -> tuple[GameContext, dict[str, str], dict]:
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

    texts = {key: await _read_file(path) for key, path in file_map.items()}
    return ctx, texts, fixture


def _get_workflow_fn(module_path: str, fn_name: str = "run"):
    """Import a workflow run function; returns None if not yet implemented."""
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, fn_name, None)
    except ImportError:
        return None


async def _not_impl(agent_name: str):
    raise NotImplementedError(f"{agent_name} is not yet implemented")


# ── Hard pipeline ─────────────────────────────────────────────────────────────
# Runs all 4 workflows concurrently, saves everything to DB.

async def _run_hard(
    ctx: GameContext,
    texts: dict[str, str],
    fixture: dict,
    dummy: bool = DUMMY_MODE,
) -> AsyncGenerator[SSEEvent, None]:
    yield SSEEvent(event_name="status", payload={"message": "Dispatching parallel agents..."})

    form_run    = _get_workflow_fn("app.workflows.form_workflow")
    matchup_run = _get_workflow_fn("app.workflows.matchup_workflow")
    odds_run    = _get_workflow_fn("app.workflows.odds_risk_workflow")

    home_form_coro = (
        form_run(ctx, texts["home_form"], ctx.home_team_id, dummy=dummy)
        if form_run else _not_impl("form_workflow_home")
    )
    away_form_coro = (
        form_run(ctx, texts["away_form"], ctx.away_team_id, dummy=dummy)
        if form_run else _not_impl("form_workflow_away")
    )
    matchup_coro = (
        matchup_run(ctx, texts["matchup"], dummy=dummy)
        if matchup_run else _not_impl("matchup_workflow")
    )
    odds_coro = (
        odds_run(ctx, texts["odds_risk"], dummy=dummy)
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
    odds_snapshot_id: str | None = None
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
                if not dummy:
                    await save_form(result)
            elif label == "form_workflow_away":
                away_form = result
                if not dummy:
                    await save_form(result)
            elif label == "matchup_workflow":
                matchup = result
                if not dummy:
                    await save_matchup(result)
            elif label == "odds_risk_workflow":
                odds_risk = result
                if not dummy:
                    odds_snapshot_id = await save_odds_snapshot(result)

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
                dummy=dummy,
            )
            yield SSEEvent(event_name="final_prediction", payload=prediction.model_dump())
            if not dummy and odds_snapshot_id:
                await save_recommendation(prediction, odds_snapshot_id)
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


# ── Soft pipeline ─────────────────────────────────────────────────────────────
# Lookup order for stable inputs: in-memory TTLCache → DB.
# Falls back to hard pipeline if any result is missing from both.
# Only odds_risk is always run live (market data changes frequently).

async def _fetch_form_two_level(game_id: str, team_id: str):
    """TTLCache → DB for a single form entry."""
    result = form_cache.get(f"{game_id}:{team_id}")
    if result is not None:
        logger.debug("memory: form_cache hit for %s/%s", game_id, team_id)
        return result
    return await fetch_form(game_id, team_id)


async def _fetch_matchup_two_level(game_id: str):
    """TTLCache → DB for matchup."""
    result = matchup_cache.get(game_id)
    if result is not None:
        logger.debug("memory: matchup_cache hit for %s", game_id)
        return result
    return await fetch_matchup(game_id)


async def _run_soft(
    ctx: GameContext,
    texts: dict[str, str],
    fixture: dict,
    dummy: bool = DUMMY_MODE,
) -> AsyncGenerator[SSEEvent, None]:
    yield SSEEvent(event_name="status", payload={"message": "Soft pipeline — checking cache..."})

    home_form, away_form, matchup = await asyncio.gather(
        _fetch_form_two_level(ctx.game_id, ctx.home_team_id),
        _fetch_form_two_level(ctx.game_id, ctx.away_team_id),
        _fetch_matchup_two_level(ctx.game_id),
    )

    if home_form is None or away_form is None or matchup is None:
        yield SSEEvent(
            event_name="status",
            payload={"message": "Cache miss — switching to hard pipeline..."},
        )
        async for event in _run_hard(ctx, texts, fixture, dummy=dummy):
            yield event
        return

    # Emit cached results as agent_update events so the UI receives the same shape
    yield SSEEvent(event_name="agent_update", payload={"agent": "form_workflow_home", "data": home_form.model_dump()})
    yield SSEEvent(event_name="agent_update", payload={"agent": "form_workflow_away", "data": away_form.model_dump()})
    yield SSEEvent(event_name="agent_update", payload={"agent": "matchup_workflow",   "data": matchup.model_dump()})

    # Run only the odds_risk workflow to get fresh market data
    yield SSEEvent(event_name="status", payload={"message": "Fetching fresh odds and risk data..."})

    odds_run = _get_workflow_fn("app.workflows.odds_risk_workflow")
    odds_coro = (
        odds_run(ctx, texts["odds_risk"], dummy=dummy)
        if odds_run else _not_impl("odds_risk_workflow")
    )

    odds_result = await asyncio.gather(odds_coro, return_exceptions=True)
    odds_risk = odds_result[0]
    odds_snapshot_id: str | None = None
    partial_telemetry = False

    if isinstance(odds_risk, Exception):
        partial_telemetry = True
        err = AgentError(
            agent_name="odds_risk_workflow",
            error_type=type(odds_risk).__name__,
            error_message=str(odds_risk),
        )
        yield SSEEvent(event_name="agent_error", payload=err.model_dump(mode="json"))
        logger.warning("odds_risk_workflow failed in soft pipeline: %s", odds_risk)
    else:
        yield SSEEvent(event_name="agent_update", payload={"agent": "odds_risk_workflow", "data": odds_risk.model_dump()})
        if not dummy:
            odds_snapshot_id = await save_odds_snapshot(odds_risk)

    if partial_telemetry:
        yield SSEEvent(
            event_name="status",
            payload={"message": "Partial telemetry — odds agent failed. Proceeding with available data."},
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
                odds_risk=odds_risk if not isinstance(odds_risk, Exception) else None,
                partial_telemetry=partial_telemetry,
                dummy=dummy,
            )
            yield SSEEvent(event_name="final_prediction", payload=prediction.model_dump())
            if not dummy and odds_snapshot_id:
                await save_recommendation(prediction, odds_snapshot_id)
        except Exception as e:
            logger.error("final_prediction agent failed in soft pipeline: %s", e)
            yield SSEEvent(
                event_name="agent_error",
                payload=AgentError(
                    agent_name="final_prediction",
                    error_type=type(e).__name__,
                    error_message=str(e),
                ).model_dump(mode="json"),
            )


# ── Entry point ───────────────────────────────────────────────────────────────

async def run_pipeline(
    game_id: str,
    mode: Literal["hard", "soft"] = "hard",
    dummy: bool = DUMMY_MODE,
) -> AsyncGenerator[SSEEvent, None]:
    yield SSEEvent(event_name="status", payload={"message": "Loading game context..."})

    try:
        ctx, texts, fixture = await _load_context(game_id)
    except Exception as e:
        yield SSEEvent(event_name="error", payload={"message": str(e)})
        return

    if not dummy:
        await save_match(ctx, fixture)
    yield SSEEvent(event_name="context_loaded", payload=ctx.model_dump())

    pipeline = _run_hard if mode == "hard" else _run_soft
    async for event in pipeline(ctx, texts, fixture, dummy=dummy):
        yield event

    yield SSEEvent(event_name="done", payload={})
