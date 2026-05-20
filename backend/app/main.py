# app/main.py
import json
import logging
import asyncio
import hashlib  # Used for efficient change detection
from pathlib import Path

import aiofiles
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
# --- SSE Imports ---
from sse_starlette.sse import EventSourceResponse

from app.schemas import MatchFixture, NBATeamSchema, MatchPredictionSchema, GameAnalysisSchema

logger = logging.getLogger(__name__)
MOCK_DATA_DIR = Path(__file__).parent / "mock_data"

app = FastAPI(title="CourMind AI Core Gateway")

# Ensure your CORS allows the frontend origins to stream
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _read_json_file(filename: str) -> list:
    """Read a JSON file from the mock_data directory without blocking the event loop."""
    file_path = MOCK_DATA_DIR / filename
    if not file_path.exists():
        logger.error("Mock data file not found", extra={"path": str(file_path)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data file '{filename}' could not be located.",
        )
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            raw = await f.read()
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.exception("JSON decode failure", extra={"file": filename})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data file '{filename}' contains malformed JSON.",
        ) from exc


# =====================================================================
# DATA RETRIEVAL LAYER (Your future Redis bridge)
# =====================================================================

async def _get_latest_predictions_data() -> tuple[list, str]:
    """
    Reads predictions data and generates a unique fingerprint string hash.
    
    WHEN YOU SWITCH TO REDIS:
    Replace this block with a non-blocking Redis call:
        raw_content = await redis_client.get("agent:predictions:latest")
    """
    file_path = MOCK_DATA_DIR / "predictions.json"
    if not file_path.exists():
        logger.error("Predictions data file not found", extra={"path": str(file_path)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Predictions data source unavailable.",
        )
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            raw_content = await f.read()
        
        # Generate fingerprint to avoid reprocessing unchanged records
        data_version = hashlib.md5(raw_content.encode("utf-8")).hexdigest()
        data = json.loads(raw_content)
        return data, data_version
        
    except (json.JSONDecodeError, IOError) as exc:
        logger.exception("Failure within predictions pipeline retrieval")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reading core analysis data pipeline.",
        ) from exc
        
async def _get_latest_agent_analysis() -> tuple[list, str]:
    file_path = MOCK_DATA_DIR / "agent_analysis.json"
    if not file_path.exists():
        logger.error("Agent_analysis data file not found", extra={"path": str(file_path)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent_analysis data source unavailable.",
        )
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            raw_content = await f.read()
        
        # Generate fingerprint to avoid reprocessing unchanged records
        data_version = hashlib.md5(raw_content.encode("utf-8")).hexdigest()
        data = json.loads(raw_content)
        return data, data_version
        
    except (json.JSONDecodeError, IOError) as exc:
        logger.exception("Failure within agent_analysis pipeline retrieval")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reading core analysis data pipeline.",
        ) from exc


# =====================================================================
# ENDPOINTS
# =====================================================================

@app.get("/api/predictions/stream")
async def stream_predictions():
    async def event_generator():
        # Tracks data version uniquely for each isolated client connection hook
        last_sent_version = None
        
        while True:
            try:
                # 1. Pull current data and its fingerprint
                data, current_version = await _get_latest_predictions_data()
                
                # 2. Only broadcast down the pipe if a change happened
                if current_version == last_sent_version:
                    await asyncio.sleep(2)  # Check back shortly
                    continue
                
                # 3. Process new data state via Pydantic matching camelCase aliases
                predictions = [
                    MatchPredictionSchema.model_validate(item).model_dump(by_alias=True) 
                    for item in data
                ]
                
                # 4. Save state checkpoint for this iteration loop
                last_sent_version = current_version
                
                # 5. Stream it out to the client
                yield {
                    "event": "message",
                    "data": json.dumps(predictions)
                }
                
                await asyncio.sleep(2)
                
            except asyncio.CancelledError:
                logger.info("Client disconnected from predictions stream.")
                break
            except Exception as e:
                logger.error(f"Error streaming predictions: {e}")
                yield {"event": "error", "data": "Internal streaming error"}
                await asyncio.sleep(10)

    return EventSourceResponse(event_generator())

@app.get("/api/agent_analysis/stream")
async def stream_agent_analysis():
    async def event_generator():
        # Tracks data version uniquely for each isolated client connection hook
        last_sent_version = None
        
        while True:
            try:
                # 1. Pull current data and its fingerprint
                data, current_version = await _get_latest_agent_analysis()
                
                # 2. Only broadcast down the pipe if a change happened
                if current_version == last_sent_version:
                    await asyncio.sleep(2)  # Check back shortly
                    continue
                
                # 3. Process new data state via Pydantic matching camelCase aliases
                predictions = [
                    GameAnalysisSchema.model_validate(item).model_dump(by_alias=True) 
                    for item in data
                ]
                
                # 4. Save state checkpoint for this iteration loop
                last_sent_version = current_version
                
                # 5. Stream it out to the client
                yield {
                    "event": "message",
                    "data": json.dumps(predictions)
                }
                
                await asyncio.sleep(2)
                
            except asyncio.CancelledError:
                logger.info("Client disconnected from agent analysis stream.")
                break
            except Exception as e:
                logger.error(f"Error streaming agent analysis: {e}")
                yield {"event": "error", "data": "Internal streaming error"}
                await asyncio.sleep(10)

    return EventSourceResponse(event_generator())


@app.get("/api/matches", response_model=list[MatchFixture])
async def get_matches() -> list[MatchFixture]:
    data = await _read_json_file("games.json")
    return [MatchFixture.model_validate(item) for item in data]


@app.get("/api/teams", response_model=list[NBATeamSchema])
async def get_teams() -> list[NBATeamSchema]:
    data = await _read_json_file("teams.json")
    return [NBATeamSchema.model_validate(item) for item in data]