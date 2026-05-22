from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from .matchup import H2HGame

common_config = ConfigDict(populate_by_name=True)


class PlayerStatus(BaseModel):
    model_config = common_config

    player_name: str = Field(
        description="The full legal name of the player.")
    team_id: str = Field(
        description="The unique identifier or abbreviation of the player's franchise.")
    status: Literal["OUT", "QUESTIONABLE", "AVAILABLE"] = Field(
        description="The active status designation evaluating the player's availability for upcoming rotations.")
    notes: str = Field(
        default="",
        description="Additional technical notes regarding the player's performance limitations or status updates.")


class FormEvalJSON(BaseModel):
    model_config = common_config

    game_id: str = Field(
        description="The unique identifier tracking the upcoming scheduled match or fixture.")
    team_id: str = Field(
        description="The unique identifier or abbreviation of the specific franchise being evaluated.")
    team_name: str = Field(
        description="The full official name of the franchise (e.g., 'Boston Celtics').")
    last_10_wins: int = Field(
        description="The total number of victories achieved by this team over their last 10 regular season matches.")
    last_10_losses: int = Field(
        description="The total number of defeats sustained by this team over their last 10 regular season matches.")
    last_10_record: str = Field(
        description="The aggregated win-loss record over the trailing 10 games, formatted textually as 'W-L' (e.g., '7-3').")
    home_wins: int = Field(
        description="The total cumulative home wins accrued by this franchise across the current regular season.")
    home_losses: int = Field(
        description="The total cumulative home losses sustained by this franchise across the current regular season.")
    home_record: str = Field(
        description="The total cumulative regular season home record, formatted textually as 'W-L' (e.g., '22-8').")
    away_wins: int = Field(
        description="The total cumulative away wins accrued by this franchise across the current regular season.")
    away_losses: int = Field(
        description="The total cumulative away losses sustained by this franchise across the current regular season.")
    away_record: str = Field(
        description="The total cumulative regular season away record, formatted textually as 'W-L' (e.g., '14-16').")
    record: str = Field(
        description="The consolidated overall regular season win-loss record, formatted textually as 'W-L' (e.g., '36-24').")
    last_10_offensive_rating: float = Field(
        description="The calculated offensive efficiency rating (points produced per 100 possessions) tracking across the trailing 10 games.")
    last_10_defensive_rating: float = Field(
        description="The calculated defensive efficiency rating (points allowed per 100 possessions) tracking across the trailing 10 games.")
    last_10_rating_differential: float = Field(
        description="The net efficiency differential over the trailing 10 games, calculated as (Offensive Rating minus Defensive Rating).")
    recent_game: H2HGame = Field(
        description="A nested schema block representing the absolute most recent game played by this franchise against any opponent.")