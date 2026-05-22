import copy
import logging
from anthropic.types import ToolUseBlock

from app.client import anthropic_client
from app.schemas import FormEvalJSON, GameContext, H2HGame

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a precise NBA data extraction agent. "
    "Extract the team's form and performance statistics from the provided raw data text. "
    "Return only values explicitly present in the text. "
    "For the recent_game field, use the values from the MOST RECENT H2H GAME DETAIL section."
)

# Build the tool schema once at import time, removing fields we inject manually.
_BASE_SCHEMA = copy.deepcopy(FormEvalJSON.model_json_schema())
for _field in ("game_id", "team_id"):
    _BASE_SCHEMA.get("properties", {}).pop(_field, None)
    if _field in _BASE_SCHEMA.get("required", []):
        _BASE_SCHEMA["required"].remove(_field)

_TOOL_DEF = {
    "name": "submit_form_eval",
    "description": "Extract and submit the structured team form evaluation from the raw data.",
    "input_schema": _BASE_SCHEMA,
}


_DUMMY_FORMS: dict[str, FormEvalJSON] = {
    "LAL": FormEvalJSON(
        game_id="LAL_GSW",
        team_id="LAL",
        team_name="Los Angeles Lakers",
        last_10_wins=4, last_10_losses=6, last_10_record="4-6",
        home_wins=2, home_losses=3, home_record="2-3",
        away_wins=2, away_losses=3, away_record="2-3",
        record="4-6",
        last_10_offensive_rating=110.4,
        last_10_defensive_rating=114.2,
        last_10_rating_differential=-3.8,
        recent_game=H2HGame(
            date="2026-05-12",
            home_team_id="1610612760",
            away_team_id="1610612747",
            home_score=115,
            away_score=110,
            winner_team_id="1610612760",
        ),
    ),
    "GSW": FormEvalJSON(
        game_id="LAL_GSW",
        team_id="GSW",
        team_name="Golden State Warriors",
        last_10_wins=6, last_10_losses=4, last_10_record="6-4",
        home_wins=5, home_losses=2, home_record="5-2",
        away_wins=3, away_losses=3, away_record="3-3",
        record="8-5",
        last_10_offensive_rating=118.2,
        last_10_defensive_rating=112.5,
        last_10_rating_differential=5.7,
        recent_game=H2HGame(
            date="2026-05-20",
            home_team_id="1610612744",
            away_team_id="1610612760",
            home_score=112,
            away_score=108,
            winner_team_id="1610612744",
        ),
    ),
}


async def run(ctx: GameContext, raw_text: str, team_id: str, dummy: bool = True) -> FormEvalJSON:
    if dummy:
        logger.info("DUMMY FORM_WORKFLOW_%s", team_id)
        result = _DUMMY_FORMS.get(team_id)
        if result is None:
            raise ValueError(f"No dummy data for team_id={team_id}")
        result = result.model_copy(update={"game_id": ctx.game_id})
        return result

    response = await anthropic_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        tools=[_TOOL_DEF],
        tool_choice={"type": "tool", "name": "submit_form_eval"},
        messages=[{"role": "user", "content": raw_text}],
    )

    tool_block = next((b for b in response.content if isinstance(b, ToolUseBlock)), None)
    if tool_block is None:
        raise ValueError(f"form_workflow: model did not return a tool call for team {team_id}")
    tool_input: dict[str, object] = tool_block.input
    tool_input["game_id"] = ctx.game_id
    tool_input["team_id"] = team_id
    result = FormEvalJSON.model_validate(tool_input)
    logger.info("form_workflow result: %s", result)

    return result