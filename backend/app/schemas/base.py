from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

common_config = ConfigDict(populate_by_name=True)


class GameContext(BaseModel):
    model_config = common_config

    game_id: str
    home_team_id: str
    away_team_id: str
    game_date: str
    venue: str


class SSEEvent(BaseModel):
    model_config = common_config

    event_name: str
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentError(BaseModel):
    model_config = common_config

    agent_name: str
    error_type: str
    error_message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
