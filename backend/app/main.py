# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import games, teams, predictions, analysis

app = FastAPI(title="CourMind AI Core Gateway")

# Make sure all your local frontend variations are listed here
origins = [
    "http://localhost:5174",  # Your current active Vite port
    "http://127.0.0.1:5174",  
    "http://localhost:5173",  # Good to keep as a fallback
    "http://localhost:3000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # <-- Change this from the hardcoded string list to your variable!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router)
app.include_router(teams.router)
app.include_router(predictions.router)
app.include_router(analysis.router)