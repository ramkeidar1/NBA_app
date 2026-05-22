import copy
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
import aiofiles
import anthropic

from app.schemas import MatchupEvalJSON, GameContext, H2HGame

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
_BASE_SCHEMA = copy.deepcopy(MatchupEvalJSON.model_json_schema())
for _field in ("game_id", "team_id"):
    _BASE_SCHEMA.get("properties", {}).pop(_field, None)
    if _field in _BASE_SCHEMA.get("required", []):
        _BASE_SCHEMA["required"].remove(_field)

_TOOL_DEF = {
    "name": "submit_matchup_eval",
    "description": "Extract and submit the structured team form evaluation from the raw data.",
    "input_schema": _BASE_SCHEMA,
}

_DUMMY_FORMS = [
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

async def run(ctx: GameContext, raw_text: str, team_id: str, dummy: bool = True) -> MatchupEvalJSON:
    if dummy:
        print("DUMMY MATCHUP_WORKFLOW")
        result = _DUMMY_FORMS.get(team_id)
        if result is None:
            raise ValueError(f"No dummy data for team_id={team_id}")
        result = result.model_copy(update={"game_id": ctx.game_id})
        return result

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
    result = MatchupEvalJSON.model_validate(tool_input)
    print(result)

    return result