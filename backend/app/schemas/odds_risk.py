from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

common_config = ConfigDict(populate_by_name=True)


class InjuryEntry(BaseModel):
    model_config = common_config

    player_name: str = Field(
        description="The full legal name of the player listed on the injury report.")
    team_id: str = Field(
        description="The unique identifier or abbreviation of the player's team (e.g., 'BOS', 'LAL').")
    status: Literal["OUT", "QUESTIONABLE", "AVAILABLE"] = Field(
        description="The official game-day availability status designated by the team's medical staff.")
    impact_note: str = Field(
        default="",
        description="A brief analytical note detailing how this player's absence or limitation affects team rotation, depth, or specific matchup metrics.")


class OddsRiskEvalJSON(BaseModel):
    model_config = common_config

    game_id: str = Field(
        description="The unique identifier tracking the scheduled match or fixture.")
    injury_report: list[InjuryEntry] = Field(
        description="A structured list containing all relevant player health updates and status designations for this specific game.")
    moneyline_home: float = Field(
        description="The standard decimal odds line for the home team to win outright.")
    moneyline_away: float = Field(
        description="The standard decimal odds line for the away team to win outright.")
    spread: float = Field(
        description="The opening or current consensus point spread for the match, relative to the home team (e.g., -4.5 implies the home team is favored by 4.5 points).")
    over_under: float = Field(
        description="The total consensus line for the combined points scored by both teams.")
    market_implied_probability_home: float = Field(
        description="The calculated win probability for the home team extracted from market odds, expressed as a decimal between 0.0 and 1.0 (with vigorish/juice removed if applicable).")