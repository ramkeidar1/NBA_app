from pydantic import BaseModel, ConfigDict, Field

common_config = ConfigDict(populate_by_name=True)


class H2HGame(BaseModel):
    model_config = common_config

    date: str = Field(
        description="The historical date when the match occurred, formatted as YYYY-MM-DD.")
    home_team_id: str = Field(
        description="The unique identifier or abbreviation of the home team for this historical game.")
    away_team_id: str = Field(
        description="The unique identifier or abbreviation of the away team for this historical game.")
    home_score: int = Field(
        description="The total final score compiled by the home team.")
    away_score: int = Field(
        description="The total final score compiled by the away team.")
    winner_team_id: str = Field(
        description="The unique identifier or abbreviation of the team that won the match.")


class MatchupEvalJSON(BaseModel):
    model_config = common_config

    game_id: str = Field(
        description="The unique identifier tracking the upcoming scheduled match or fixture.")
    h2h_last_10: list[H2HGame] = Field(
        description="A chronologically ordered list of the last 10 head-to-head meetings between these two franchises, sorted from most recent to oldest.")
    last_h2h: H2HGame = Field(
        description="The single most recent head-to-head match played between these two teams.")