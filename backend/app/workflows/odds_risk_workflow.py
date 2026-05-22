import copy
import logging
from dotenv import load_dotenv
import anthropic

from app.schemas import OddsRiskEvalJSON, GameContext, InjuryEntry

load_dotenv()

logger = logging.getLogger(__name__)

_client = anthropic.AsyncAnthropic()

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

_DUMMY_ODDS_RISKS = [
    OddsRiskEvalJSON(
        game_id="LAL_GSW",
        moneyline_home=-155.0,
        moneyline_away=135.0,
        spread=-3.5,
        over_under=224.5,
        market_implied_probability_home=60.8,
        injury_report=[
            InjuryEntry(
                player_name="Luka Doncic",
                team_id="LAL",
                status="OUT",
                impact_note="Sidelined for the entire second round of the playoffs due to a severe injury. Significantly shifts offensive creation burden to secondary playmakers."
            ),
            InjuryEntry(
                player_name="Jonathan Kuminga",
                team_id="GSW",
                status="QUESTIONABLE",
                impact_note="Day-to-day following mild ankle soreness during game 2 of the WCF. Potential limit to frontcourt athleticism and transition versatility if restricted."
            ),
            InjuryEntry(
                player_name="Brandin Podziemski",
                team_id="GSW",
                status="OUT",
                impact_note="Sidelined for the remainder of the series due to a non-displaced wrist fracture. Thins out backcourt depth and secondary playmaking rotations."
            ),
            InjuryEntry(
                player_name="Austin Reaves",
                team_id="LAL",
                status="AVAILABLE",
                impact_note="Fully cleared, no structural or physical limitations. Expected to shoulder heavy volume and primary scoring responsibility."
            ),
            InjuryEntry(
                player_name="Stephen Curry",
                team_id="GSW",
                status="AVAILABLE",
                impact_note="Fully cleared, managing standard veteran recovery schedules between games. Anchors the primary spacing engine."
            ),
            InjuryEntry(
                player_name="LeBron James",
                team_id="LAL",
                status="AVAILABLE",
                impact_note="Fully cleared, handling veteran workload management cleanly. Anticipated high usage rate in high-leverage positions."
            )
        ]
    )
]

async def run(ctx: GameContext, raw_text: str, dummy: bool = True) -> OddsRiskEvalJSON:
    if dummy:
        print(f"DUMMY ODDS_&_RISK_WORKFLOW_{ctx.game_id}")
        result = next((odds_risks for odds_risks in _DUMMY_ODDS_RISKS if ctx.game_id in odds_risks.game_id), None)
        if result is None:
            # Fallback to first item if it's a generic test
            result = _DUMMY_ODDS_RISKS[0]
            
        result = result.model_copy(update={"game_id": ctx.game_id})
        return result

    response = await _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        tools=[_TOOL_DEF],
        tool_choice={"type": "tool", "name": "submit_odds_risk_eval"},
        messages=[{"role": "user", "content": raw_text}],
    )

    tool_input: dict = response.content[0].input
    tool_input["game_id"] = ctx.game_id
    result = OddsRiskEvalJSON.model_validate(tool_input)
    print(result)

    return result