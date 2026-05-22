import copy
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
import aiofiles
import anthropic

from app.schemas import FormEvalJSON, GameContext

load_dotenv()

logger = logging.getLogger(__name__)

_client = anthropic.AsyncAnthropic()


_TEAMS_FILE = Path(__file__).parent.parent / "mock_data" / "teams.json"

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


def _parse_record(record: str) -> tuple[int, int]:
    """'4-6' → (4, 6)"""
    parts = record.split("-")
    return int(parts[0]), int(parts[1])


async def _patch_teams_json(result: FormEvalJSON) -> None:
    print(result)
    async with aiofiles.open(_TEAMS_FILE, "r", encoding="utf-8") as f:
        teams: list[dict] = json.loads(await f.read())

    for team in teams:
        if team["id"] == result.team_id:
            wins, losses = _parse_record(result.record)
            team["standing"]["wins"] = wins
            team["standing"]["losses"] = losses
            team["offensiveRating"] = result.last_10_offensive_rating
            team["defensiveRating"] = result.last_10_defensive_rating
            team["differentialRating"] = result.last_10_rating_differential
            break
    else:
        logger.warning("form_workflow: team_id %s not found in teams.json", result.team_id)
        return

    async with aiofiles.open(_TEAMS_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(teams, indent=2, ensure_ascii=False))


async def run(ctx: GameContext, raw_text: str, team_id: str) -> FormEvalJSON:
    response = await _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        tools=[_TOOL_DEF],
        tool_choice={"type": "tool", "name": "submit_form_eval"},
        messages=[{"role": "user", "content": raw_text}],
    )

    tool_input: dict = response.content[0].input
    tool_input["game_id"] = ctx.game_id
    tool_input["team_id"] = team_id
    result = FormEvalJSON.model_validate(tool_input)

    await _patch_teams_json(result)
    return result
