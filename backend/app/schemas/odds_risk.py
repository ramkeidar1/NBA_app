from typing import Literal
from pydantic import BaseModel, ConfigDict

common_config = ConfigDict(populate_by_name=True)


class InjuryEntry(BaseModel):
    model_config = common_config

    player_name: str
    team_id: str
    status: Literal["OUT", "QUESTIONABLE", "AVAILABLE"]
    impact_note: str = ""


class OddsRiskEvalJSON(BaseModel):
    model_config = common_config

    game_id: str
    injury_report: list[InjuryEntry]
    moneyline_home: float
    moneyline_away: float
    spread: float
    over_under: float
    market_implied_probability_home: float
