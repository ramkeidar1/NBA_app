from typing import Literal
from pydantic import BaseModel, ConfigDict

common_config = ConfigDict(populate_by_name=True)


class FinalPredictionJSON(BaseModel):
    model_config = common_config

    game_id: str
    predicted_winner: str
    confidence: float
    risk_rating: Literal["LOW", "MEDIUM", "HIGH"]
    reasoning_narrative: str
    form_weight: float
    matchup_weight: float
    odds_weight: float
    signal_disagreement_flag: bool
    partial_telemetry: bool
    extended_thinking: bool = False
