import asyncio
import hashlib
import json
import logging
from pathlib import Path

import aiofiles
from fastapi import APIRouter, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from app.cache.db import fetch_form, fetch_matchup, fetch_recommendation
from app.orchestrator import run_pipeline
from app.schemas import FinalPredictionJSON, GameAnalysisSchema, CommandRequest

logger = logging.getLogger(__name__)
MOCK_DATA_DIR = Path(__file__).parent.parent / "mock_data"

router = APIRouter()


async def _get_latest_agent_analysis() -> tuple[list, str]:
    file_path = MOCK_DATA_DIR / "agent_analysis.json"
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent analysis data source unavailable.",
        )
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            raw_content = await f.read()
        data_version = hashlib.md5(raw_content.encode("utf-8")).hexdigest()
        return json.loads(raw_content), data_version
    except (json.JSONDecodeError, IOError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reading agent analysis data.",
        ) from exc


@router.get("/api/agent_analysis/stream")
async def stream_agent_analysis():
    async def event_generator():
        last_sent_version = None
        while True:
            try:
                data, current_version = await _get_latest_agent_analysis()
                if current_version == last_sent_version:
                    await asyncio.sleep(2)
                    continue
                analyses = [
                    GameAnalysisSchema.model_validate(item).model_dump(by_alias=True)
                    for item in data
                ]
                last_sent_version = current_version
                yield {"event": "message", "data": json.dumps(analyses)}
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                logger.info("Client disconnected from agent analysis stream.")
                break
            except Exception as e:
                logger.error("Error streaming agent analysis: %s", e)
                yield {"event": "error", "data": "Internal streaming error"}
                await asyncio.sleep(10)

    return EventSourceResponse(event_generator())

@router.get("/api/analysis/stream/{game_id}")
async def stream_analysis(game_id: str, mode: str = "hard"):
    async def event_generator():
        try:
            async for event in run_pipeline(game_id, mode=mode):
                yield {
                    "event": event.event_name,
                    "data": json.dumps(event.payload, default=str),
                }
        except asyncio.CancelledError:
            logger.info("Client disconnected from analysis stream for game %s", game_id)

    return EventSourceResponse(event_generator())


@router.get("/api/analysis/{game_id}")
async def get_cached_analysis(game_id: str):
    parts = game_id.split("_")
    home_id, away_id = parts[0], parts[1]
    home_form, away_form, matchup = await asyncio.gather(
        fetch_form(game_id, home_id),
        fetch_form(game_id, away_id),
        fetch_matchup(game_id),
    )
    if home_form is None and away_form is None and matchup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cached analysis for game '{game_id}'.")
    return {
        "game_id": game_id,
        "home_form": home_form.model_dump() if home_form else None,
        "away_form": away_form.model_dump() if away_form else None,
        "matchup": matchup.model_dump() if matchup else None,
    }


@router.get("/api/predictions/{game_id}", response_model=FinalPredictionJSON)
async def get_cached_prediction(game_id: str) -> FinalPredictionJSON:
    prediction = await fetch_recommendation(game_id)
    if prediction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cached prediction for game '{game_id}'.")
    return prediction


@router.post("/command")
async def receive_ui_command(payload: CommandRequest):
    if payload.command == "GetUpdatedPredictionData":
        mode = payload.mode if payload.mode in ("hard", "soft") else "hard"
        stream_url = f"/api/analysis/stream/{payload.game_id}?mode={mode}"
        return {
            "status": "success",
            "message": f"Pipeline ready for game {payload.game_id} in {mode} mode.",
            "stream_url": stream_url,
            "mode": mode,
        }

    return {
        "status": "ignored",
        "message": f"Command '{payload.command}' not recognized.",
    }
