import copy
import logging
from anthropic.types import ToolUseBlock

from app.client import anthropic_client
from app.schemas import (
    GameContext,
    FormEvalJSON,
    MatchupEvalJSON,
    OddsRiskEvalJSON,
    FinalPredictionJSON,
)
from app.schemas.prediction import FormWorkflowJSON, MatchupWorkflowJSON, OddsRiskWorkflowJSON

logger = logging.getLogger(__name__)

_DUMMY_MODE = True

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

# ─── Dummy data ───────────────────────────────────────────────────────────────

_DUMMY_PREDICTION = FinalPredictionJSON(
    game_id="LAL_GSW",
    predicted_winner_id="GSW",
    predicted_winner_name="Golden State Warriors",
    confidence=0.63,
    risk_rating="MEDIUM",
    reasoning_narrative=(
        "GSW's +5.7 net rating, 7-3 H2H dominance, and -155 market line collectively outweigh LAL's "
        "compromised roster — Doncic OUT strips their primary creation engine while Curry anchors GSW's spacing. "
        "Moderate confidence (0.63) reflects Podziemski's absence and Kuminga's questionable status introducing "
        "bilateral roster risk, but form, matchup history, and market consensus align on a GSW home win."
    ),
    form_report=FormWorkflowJSON(
        confidence=0.68,
        workflow_weight=0.40,
        winner_form="GSW 6-4, +5.7 net",
        loser_form="LAL 4-6, -3.8 net",
        key_context="Doncic OUT, LAL depleted",
    ),
    matchup_report=MatchupWorkflowJSON(
        confidence=0.71,
        workflow_weight=0.35,
        last_match="GSW 118-112 Mar-8",
        last_ten_matches="GSW leads 7-3",
        net_differential="GSW +4.2 avg",
    ),
    odds_risk_report=OddsRiskWorkflowJSON(
        confidence=0.61,
        workflow_weight=0.25,
        winner_odds=1.8,
        key_context=[
            "GSW -155, 60.8% implied",
            "Spread -3.5 GSW",
            "Doncic OUT LAL",
            "Podziemski OUT GSW",
            "Kuminga QUESTIONABLE GSW",
            "O/U 224.5",
        ],
    ),
    signal_disagreement_flag=False,
    partial_telemetry=False,
    extended_thinking=False,
)

# ─── run() ────────────────────────────────────────────────────────────────────

async def run(
    ctx: GameContext,
    home_form: FormEvalJSON | None,
    away_form: FormEvalJSON | None,
    matchup: MatchupEvalJSON | None,
    odds_risk: OddsRiskEvalJSON | None,
    partial_telemetry: bool,
    extended_thinking: bool = False,
) -> FinalPredictionJSON:
    if _DUMMY_MODE:
        logger.info("DUMMY FINAL_PREDICTION_%s", ctx.game_id)
        result = _DUMMY_PREDICTION.model_copy(
            update={
                "game_id": ctx.game_id,
                "partial_telemetry": partial_telemetry,
                "extended_thinking": extended_thinking,
            }
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

    create_kwargs: dict = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 8000 if extended_thinking else 4096,
        "system": _SYSTEM_PROMPT,
        "tools": [_TOOL_DEF],
        "tool_choice": {"type": "tool", "name": "submit_final_prediction"},
        "messages": [{"role": "user", "content": user_message}],
    }
    if extended_thinking:
        create_kwargs["betas"] = ["interleaved-thinking-2025-05-14"]
        create_kwargs["thinking"] = {"type": "enabled", "budget_tokens": 3000}

    response = await anthropic_client.messages.create(**create_kwargs)

    tool_block = next((b for b in response.content if isinstance(b, ToolUseBlock)), None)
    if tool_block is None:
        raise ValueError(f"final_prediction: model did not return a tool call for game {ctx.game_id}")

    tool_input: dict[str, object] = tool_block.input
    tool_input["game_id"] = ctx.game_id
    tool_input["partial_telemetry"] = partial_telemetry
    tool_input["extended_thinking"] = extended_thinking

    result = FinalPredictionJSON.model_validate(tool_input)
    logger.info("final_prediction result: %s", result)

    return result
