---
name: project-courmind-state
description: CourMind NBA app — five-node pipeline design, milestone state, and locked decisions as of 2026-05-22
metadata:
  type: project
---

CourMind is a FastAPI+React NBA forecasting platform with a five-node async pipeline. Backend lives in `backend/app/`.

**Pipeline nodes:**
- Orchestrator (pure Python, no LLM): asyncio.gather() + SSE emission
- form_workflow (Haiku): parser — extracts team form data into FormEvalJSON
- matchup_workflow (Haiku): parser — extracts H2H matchup data into MatchupEvalJSON
- odds_risk_workflow (Haiku): parser — extracts odds/injury data into OddsRiskEvalJSON (no cache, ~30min TTL)
- final_prediction (Sonnet): synthesizer — three eval JSONs -> FinalPredictionJSON

**Locked decisions:**
- tool_use pattern (not JSON mode) — proven in example_agent.py
- extended_thinking: bool = False flag on FinalPredictionJSON (toggleable without rewrite)
- Graceful degradation: catch agent failure, emit agent_error SSE, pass None to final agent, set partial_telemetry=True
- Named SSE events: agent_start, agent_complete, agent_error, pipeline_complete
- AsyncAnthropic client at module level per workflow file
- Mock data for now (LAL vs GSW May 22 2026 fixture in backend/app/mock_data/)

**Current milestone: M1** — filling backend/app/schemas/ package. Scaffold exists, all domain files empty:
- form.py, matchup.py, odds_risk.py, prediction.py — empty placeholders
- base.py — does not exist yet (needs to be created for GameContext, SSEEvent, AgentError)
- __init__.py — currently a copy of the old legacy flat schemas.py (needs to become a clean re-export)
- schemas.py (root level) — legacy flat file, still used by existing API routes; must not break during M1

**Open:** Q3 — single game_id vs batch endpoint. User asked for plain-language explanation before deciding.

**Why:** Demonstrates multi-agent async orchestration, SSE streaming, and probabilistic reasoning for portfolio/interview.
**How to apply:** Haiku = parser/extractor only. Sonnet = synthesizer only. Never mix roles. All models inherit from Pydantic BaseModel with strict type hints and Google-style docstrings.
