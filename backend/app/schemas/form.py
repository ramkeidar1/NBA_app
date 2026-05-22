from typing import Literal
from pydantic import BaseModel, ConfigDict
from .matchup import H2HGame

common_config = ConfigDict(populate_by_name=True)


class PlayerStatus(BaseModel):
    model_config = common_config

    player_name: str
    team_id: str
    status: Literal["OUT", "QUESTIONABLE", "AVAILABLE"]
    notes: str = ""


class FormEvalJSON(BaseModel):
    model_config = common_config

    game_id: str
    team_id: str
    team_name: str
    last_10_wins: int
    last_10_losses: int
    last_10_record: str
    home_wins: int
    home_losses: int
    home_record: str
    away_wins: int
    away_losses: int
    away_record: str
    record: str
    last_10_offensive_rating: float
    last_10_defensive_rating: float
    last_10_rating_differential: float
    recent_game: H2HGame
