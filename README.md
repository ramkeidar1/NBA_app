# CourMind

An enterprise-grade, multi-agent AI orchestration platform for probabilistic NBA game analysis. CourMind aggregates live stats, runs parallel LLM reasoning chains, and streams real-time agent output to a React dashboard.

---

## Architecture

```
React Frontend (Vite)
       │
       │  REST + Server-Sent Events
       ▼
FastAPI Gateway
       │
       ▼
 Orchestrator  ──── asyncio.gather() ────┐
       │                                 │
       ▼                                 ▼
Matchup & Form Agent            Intuition & Odds Agent
   (Claude Haiku)                    (Claude Haiku)
       │                                 │
       └──────────────┬──────────────────┘
                      ▼
           Decision & Risk Agent
              (Claude Sonnet)
                      │
                      ▼
              Supabase Database
```

The Orchestrator is pure async Python — no LLM calls, no blocking I/O. It pre-processes payloads, runs the two worker agents concurrently, then passes their outputs to the final synthesis agent. All intermediate state is cached in Supabase with an in-process TTL cache layer in front.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Zustand, Vite |
| Backend | Python 3.11, FastAPI, Pydantic v2 |
| AI | Anthropic Claude SDK (Haiku + Sonnet) |
| Database | Supabase (PostgreSQL) |
| Streaming | Server-Sent Events (SSE) via `sse-starlette` |
| Auth | JWT dual-token (access + refresh) |

---

## Project Structure

```
NBA_app/
├── backend/
│   ├── app/
│   │   ├── agents/          # Final prediction agent (Sonnet)
│   │   ├── api/             # FastAPI route handlers
│   │   ├── auth/            # JWT utilities and dependencies
│   │   ├── cache/           # Supabase + in-memory TTL caching
│   │   ├── schemas/         # Pydantic v2 data contracts
│   │   ├── workflows/       # Worker agent workflows (Haiku)
│   │   ├── orchestrator.py  # Pipeline coordinator
│   │   ├── config.py        # Environment config
│   │   └── main.py          # App entry point
│   ├── tests/
│   │   ├── conftest.py      # Shared fixtures (TestClient, token factory)
│   │   └── test_core.py     # Auth, SSE stream, and pipeline tests
│   └── pytest.ini
└── frontend/
    └── src/
        ├── __tests__/       # Vitest test suite
        ├── components/      # React UI components
        ├── hooks/           # Data-fetching hooks
        ├── pages/           # Route-level page components
        ├── services/        # API + auth service layer
        ├── store/           # Zustand auth store
        └── types/           # TypeScript interfaces
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Supabase](https://supabase.com) project
- An [Anthropic](https://console.anthropic.com) API key

### 1. Clone the repo

```bash
git clone https://github.com/ramkeidar1/NBA_app.git
cd NBA_app
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
# Required
JWT_SECRET=your-strong-secret-here
JWT_REFRESH_SECRET=your-strong-refresh-secret-here
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_SECRET_KEY=your-supabase-service-role-key

# Optional
DUMMY_MODE=true        # Set to false to make real LLM calls
LOG_LEVEL=INFO
```

> `DUMMY_MODE=true` (the default) runs the full pipeline using mock data — no API spend required during development.

Start the backend:

```bash
fastapi dev app/main.py
# Runs on http://127.0.0.1:8000
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5174
```

The Vite dev server proxies `/api` and `/auth` requests to the FastAPI backend automatically — no CORS configuration needed during development.

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `JWT_SECRET` | Yes | Signs access tokens |
| `JWT_REFRESH_SECRET` | Yes | Signs refresh tokens |
| `ANTHROPIC_API_KEY` | Yes (in live mode) | Claude API key |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_API_SECRET_KEY` | Yes | Supabase service role key |
| `DUMMY_MODE` | No | `true` uses mock data, `false` calls Claude (default: `true`) |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING`, `ERROR` (default: `INFO`) |

---

## API Overview

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/login` | Login, returns access + refresh tokens |
| `POST` | `/auth/refresh` | Refresh access token |
| `POST` | `/auth/logout` | Invalidate refresh token |
| `GET` | `/api/matches` | Fetch today's games |
| `GET` | `/api/teams/{team_id}` | Fetch team profile |
| `GET` | `/api/analysis/stream/{game_id}` | SSE stream — runs the full agent pipeline |
| `GET` | `/api/predictions/{game_id}` | Fetch cached final prediction |
| `GET` | `/api/matchup/{game_id}` | Fetch cached matchup analysis |

The SSE stream endpoint requires a valid JWT passed as `?token=<access_token>`. All other protected endpoints use a standard `Authorization: Bearer <token>` header.

---

## Testing

### Backend (pytest)

Tests live in `backend/tests/`. Run from inside `backend/`:

```bash
pytest -v                     # Run all tests
pytest -v tests/test_core.py  # Run a specific file
```

Covers: JWT expiry, login 401, SSE stream auth (missing/invalid token), and full dummy pipeline completion. `DUMMY_MODE` is forced to `true` in tests — no API spend.

### Frontend (Vitest)

Tests live in `frontend/src/__tests__/`. Run from inside `frontend/`:

```bash
npm test                  # Watch mode (development)
npm test -- --run         # Single run (CI)
npm coverage              # Run with coverage report
```

Covers: `gameKey` pure logic, `agentUpdatesToGameAgentAnalysis` mapping, `GameCard` rendering, and `useGames` hook states (loading, success, error).

---

## Development Commands

```bash
# Backend
fastapi dev app/main.py       # Start with hot reload

# Frontend
npm run dev                   # Start Vite dev server
npm run build                 # Production build
npm run lint                  # ESLint
npx tsc --noEmit              # Type check
```
