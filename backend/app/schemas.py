# app/schemas.py
from pydantic import BaseModel, Field
from typing import List

class TeamData(BaseModel):
    name: str
    record: str
    odds: str  # Kept as str because your data wraps them in quotes (e.g., "1.56")

class MatchFixture(BaseModel):
    time: str = Field(..., alias="Time")
    home_team: TeamData = Field(..., alias="Home team")
    away_team: TeamData = Field(..., alias="Away team")

    class Config:
        # This allows FastAPI to read the data using your "Home team" keys 
        # while letting you write clean Python variables like match.home_team
        populate_by_name = True