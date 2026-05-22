import asyncio
import hashlib
import json
import logging
from pathlib import Path

import aiofiles
from fastapi import APIRouter, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from app.schemas import MatchPredictionSchema

logger = logging.getLogger(__name__)
MOCK_DATA_DIR = Path(__file__).parent.parent / "mock_data"

router = APIRouter()


async def _get_latest_predictions_data() -> tuple[list, str]:
    file_path = MOCK_DATA_DIR / "predictions.json"
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Predictions data source unavailable.",
        )
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            raw_content = await f.read()
        data_version = hashlib.md5(raw_content.encode("utf-8")).hexdigest()
        return json.loads(raw_content), data_version
    except (json.JSONDecodeError, IOError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reading predictions data.",
        ) from exc


@router.get("/api/predictions/stream")
async def stream_predictions():
    async def event_generator():
        last_sent_version = None
        while True:
            try:
                data, current_version = await _get_latest_predictions_data()
                if current_version == last_sent_version:
                    await asyncio.sleep(2)
                    continue
                predictions = [
                    MatchPredictionSchema.model_validate(item).model_dump(by_alias=True)
                    for item in data
                ]
                last_sent_version = current_version
                yield {"event": "message", "data": json.dumps(predictions)}
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                logger.info("Client disconnected from predictions stream.")
                break
            except Exception:
                logger.exception("Error streaming predictions")
                yield {"event": "error", "data": "Internal streaming error"}
                await asyncio.sleep(10)

    return EventSourceResponse(event_generator())
