from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

common_config = ConfigDict(populate_by_name=True)

class FormWorkflowJSON(BaseModel):
    model_config = common_config
    
    confidence: float = Field(description="Confidence score for form analysis, between 0.0 and 1.0.")
    workflow_weight: float = Field(description="The structural weight given to recent form in the final model.")
    winner_form: str = Field(description="Summary narrative of the predicted winner's recent trend and momentum.")
    loser_form: str = Field(description="Summary narrative of the predicted loser's recent trend and momentum.")
    key_context: str = Field(description="Critical contextual factors regarding team form (e.g., back-to-back games, rest days).")
    
class MatchupWorkflowJSON(BaseModel):
    model_config = common_config
    
    confidence: float = Field(description="Confidence score for head-to-head history analysis, between 0.0 and 1.0.")
    workflow_weight: float = Field(description="The structural weight given to historical matchups in the final model.")
    last_match: str = Field(description="Brief breakdown of the single most recent head-to-head matchup.")
    last_ten_matches: str = Field(description="Statistical or narrative trend across the last 10 head-to-head meetings.")
    net_differential: str = Field(description="The calculated point or efficiency differential trend between these teams.")
    
class OddsRiskWorkflowJSON(BaseModel):
    model_config = common_config
    
    confidence: float = Field(description="Confidence score based on market odds and risk boundaries, between 0.0 and 1.0.")
    workflow_weight: float = Field(description="The structural weight given to market conditions and risk vectors.")
    key_context: list[str] = Field(description="List of specific risk factors identified in the odds market (e.g., line movement anomalies).")

class FinalPredictionJSON(BaseModel):
    model_config = common_config

    game_id: str = Field(description="The unique identifier for the scheduled fixture.")
    predicted_winner_id: str = Field(description="The id of the team projected to win.")
    predicted_winner_name: str = Field(description="The name of the team projected to win.")
    confidence: float = Field(description="Overall consolidated model confidence score, between 0.0 and 1.0.")
    risk_rating: Literal["LOW", "MEDIUM", "HIGH"] = Field(description="The evaluated volatility and risk profile of making this assertion.")
    reasoning_narrative: str = Field(description="High-level executive summary combining all workflow outputs into a cohesive decision defense.")
    form_report: FormWorkflowJSON
    matchup_report: MatchupWorkflowJSON
    odds_risk_report: OddsRiskWorkflowJSON
    signal_disagreement_flag: bool = Field(description="Set to true if individual sub-workflows yielded conflicting directional indicators.")
    partial_telemetry: bool = Field(description="Indicates if the analysis was forced to run on incomplete or delayed telemetry data stream arrays.")
    extended_thinking: bool = Field(default=False, description="Internal configuration flag tracking if multi-stage verification routing was used.")