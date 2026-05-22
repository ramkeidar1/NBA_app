import json
import logging
from pathlib import Path

import aiofiles
from fastapi import APIRouter, HTTPException, status

from app.schemas import MatchFixture

logger = logging.getLogger(__name__)
MOCK_DATA_DIR = Path(__file__).parent.parent / "mock_data"

router = APIRouter()


async def _read_json_file(filename: str) -> list:
    file_path = MOCK_DATA_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data file '{filename}' could not be located.",
        )
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            raw = await f.read()
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data file '{filename}' contains malformed JSON.",
        ) from exc


@router.get("/api/matches", response_model=list[MatchFixture], response_model_by_alias=True)
async def get_matches() -> list[MatchFixture]:
    data = await _read_json_file("games.json")
    return [MatchFixture.model_validate(item) for item in data]
