from pydantic import BaseModel, ConfigDict

common_config = ConfigDict(populate_by_name=True)


class H2HGame(BaseModel):
    model_config = common_config

    date: str
    home_team_id: str
    away_team_id: str
    home_score: int
    away_score: int
    winner_team_id: str


class MatchupEvalJSON(BaseModel):
    model_config = common_config

    game_id: str
    h2h_last_10: list[H2HGame]
    home_team_h2h_wins: int
    home_team_h2h_losses: int
    venue_advantage_note: str = ""
    standalone_probability: float
    analysis_notes: str = ""
