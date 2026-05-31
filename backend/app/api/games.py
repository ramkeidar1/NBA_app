import logging

from fastapi import APIRouter, HTTPException, status

from app.cache.db import fetch_match, fetch_matches
from app.cache.memory import TTLCache
from app.schemas import MatchFixture, TeamData

logger = logging.getLogger(__name__)

router = APIRouter()

_match_cache: TTLCache[MatchFixture] = TTLCache(ttl_seconds=300)


def _row_to_fixture(row: dict) -> MatchFixture:
    return MatchFixture.model_validate({
        "Time": row["game_time"],
        "Home team": {"id": row["home_team_id"], "name": row["home_team_name"]},
        "Away team": {"id": row["away_team_id"], "name": row["away_team_name"]},
    })


@router.get("/api/matches", response_model=list[MatchFixture], response_model_by_alias=True)
async def get_matches() -> list[MatchFixture]:
    rows = await fetch_matches()
    return [_row_to_fixture(row) for row in rows]


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
