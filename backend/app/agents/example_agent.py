"""
example_agent.py — A minimal, self-contained learning script for the tool_use pattern.

HOW STRUCTURED OUTPUT WORKS VIA tool_use IN 4 STEPS:

  STEP 1 — Define a Pydantic schema.
    Write a normal Pydantic v2 model for the shape you want back from the LLM.
    This is the source of truth for your output structure.

  STEP 2 — Convert the schema to an Anthropic tool definition.
    The Anthropic API does not natively accept Pydantic models, but it does
    accept JSON Schema objects (the "input_schema" field on a tool). Pydantic
    can generate that JSON Schema. We wrap it in the exact dict shape the API
    expects: {"name": ..., "description": ..., "input_schema": ...}.

  STEP 3 — Force the model to call that tool with tool_choice.
    Passing tool_choice={"type": "tool", "name": "<tool_name>"} tells the model
    it MUST call exactly that tool. This is what forces structured output:
    instead of free-form text, the model fills in the tool's parameters, which
    are validated against the JSON Schema before being returned to you.

  STEP 4 — Extract and validate the tool_use block.
    The response content will contain a block with type="tool_use". Its .input
    field is a dict matching your schema. Feed it into Pydantic for runtime
    validation and a typed Python object.

WHY THIS PATTERN?
    Unlike asking the model to "return JSON", tool_use forces schema compliance
    at the API level. The model cannot accidentally return extra prose or
    malformed JSON — it is structurally constrained to produce valid input for
    the named tool.

Run from the backend/ directory:
    python -m app.agents.example_agent
"""

import asyncio
import json
import logging
import os
from dotenv import load_dotenv
import anthropic
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# STEP 1: Define a Pydantic v2 output schema
# ---------------------------------------------------------------------------


class GameSummary(BaseModel):
    """Structured summary produced by the model for a single NBA matchup.

    Attributes:
        home_team: Full name of the home team (e.g. "Boston Celtics").
        away_team: Full name of the away team (e.g. "Miami Heat").
        predicted_winner: Which team the model predicts will win.
        confidence_pct: Win probability for the predicted winner, 0–100.
        key_factor: One concise sentence explaining the decisive factor.
    """

    home_team: str = Field(description="Full name of the home team.")
    away_team: str = Field(description="Full name of the away team.")
    predicted_winner: str = Field(
        description="Full name of the team predicted to win."
    )
    confidence_pct: float = Field(
        ge=0.0,
        le=100.0,
        description="Win probability for the predicted winner, as a percentage 0–100.",
    )
    key_factor: str = Field(
        description="One sentence describing the single most decisive factor."
    )


# ---------------------------------------------------------------------------
# STEP 2: Build an Anthropic tool definition from the Pydantic schema
# ---------------------------------------------------------------------------


def build_tool_from_model(model_cls: type[BaseModel], tool_name: str) -> dict:
    """Convert a Pydantic v2 BaseModel into an Anthropic tool definition dict.

    The Anthropic API expects tools in the form:
        {
            "name": "<snake_case_name>",
            "description": "<what the tool does>",
            "input_schema": <JSON Schema object>
        }

    Pydantic's .model_json_schema() produces a JSON Schema object that maps
    directly to input_schema. We use the model docstring as the description.

    Args:
        model_cls: A Pydantic v2 BaseModel subclass to convert.
        tool_name: The tool name string the API will use (snake_case).

    Returns:
        A dict ready to be passed in the tools= list of messages.create().
    """
    schema = model_cls.model_json_schema()

    # Pydantic may add a top-level "title" key that the API does not need.
    schema.pop("title", None)

    return {
        "name": tool_name,
        "description": (model_cls.__doc__ or "").strip().split("\n")[0],
        "input_schema": schema,
    }


# ---------------------------------------------------------------------------
# STEP 3 + 4: Make the API call and validate the result
# ---------------------------------------------------------------------------

TOOL_NAME = "record_game_summary"


async def analyze_matchup(home_team: str, away_team: str) -> GameSummary:
    """Ask Claude to produce a structured GameSummary for a given matchup.

    Uses tool_choice to force the model to fill in the GameSummary schema
    rather than returning free-form text.

    Args:
        home_team: Name of the home team.
        away_team: Name of the away team.

    Returns:
        A validated GameSummary instance.

    Raises:
        ValueError: If the model response does not contain a tool_use block.
        anthropic.APIConnectionError: On network failures.
        anthropic.RateLimitError: If the API rate limit is exceeded.
    """
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # STEP 2 — convert schema → tool definition
    tool_def = build_tool_from_model(GameSummary, TOOL_NAME)

    user_message = (
        f"Analyse this NBA matchup and record a game summary.\n"
        f"Home team: {home_team}\n"
        f"Away team: {away_team}"
    )

    logger.info("Calling Claude for matchup: %s vs %s", home_team, away_team)

    # STEP 3 — force the model to call our tool
    try:
        response = await client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            tools=[tool_def],
            # This is the key line: the model MUST call TOOL_NAME.
            tool_choice={"type": "tool", "name": TOOL_NAME},
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.APIConnectionError as exc:
        logger.error("API connection failed: %s", exc)
        raise
    except anthropic.RateLimitError as exc:
        logger.warning("Rate limited by Anthropic API: %s", exc)
        raise

    logger.info("Response stop_reason: %s", response.stop_reason)

    # STEP 4 — extract the tool_use block and validate into Pydantic
    tool_use_block = next(
        (block for block in response.content if block.type == "tool_use"),
        None,
    )

    if tool_use_block is None:
        raise ValueError(
            f"Model did not return a tool_use block. "
            f"Content was: {response.content}"
        )

    # tool_use_block.input is already a parsed dict; Pydantic validates it.
    summary = GameSummary.model_validate(tool_use_block.input)
    return summary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main() -> None:
    """Run a single example call and print the validated result."""
    summary = await analyze_matchup(
        home_team="Boston Celtics",
        away_team="Miami Heat",
    )

    print("\n--- GameSummary (validated Pydantic model) ---")
    print(json.dumps(summary.model_dump(), indent=2))
    print(f"\nPredicted winner : {summary.predicted_winner}")
    print(f"Confidence       : {summary.confidence_pct:.1f}%")
    print(f"Key factor       : {summary.key_factor}")


if __name__ == "__main__":
    asyncio.run(main())
