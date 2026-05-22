import asyncio
import hashlib
import json
import logging
from pathlib import Path

import aiofiles
from fastapi import APIRouter, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from app.orchestrator import run_pipeline
from app.schemas import GameAnalysisSchema, CommandRequest

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
            except Exception:
                logger.exception("Error streaming agent analysis")
                yield {"event": "error", "data": "Internal streaming error"}
                await asyncio.sleep(10)

    return EventSourceResponse(event_generator())

@router.get("/api/analysis/stream/{game_id}")
async def stream_analysis(game_id: str):
    async def event_generator():
        try:
            async for event in run_pipeline(game_id):
                yield {
                    "event": event.event_name,
                    "data": json.dumps(event.payload, default=str),
                }
        except asyncio.CancelledError:
            logger.info("Client disconnected from analysis stream for game %s", game_id)

    return EventSourceResponse(event_generator())


@router.post("/command")
async def receive_ui_command(payload: CommandRequest):
    if payload.command == "GetFullPredictionData":
        stream_url = f"/api/analysis/stream/{payload.game_id}"
        return {
            "status": "success",
            "message": f"Pipeline ready for game {payload.game_id}.",
            "stream_url": stream_url,
        }

    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"status": "error", "message": f"Command '{payload.command}' not recognized."},
    )
