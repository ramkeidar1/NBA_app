# app/main.py
import json
import logging
from pathlib import Path

import aiofiles
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import MatchFixture, NBATeamSchema

logger = logging.getLogger(__name__)

MOCK_DATA_DIR = Path(__file__).parent / "mock_data"

app = FastAPI(title="CourMind AI Core Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _read_json_file(filename: str) -> list:
    """Read a JSON file from the mock_data directory without blocking the event loop."""
    file_path = MOCK_DATA_DIR / filename
    if not file_path.exists():
        logger.error("Mock data file not found", extra={"path": str(file_path)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data file '{filename}' could not be located.",
        )
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            raw = await f.read()
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.exception("JSON decode failure", extra={"file": filename})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data file '{filename}' contains malformed JSON.",
        ) from exc


@app.get("/api/matches", response_model=list[MatchFixture])
async def get_matches() -> list[MatchFixture]:
    data = await _read_json_file("games.json")
    return [MatchFixture.model_validate(item) for item in data]


@app.get("/api/teams", response_model=list[NBATeamSchema])
async def get_teams() -> list[NBATeamSchema]:
    data = await _read_json_file("teams.json")
    return [NBATeamSchema.model_validate(item) for item in data]
