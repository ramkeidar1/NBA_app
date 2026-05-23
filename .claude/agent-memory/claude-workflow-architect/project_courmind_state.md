---
name: project-courmind-state
description: CourMind backend pipeline state as of 2026-05-23 — fully wired, dummy mode works, several bugs identified in real LLM path
metadata:
  type: project
---

CourMind is a FastAPI+React NBA forecasting platform with a five-node async pipeline. Backend lives in `backend/app/`.

**Pipeline nodes (all implemented):**
- Orchestrator (pure Python, no LLM): asyncio.gather() + SSE emission, hard/soft pipeline modes
- form_workflow (claude-haiku-4-5): parser — extracts team form data into FormEvalJSON
- matchup_workflow (claude-haiku-4-5): parser — extracts H2H matchup data into MatchupEvalJSON
- odds_risk_workflow (claude-haiku-4-5): parser — extracts odds/injury data into OddsRiskEvalJSON (no cache, always live)
- final_prediction (claude-sonnet-4-6): synthesizer — three eval JSONs -> FinalPredictionJSON

**Status as of 2026-05-23:** Full pipeline implemented and wired. DUMMY_MODE=true works end-to-end. Real LLM path (DUMMY_MODE=false) is wired but has runtime bugs that must be fixed before going live.

**Locked decisions:**
- tool_use pattern (not JSON mode) — force tool_choice so model always calls the tool
- $ref resolver pattern — final_prediction.py has _resolve_refs(); form_workflow.py MISSING this (Bug 1)
- extended_thinking: bool = False flag on FinalPredictionJSON (toggleable without rewrite)
- Graceful degradation: asyncio.gather(return_exceptions=True), emit agent_error SSE, partial_telemetry=True
- Actual SSE event names: status, context_loaded, agent_update, agent_error, final_prediction, done
- AsyncAnthropic client singleton in client.py, shared across all workflows
- Mock data in backend/app/mock_data/ (LAL vs GSW May 22 2026 fixture)
- DUMMY_MODE env var (default true) — each workflow returns pre-built instances from dummy_data.py
- Two-level cache: TTLCache (1hr in-process) + Supabase (persistent); soft pipeline checks both before running agents

**Bugs to fix before real LLM use:**
1. form_workflow.py — nested H2HGame $ref not resolved before Anthropic tool schema (will crash)
2. games.py — `game_id` NameError in GET /api/matches/{team_id} error handler
3. supabase.py — "SECRECT" typo in env var `SUPABASE_API_SECRECT_KEY`
4. FormEvalJSON — kebab alias_generator causes mismatch between LLM tool output keys (kebab) and manual injection keys (snake_case)
5. matchup_workflow.py + odds_risk_workflow.py — dummy lookup uses `ctx.game_id in matchup.game_id` (reversed, will fail for longer game_ids)

**Why:** Demonstrates multi-agent async orchestration, SSE streaming, and probabilistic reasoning for portfolio/interview.
**How to apply:** Haiku = parser/extractor only. Sonnet = synthesizer only. Never mix roles. All public functions need Google-style docstrings. All Anthropic SDK calls need local try/except.
