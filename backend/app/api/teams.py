import json
import logging
from pathlib import Path

import aiofiles
from fastapi import APIRouter, HTTPException, status

from app.schemas import NBATeamSchema

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


@router.get("/api/teams", response_model=list[NBATeamSchema])
async def get_teams() -> list[NBATeamSchema]:
    data = await _read_json_file("teams.json")
    return [NBATeamSchema.model_validate(item) for item in data]
