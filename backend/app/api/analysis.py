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
from app.schemas import FinalPredictionJSON, GameAnalysisSchema, CommandRequest, MatchupEvalJSON

logger = logging.getLogger(__name__)
MOCK_DATA_DIR = Path(__file__).parent.parent / "mock_data"

router = APIRouter()


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


@router.get("/api/matchup/{game_id}", response_model=MatchupEvalJSON)
async def get_cached_matchup(game_id: str) -> MatchupEvalJSON:
    matchup = await fetch_matchup(game_id)
    if matchup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cached matchup for game '{game_id}'.")
    return matchup


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
