from .base import AgentError, GameContext, SSEEvent
from .form import FormEvalJSON, PlayerStatus
from .matchup import H2HGame, MatchupEvalJSON
from .odds_risk import InjuryEntry, OddsRiskEvalJSON
from .prediction import FinalPredictionJSON

# Legacy models — defined inline to preserve backward compat with existing API routes
from pydantic import BaseModel, Field, ConfigDict
from typing import List

common_config = ConfigDict(populate_by_name=True)


class TeamData(BaseModel):
    model_config = common_config

    id: str
    name: str
    record: str
    odds: str


class MatchFixture(BaseModel):
    model_config = common_config

    time: str = Field(..., alias="Time")
    home_team: TeamData = Field(..., alias="Home team")
    away_team: TeamData = Field(..., alias="Away team")


class StandingSchema(BaseModel):
    wins: int
    losses: int
    seed: int


class NBATeamSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    conference: str
    division: str
    home_court_name: str = Field(..., alias="homeCourtName")
    standing: StandingSchema
    offensive_rating: float = Field(..., alias="offensiveRating")
    defensive_rating: float = Field(..., alias="defensiveRating")
    rating_differential: float = Field(..., alias="differentialRating")
    star_player: str = Field(..., alias="starPlayer")


class MatchPredictionSchema(BaseModel):
    model_config = common_config

    name: str
    winner_team: str = Field(..., alias="winnerTeam")
    difference: int
    confidence: float
    expected_value: float = Field(..., alias="expectedValue")
    risk_level: str = Field(..., alias="riskLevel")
    ai_summary: str = Field(..., alias="aiSummary")


class FormAgentSchema(BaseModel):
    model_config = common_config

    expected_winner_form: str = Field(..., alias="Expected winner Form")
    expected_loser_form: str = Field(..., alias="Expected losser Form")
    addons: str = Field(..., alias="Addons")
    certainty: int = Field(..., alias="Certainty", ge=0, le=100)


class MatchupAgentSchema(BaseModel):
    model_config = common_config

    expected_winner_form: str = Field(..., alias="Expected winner Form")
    expected_loser_form: str = Field(..., alias="Expected losser Form")
    differential_net: str = Field(..., alias="Deferntial net")
    interesting_matchups: str = Field(..., alias="Intersting Matchups")
    certainty: int = Field(..., alias="Certainty", ge=0, le=100)


class RiskAgentSchema(BaseModel):
    model_config = common_config

    addons: List[str] = Field(..., alias="Addons")
    certainty: int = Field(..., alias="Certainty", ge=0, le=100)


class GameAnalysisSchema(BaseModel):
    model_config = common_config

    name: str
    form_agent: FormAgentSchema = Field(..., alias="Form Agent")
    matchup_agent: MatchupAgentSchema = Field(..., alias="Matchup Agent")
    risk_agent: RiskAgentSchema = Field(..., alias="Risk Agent")
    
class CommandRequest(BaseModel):
    game_id: str = Field(..., description="The ID of the match to target")
    command: str = Field(..., description="The directive to execute, e.g., 'REFRESH'")


__all__ = [
    # Inter-agent contracts
    "GameContext",
    "SSEEvent",
    "AgentError",
    "PlayerStatus",
    "FormEvalJSON",
    "H2HGame",
    "MatchupEvalJSON",
    "InjuryEntry",
    "OddsRiskEvalJSON",
    "FinalPredictionJSON",
    # Legacy
    "TeamData",
    "MatchFixture",
    "StandingSchema",
    "NBATeamSchema",
    "MatchPredictionSchema",
    "FormAgentSchema",
    "MatchupAgentSchema",
    "RiskAgentSchema",
    "GameAnalysisSchema",
]
