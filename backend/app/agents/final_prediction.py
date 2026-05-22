import copy
import logging
import os
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

_DUMMY_MODE = os.getenv("USE_DUMMY_AGENTS", "false").lower() == "true"

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
    "4. reasoning_narrative must be at least 3 sentences: one summarising form, one summarising "
    "matchup history, one summarising market conditions, and a final sentence stating the decision.\n"
    "5. risk_rating is LOW when confidence > 0.70 and no signal disagreement, HIGH when confidence "
    "< 0.50 or signal_disagreement_flag is true, and MEDIUM otherwise.\n"
    "6. If any agent input is marked UNAVAILABLE, reduce that agent's workflow_weight to 0.0 and "
    "redistribute its weight to the remaining agents proportionally.\n"
    "7. Populate winner_form and loser_form in form_report relative to your predicted_winner_id decision."
)

# ─── Dummy data ───────────────────────────────────────────────────────────────

_DUMMY_PREDICTION = FinalPredictionJSON(
    game_id="LAL_GSW",
    predicted_winner_id="GSW",
    predicted_winner_name="Golden State Warriors",
    confidence=0.63,
    risk_rating="MEDIUM",
    reasoning_narrative=(
        "The Golden State Warriors enter this fixture with superior recent form, posting a 6-4 record "
        "over their last 10 games against the Lakers' 4-6 stretch, anchored by a +5.7 net rating differential. "
        "Head-to-head history over the last 10 meetings heavily favours Golden State with 7 wins, "
        "including the most recent encounter on March 8 where they won by 6 points at home. "
        "Market conditions reflect this edge with GSW installed as -155 moneyline favourites implying 60.8% "
        "win probability, though the absence of Luka Doncic for LAL and Brandin Podziemski for GSW "
        "introduces meaningful roster uncertainty on both sides. "
        "Weighing all three signals, Golden State is projected to win at home with moderate confidence."
    ),
    form_report=FormWorkflowJSON(
        confidence=0.68,
        workflow_weight=0.40,
        winner_form=(
            "Golden State Warriors — 6-4 over last 10, ORTG 118.2, DRTG 112.5, net rating +5.7. "
            "Strong home record of 5-2 in the postseason stretch."
        ),
        loser_form=(
            "Los Angeles Lakers — 4-6 over last 10, ORTG 110.4, DRTG 114.2, net rating -3.8. "
            "Luka Doncic sidelined significantly reduces offensive ceiling."
        ),
        key_context=(
            "Lakers playing without their primary ball-handler and MVP candidate. "
            "Austin Reaves and LeBron James must absorb heavy usage volume."
        ),
    ),
    matchup_report=MatchupWorkflowJSON(
        confidence=0.71,
        workflow_weight=0.35,
        last_match=(
            "March 8, 2026 — GSW 118, LAL 112 at Chase Center. "
            "Warriors controlled the fourth quarter, outscoring LAL by 9 in the final period."
        ),
        last_ten_matches=(
            "GSW leads the last 10 H2H meetings 7-3. "
            "Warriors have won 3 consecutive matchups and 5 of the last 6. "
            "Average margin of victory for GSW in wins: +7.1 points."
        ),
        net_differential=(
            "GSW holds a +4.2 average point differential across the last 10 meetings. "
            "Home/away split favours GSW strongly at Chase Center (5-1 in last 6 home games vs LAL)."
        ),
    ),
    odds_risk_report=OddsRiskWorkflowJSON(
        confidence=0.61,
        workflow_weight=0.25,
        key_context=[
            "GSW moneyline -155 implies 60.8% market win probability — aligned with model output.",
            "Spread set at -3.5 for GSW, consistent with historical average margin.",
            "Luka Doncic (LAL) OUT — significant downward pressure on LAL implied probability.",
            "Brandin Podziemski (GSW) OUT — reduces backcourt depth but Curry fully available.",
            "Jonathan Kuminga (GSW) QUESTIONABLE — monitor day-of status for frontcourt impact.",
            "Over/Under 224.5 — slightly elevated given LAL's defensive struggles in last 10.",
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
) -> FinalPredictionJSON:
    if _DUMMY_MODE:
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
