import logging

from fastapi import APIRouter, HTTPException, status

from app.cache.db import fetch_team, fetch_teams
from app.cache.memory import TTLCache
from app.schemas import NBATeamSchema

logger = logging.getLogger(__name__)

router = APIRouter()

_team_cache: TTLCache[NBATeamSchema] = TTLCache(ttl_seconds=3600)
_teams_list_cache: TTLCache[list[NBATeamSchema]] = TTLCache(ttl_seconds=3600)


@router.get("/api/teams", response_model=list[NBATeamSchema], response_model_by_alias=True)
async def get_teams() -> list[NBATeamSchema]:
    cached = _teams_list_cache.get("all")
    if cached is not None:
        return cached

    rows = await fetch_teams()
    teams = [NBATeamSchema.model_validate(row) for row in rows]
    _teams_list_cache.set("all", teams)
    return teams


@router.get("/api/teams/{team_id}", response_model=NBATeamSchema, response_model_by_alias=True)
async def get_team(team_id: str) -> NBATeamSchema:
    cached = _team_cache.get(team_id)
    if cached is not None:
        return cached

    row = await fetch_team(team_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{team_id}' not found.")

    team = NBATeamSchema.model_validate(row)
    _team_cache.set(team_id, team)
    return team
