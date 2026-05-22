import copy
import logging
from anthropic.types import ToolUseBlock

from app.client import anthropic_client
from app.schemas import MatchupEvalJSON, GameContext, H2HGame

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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

_DUMMY_MATCHUPS = [
    MatchupEvalJSON(
        game_id="LAL_GSW",
        last_h2h=H2HGame(
            date="2026-03-08",
            home_team_id="GSW",
            away_team_id="LAL",
            home_score=118,
            away_score=112,
            winner_team_id="GSW",
        ),
        h2h_last_10=[
            H2HGame(
                date="2026-03-08",
                home_team_id="GSW",
                away_team_id="LAL",
                home_score=118,
                away_score=112,
                winner_team_id="GSW",
            ),
            H2HGame(
                date="2026-01-25",
                home_team_id="LAL",
                away_team_id="GSW",
                home_score=105,
                away_score=112,
                winner_team_id="GSW",
            ),
            H2HGame(
                date="2025-12-15",
                home_team_id="GSW",
                away_team_id="LAL",
                home_score=121,
                away_score=115,
                winner_team_id="GSW",
            ),
            H2HGame(
                date="2025-10-30",
                home_team_id="LAL",
                away_team_id="GSW",
                home_score=110,
                away_score=104,
                winner_team_id="LAL",
            ),
            H2HGame(
                date="2025-04-05",
                home_team_id="GSW",
                away_team_id="LAL",
                home_score=128,
                away_score=120,
                winner_team_id="GSW",
            ),
            H2HGame(
                date="2025-03-12",
                home_team_id="LAL",
                away_team_id="GSW",
                home_score=114,
                away_score=122,
                winner_team_id="GSW",
            ),
            H2HGame(
                date="2025-01-18",
                home_team_id="GSW",
                away_team_id="LAL",
                home_score=109,
                away_score=113,
                winner_team_id="LAL",
            ),
            H2HGame(
                date="2024-12-25",
                home_team_id="LAL",
                away_team_id="GSW",
                home_score=124,
                away_score=118,
                winner_team_id="LAL",
            ),
            H2HGame(
                date="2024-04-09",
                home_team_id="LAL",
                away_team_id="GSW",
                home_score=120,
                away_score=134,
                winner_team_id="GSW",
            ),
            H2HGame(
                date="2024-03-16",
                home_team_id="LAL",
                away_team_id="GSW",
                home_score=121,
                away_score=128,
                winner_team_id="GSW",
            ),
        ],
    )
]

async def run(ctx: GameContext, raw_text: str, dummy: bool = True) -> MatchupEvalJSON:
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
    logger.info("matchup_workflow result: %s", result)

    return result