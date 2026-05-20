# app/schemas.py
from pydantic import BaseModel, Field, ConfigDict


class TeamData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    record: str
    odds: str


class MatchFixture(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    time: str = Field(..., alias="Time")
    home_team: TeamData = Field(..., alias="Home team")
    away_team: TeamData = Field(..., alias="Away team")


class StandingSchema(BaseModel):
    wins: int
    losses: int
    seed: int


class NBATeamSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    conference: str
    division: str
    # JSON source uses camelCase; alias maps inbound key to snake_case attribute
    home_court_name: str = Field(..., alias="homeCourtName")
    standing: StandingSchema
    offensive_rating: float = Field(..., alias="offensiveRating")
    defensive_rating: float = Field(..., alias="defensiveRating")
    star_player: str = Field(..., alias="starPlayer")
