import copy
import logging
from anthropic.types import ToolUseBlock

from app.client import anthropic_client
from app.config import DUMMY_MODE
from app.schemas import OddsRiskEvalJSON, GameContext
from app.workflows.dummy_data import _DUMMY_ODDS_RISKS

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a precise NBA sports data extraction agent. "
    "Your task is to parse the raw text to extract sports betting odds (moneyline, spread, over/under) "
    "and parse the consolidated injury and risk report into a structured format. "
    "Extract only facts explicitly mentioned in the text. Do not calculate or extrapolate any figures."
)

# Build the tool schema once at import time, removing fields we inject manually.
_BASE_SCHEMA = copy.deepcopy(OddsRiskEvalJSON.model_json_schema())
for _field in ("game_id",):
    _BASE_SCHEMA.get("properties", {}).pop(_field, None)
    if _field in _BASE_SCHEMA.get("required", []):
        _BASE_SCHEMA["required"].remove(_field)

_TOOL_DEF = {
    "name": "submit_odds_risk_eval",
    "description": "Extract and submit the structured odds and risk evaluation from the raw data.",
    "input_schema": _BASE_SCHEMA,
}

async def run(ctx: GameContext, raw_text: str, dummy: bool = DUMMY_MODE) -> OddsRiskEvalJSON:
    if dummy:
        logger.info("DUMMY ODDS_RISK_WORKFLOW_%s", ctx.game_id)
        result = next((odds_risks for odds_risks in _DUMMY_ODDS_RISKS if ctx.game_id in odds_risks.game_id), None)
        if result is None:
            # Fallback to first item if it's a generic test
            result = _DUMMY_ODDS_RISKS[0]
            
        result = result.model_copy(update={"game_id": ctx.game_id})
        return result

    response = await anthropic_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        tools=[_TOOL_DEF],
        tool_choice={"type": "tool", "name": "submit_odds_risk_eval"},
        messages=[{"role": "user", "content": raw_text}],
    )

    tool_block = next((b for b in response.content if isinstance(b, ToolUseBlock)), None)
    if tool_block is None:
        raise ValueError(f"odds_risk_workflow: model did not return a tool call for game {ctx.game_id}")
    tool_input: dict = tool_block.input
    tool_input["game_id"] = ctx.game_id
    result = OddsRiskEvalJSON.model_validate(tool_input)
    logger.info("odds_risk_workflow result: %s", result)

    return result