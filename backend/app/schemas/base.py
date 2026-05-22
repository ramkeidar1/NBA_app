from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

common_config = ConfigDict(populate_by_name=True)


class GameContext(BaseModel):
    model_config = common_config

    game_id: str = Field(
        description="The unique identifier tracking the scheduled match or fixture.")
    home_team_id: str = Field(
        description="The unique identifier or abbreviation of the home franchise (e.g., 'BOS', 'LAL').")
    away_team_id: str = Field(
        description="The unique identifier or abbreviation of the away franchise (e.g., 'MIA', 'GSW').")
    game_date: str = Field(
        description="The calendar date of the fixture formatted textually as YYYY-MM-DD.")
    venue: str = Field(
        description="The official name of the arena or stadium hosting the event.")


class SSEEvent(BaseModel):
    model_config = common_config

    event_name: str = Field(
        description="The functional string identifier classifying the Server-Sent Event type (e.g., 'workflow_completed', 'telemetry_update').")
    payload: dict[str, Any] = Field(
        description="A dynamic, unstructured dictionary carrying the event's raw data properties and contextual parameters.")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The UTC timestamp recording when the event was dispatched, formatted in ISO 8601 syntax.")


class AgentError(BaseModel):
    model_config = common_config

    agent_name: str = Field(
        description="The identifier of the localized node or sub-agent routine throwing the exception (e.g., 'OddsRiskAgent').")
    error_type: str = Field(
        description="The operational class or code of the exception being raised (e.g., 'TimeoutError', 'ValidationError').")
    error_message: str = Field(
        description="A detailed human-readable narrative explaining why the execution thread failed.")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The UTC timestamp tracking exactly when the execution anomaly occurred, formatted in ISO 8601 syntax.")