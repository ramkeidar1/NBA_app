import copy
import logging
from anthropic.types import ToolUseBlock

from app.client import anthropic_client
from app.config import DUMMY_MODE
from app.schemas import (
    GameContext,
    FormEvalJSON,
    MatchupEvalJSON,
    OddsRiskEvalJSON,
    FinalPredictionJSON,
)

from app.workflows.dummy_data import _DUMMY_PREDICTION


logger = logging.getLogger(__name__)

_DUMMY_MODE = DUMMY_MODE

# ─── $ref resolver ───────────────────────────────────────────────────────────

def _resolve_refs(schema: dict) -> dict:
    """Inline all $ref pointers so the Anthropic tool API receives a flat schema."""
    defs = schema.get("$defs", {})

    def resolve(obj):
        if isinstance(obj, list):
            return [resolve(i) for i in obj]
        if not isinstance(obj, dict):
            return obj
        if "$ref" in obj:
            ref_name = obj["$ref"].split("/")[-1]
            return resolve(copy.deepcopy(defs[ref_name]))
        return {k: resolve(v) for k, v in obj.items() if k != "$defs"}

    return resolve(schema)


# ─── Tool schema (built once at import) ──────────────────────────────────────

_BASE_SCHEMA = _resolve_refs(FinalPredictionJSON.model_json_schema())
for _field in ("game_id", "partial_telemetry", "extended_thinking"):
    _BASE_SCHEMA.get("properties", {}).pop(_field, None)
    if _field in _BASE_SCHEMA.get("required", []):
        _BASE_SCHEMA["required"].remove(_field)

_TOOL_DEF = {
    "name": "submit_final_prediction",
    "description": (
        "Submit the fully synthesized final prediction for the game, including "
        "per-signal sub-reports and a consolidated decision."
    ),
    "input_schema": _BASE_SCHEMA,
}

# ─── System prompt ────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = (
    "You are CourMind's master prediction synthesizer. "
    "You receive structured outputs from three specialist agents — form, matchup, and odds/risk — "
    "and must consolidate them into a single authoritative game prediction.\n\n"

    "RULES:\n"
    "1. predicted_winner_id must be a team ID abbreviation (e.g. 'GSW', 'LAL'). "
    "predicted_winner_name must be the full team name (e.g. 'Golden State Warriors').\n"
    "2. All confidence scores and workflow_weight values must be decimals between 0.0 and 1.0. "
    "The three workflow_weight values across form_report, matchup_report, and odds_risk_report must sum to exactly 1.0.\n"
    "3. Set signal_disagreement_flag to true if any two sub-signals point to different winners.\n"
    "4. reasoning_narrative must be exactly 2 sentences. Each sentence must be dense and informative, "
    "covering form momentum, H2H history, market conditions, and the final decision — all compressed "
    "into those two sentences. No filler words.\n"
    "5. risk_rating is LOW when confidence > 0.70 and no signal disagreement, HIGH when confidence "
    "< 0.50 or signal_disagreement_flag is true, and MEDIUM otherwise.\n"
    "6. If any agent input is marked UNAVAILABLE, reduce that agent's workflow_weight to 0.0 and "
    "redistribute its weight to the remaining agents proportionally.\n"
    "7. Populate winner_form and loser_form in form_report relative to your predicted_winner_id decision.\n"
    "8. ALL string fields except reasoning_narrative must be 3-4 words maximum. "
    "This applies to: winner_form, loser_form, key_context (form_report), "
    "last_match, last_ten_matches, net_differential, and each item in key_context (odds_risk_report). "
    "Be telegraphic — use stats and abbreviations, not prose."
)

async def run(
    ctx: GameContext,
    home_form: FormEvalJSON | None,
    away_form: FormEvalJSON | None,
    matchup: MatchupEvalJSON | None,
    odds_risk: OddsRiskEvalJSON | None,
    partial_telemetry: bool,
    dummy: bool = _DUMMY_MODE,
) -> FinalPredictionJSON:
    if dummy:
        logger.info("DUMMY FINAL_PREDICTION_%s", ctx.game_id)
        result = _DUMMY_PREDICTION.model_copy(
            update={"game_id": ctx.game_id, "partial_telemetry": partial_telemetry}
        )
        return result

    def _serialise(obj) -> str:
        return obj.model_dump_json(indent=2) if obj is not None else "UNAVAILABLE — agent failed"

    user_message = (
        f"[HOME FORM]\n{_serialise(home_form)}\n\n"
        f"[AWAY FORM]\n{_serialise(away_form)}\n\n"
        f"[HEAD-TO-HEAD MATCHUP]\n{_serialise(matchup)}\n\n"
        f"[ODDS & RISK]\n{_serialise(odds_risk)}\n\n"
        f"Game: {ctx.home_team_id} (Home) vs {ctx.away_team_id} (Away) — {ctx.game_date}\n"
        f"Venue: {ctx.venue}\n"
        f"Partial telemetry active: {partial_telemetry}"
    )

    response = await anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=_SYSTEM_PROMPT,
        tools=[_TOOL_DEF],
        tool_choice={"type": "tool", "name": "submit_final_prediction"},
        messages=[{"role": "user", "content": user_message}],
    )

    tool_block = next((b for b in response.content if isinstance(b, ToolUseBlock)), None)
    if tool_block is None:
        raise ValueError(f"final_prediction: model did not return a tool call for game {ctx.game_id}")

    tool_input: dict = tool_block.input
    tool_input["game_id"] = ctx.game_id
    tool_input["partial_telemetry"] = partial_telemetry
    tool_input["extended_thinking"] = False

    result = FinalPredictionJSON.model_validate(tool_input)
    logger.info("final_prediction result: %s", result)

    return result
