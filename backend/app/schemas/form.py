from typing import Literal
from pydantic import BaseModel, ConfigDict

common_config = ConfigDict(populate_by_name=True)


class PlayerStatus(BaseModel):
    model_config = common_config

    player_name: str
    team_id: str
    status: Literal["OUT", "QUESTIONABLE", "AVAILABLE"]
    notes: str = ""


class TeamFormData(BaseModel):
    model_config = common_config

    team_id: str
    team_name: str
    last_10_wins: int
    last_10_losses: int
    home_wins: int
    home_losses: int
    away_wins: int
    away_losses: int
    key_players: list[PlayerStatus]
    recent_game_log: list[str]


class FormEvalJSON(BaseModel):
    model_config = common_config

    game_id: str
    home_team: TeamFormData
    away_team: TeamFormData
    standalone_probability: float
    analysis_notes: str = ""
