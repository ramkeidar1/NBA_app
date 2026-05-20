# app/main.py
import json
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.schemas import MatchFixture
# from app.orchestrator import ProgrammaticOrchestrator

app = FastAPI(title="CourMind AI Core Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/matches", response_model=List[MatchFixture])
async def get_matches():
    """Reads the static games array from disk and feeds the UI selector layout"""
    current_dir = Path(__file__).parent
    games_file_path = current_dir / "mock_data" / "games.json"
    
    if not games_file_path.exists():
        raise HTTPException(
            status_code=500, 
            detail="Structural data file 'games.json' could not be located on disk repository."
        )
        
    with open(games_file_path, "r", encoding="utf-8") as f:
        matches_data = json.load(f)
        
    return matches_data