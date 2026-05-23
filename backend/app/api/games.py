import json
import logging
from pathlib import Path

import aiofiles
from fastapi import APIRouter, HTTPException, status

from app.cache.db import fetch_match
from app.cache.memory import TTLCache
from app.schemas import MatchFixture

logger = logging.getLogger(__name__)
MOCK_DATA_DIR = Path(__file__).parent.parent / "mock_data"

router = APIRouter()

_match_cache: TTLCache[MatchFixture] = TTLCache(ttl_seconds=300)


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


@router.get("/api/matches/{team_id}", response_model=MatchFixture, response_model_by_alias=True)
async def get_match(team_id: str) -> MatchFixture:
    logger.info("Recieved GET request for {team_id}")
    cached = _match_cache.get(team_id)
    if cached is not None:
        return cached

    row = await fetch_match(team_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No fixture found for game_id '{game_id}'.")

    fixture = MatchFixture.model_validate(row)
    _match_cache.set(team_id, fixture)
    return fixture
