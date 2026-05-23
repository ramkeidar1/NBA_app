import copy
import logging
from anthropic.types import ToolUseBlock

from app.client import anthropic_client
from app.config import DUMMY_MODE
from app.schemas import MatchupEvalJSON, GameContext
from app.workflows.dummy_data import _DUMMY_MATCHUPS

logger = logging.getLogger(__name__)

# UPDATED: Focused specifically on Head-to-Head matchup data extraction
_SYSTEM_PROMPT = (
    "You are a precise NBA matchup data extraction agent. "
    "Extract the head-to-head (H2H) history, historic scores, and recent game outcomes "
    "between the two competing teams from the provided raw text. "
    "Return only values explicitly present in the text. "
    "Ensure accuracy for dates, scores, and team identifiers."
)

# Build the tool schema once at import time, removing fields we inject manually.
_BASE_SCHEMA = copy.deepcopy(MatchupEvalJSON.model_json_schema())
for _field in ("game_id",):
    _BASE_SCHEMA.get("properties", {}).pop(_field, None)
    if _field in _BASE_SCHEMA.get("required", []):
        _BASE_SCHEMA["required"].remove(_field)

_TOOL_DEF = {
    "name": "submit_matchup_eval",
    "description": "Extract and submit the structured team's matchu[p] evaluation from the raw data.",
    "input_schema": _BASE_SCHEMA,
}


async def run(ctx: GameContext, raw_text: str, dummy: bool = DUMMY_MODE) -> MatchupEvalJSON:
    if dummy:
        logger.info("DUMMY MATCHUP_WORKFLOW_%s", ctx.game_id)
        result = next((matchup for matchup in _DUMMY_MATCHUPS if ctx.game_id in matchup.game_id), None)
        if result is None:
            # Fallback to first item if it's a generic test
            result = _DUMMY_MATCHUPS[0]
            
        result = result.model_copy(update={"game_id": ctx.game_id})
        return result

    response = await anthropic_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        tools=[_TOOL_DEF],
        # Tool choice here should match the setup tool definition name
        tool_choice={"type": "tool", "name": "submit_matchup_eval"},
        messages=[{"role": "user", "content": raw_text}],
    )

    tool_block = next((b for b in response.content if isinstance(b, ToolUseBlock)), None)
    if tool_block is None:
        raise ValueError(f"matchup_workflow: model did not return a tool call for game {ctx.game_id}")
    tool_input: dict = tool_block.input
    tool_input["game_id"] = ctx.game_id
    result = MatchupEvalJSON.model_validate(tool_input)
    result = _normalize_team_ids(result, ctx.home_team_id, ctx.away_team_id)
    logger.info("matchup_workflow result: %s", result)

    return result


def _normalize_team_ids(result: MatchupEvalJSON, home_id: str, away_id: str) -> MatchupEvalJSON:
    """Replace any non-abbreviation team IDs (e.g. numeric NBA IDs) with the canonical abbreviations."""
    known = {home_id, away_id}

    def _fix(raw: str) -> str:
        if raw in known:
            return raw
        lower = raw.lower()
        if home_id.lower() in lower:
            return home_id
        if away_id.lower() in lower:
            return away_id
        return raw

    def _fix_game(g: dict) -> dict:
        return {
            **g,
            "home_team_id": _fix(g["home_team_id"]),
            "away_team_id": _fix(g["away_team_id"]),
            "winner_team_id": _fix(g["winner_team_id"]),
        }

    patched = result.model_dump()
    patched["h2h_last_10"] = [_fix_game(g) for g in patched["h2h_last_10"]]
    patched["last_h2h"] = _fix_game(patched["last_h2h"])
    return MatchupEvalJSON.model_validate(patched)