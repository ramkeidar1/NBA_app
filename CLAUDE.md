# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# NBA_app Guidelines

## Tech Stack & Structure
- Frontend: React 19, TypeScript, Tailwind CSS (**not yet installed** — add before using Tailwind classes)
- Backend: Python 3.11, FastAPI, Pydantic v2 (**not yet created** — `./backend/` directory does not exist yet)
- DB/Data: Local JSON caching (or PostgreSQL)
- Core App Entry: Web server runs from `./backend/main.py`, Frontend from `./frontend/`

## Core Workspace Scope
- All API route handlers must live inside `./backend/api/`
- All React presentation components must live inside `./frontend/src/components/`
- Data schemas for NBA players/games are mapped strictly inside `./backend/schemas/`

## Execution & Verification Commands
- Start Backend Dev: `cd backend && fastapi dev main.py`
- Start Frontend Dev: `cd frontend && npm run dev`
- Lint Frontend: `cd frontend && npm run lint`
- Run Backend Tests: `pytest` (from project root)
- Frontend tests: not yet configured — add Vitest or Jest before running
- Global Strict Typecheck: `cd frontend && npx tsc --noEmit`

## TypeScript Strictness
- `noUnusedLocals` and `noUnusedParameters` are enabled in `tsconfig.app.json` — remove unused variables and parameters, do not leave them as `_x`.
- `erasableSyntaxOnly` is enabled — avoid TypeScript-only syntax that requires runtime erasure.

## Engineering Laws & Restrictions
- **No Implicit Any:** Always write strict TypeScript interfaces for API payloads.
- **Async Safety:** Never use blocking synchronous code (`time.sleep` or standard `requests`) inside async FastAPI endpoints. Use `asyncio.sleep` or `httpx`.
- **State Hygiene:** Keep React state scoped locally unless it genuinely dictates top-level app behavior.
- **Error Boundaries:** Always wrap external NBA API endpoints inside explicit try/except blocks with structured error handling—never let connection errors fail silently.

## Gotchas
- When the backend is created, add a `server.proxy` entry in `frontend/vite.config.ts` to forward `/api` requests to the FastAPI dev server. Without this, the React dev server and FastAPI run on different ports and CORS will block requests.

## 🛰️ System Concept & Project Vision
**CourMind** is an enterprise-grade, multi-agent AI orchestration platform designed for probabilistic NBA sports forecasting, market sentiment tracking, and positive expected value ($+EV$) value detection. 

Rather than functioning as gambling or traditional sports betting software, CourMind is engineered as an **Analytical Mission Control Dashboard**. The primary objective of the platform is to solve high-dimensional data aggregation problems, reconcile conflicting operational metrics, and expose real-time autonomous reasoning chains in an institutional-grade user interface.

In a technical interview context, this project demonstrates mastery of:
* **Asynchronous Multi-Agent Topologies** (decoupling extraction, processing, and synthesis).
* **Non-Blocking Parallelism** via Python's asynchronous event loops.
* **Strict Type-Safe Data Contracts** across boundary lines using Pydantic.
* **Reactive UI Architectures** driven by Server-Sent Events (SSE) streaming state changes directly into Next.js.

---

## 🏗️ System Architecture

```
                      +-------------------+
                      | Next.js Frontend  |
                      +-------------------+
                                ▲  
                                │ (Server-Sent Events / Event Streaming)
                      +-------------------+
                      |   FastAPI Gateway |
                      +-------------------+
                                │
                                ▼
                      +-------------------+
                      | 1. Orchestrator   | (Deterministic Python Layer)
                      +-------------------+
                                │
        +-----------------------+-----------------------+
        │ (Async Execution)                             │ (Async Execution)
        ▼                                               ▼
+---------------+                               +---------------+
| 2. Matchup &  |                               | 3. Intuition  |
|   Form Agent  |                               |   & Odds Agent|
| (Situational) |                               |    (Value/EV) |
+---------------+                               +---------------+
        │                                               │
        +-----------------------+-----------------------+
                                │
                                ▼ (Pydantic Outbound Payload)
                      +-------------------+
                      | 4. Decision &     | (Master Aggregator /
                      |    Risk Agent     |  Weighted Synthesis)
                      +-------------------+
                                │
                                ▼
                      +-------------------+
                      | Supabase Database | (Persistent Storage State)
                      +-------------------+
```

---

## 🤖 Consolidated Agent Framework

To maximize token lifecycle management, optimize pricing models, and significantly minimize network API roundtrip times, the runtime architecture operates across a four-node deterministic topology:

### 1. Orchestrator Node (Deterministic Programmatic Code)
* **Responsibility:** Pipeline synchronization, request routing, validation telemetry, and external payload pre-processing.
* **Implementation:** Pure, highly optimized asynchronous Python code execution layer. Eliminates expensive LLM routing costs while enforcing operational boundary rules.
* **Behavior:** Ingests live stats, formats system payloads, triggers concurrent workers using `asyncio.gather()`, logs states, and streams downstream chunk boundaries.

### 2. Matchup & Form Agent (LLM Contextual Worker)
* **Responsibility:** Cross-references dynamic momentum patterns against physical baseline limitations.
* **Inputs Analysed:** Traditional and advanced efficiency metrics (Offensive/Defensive Ratings, PACE coefficients), recent performance variance vectors, localized rest/travel conditions, and specific micro-level player tactical matchups.
* **Model Tier:** High-speed, high-throughput context processing model (e.g., *Claude 3.5 Haiku* or *GPT-4o-mini*).

### 3. Intuition & Odds Agent (LLM Quantitative Worker)
* **Responsibility:** Functions as a pure market mathematical auditor tracking alpha discrepancies.
* **Inputs Analysed:** Opening lines versus real-time consensus lines, market volume drift indicators, public betting ticket volume distribution vs. total cash allocation, and mathematical validation of line value ($+EV$).
* **Model Tier:** High-speed, high-throughput context processing model (e.g., *Claude 3.5 Haiku* or *GPT-4o-mini*).

### 4. Decision & Risk Agent (LLM Master Synthesizer)
* **Responsibility:** Final consensus formation, algorithmic component prioritization, downside evaluation, and deterministic output schema compilation.
* **Inputs Analysed:** Strict JSON data payloads originating from Worker Agents 2 and 3.
* **Model Tier:** Premium reasoning and deep deductive extraction model (e.g., *Claude 3.5 Sonnet*).

---

## 🗄️ Database Strategy (Supabase / PostgreSQL)

The physical schema establishes permanent state storage and performance auditing capabilities over historical analysis windows:

* **`matches` Table:** Base operational ledger containing real-time fixtures, scheduled game times, team attributes, and changing baseline market indices.
* **`analyses` Table:** Tracks independent outputs generated by individual worker nodes. Serves as an immutable audit trail mapping specific internal agent viewpoints over time.
* **`recommendations` Table:** Stores the final multi-agent structural outputs, confidence percentages, specific risk ratings, and consolidated summary objects generated by Agent 4.

---

## 🛠️ Unified Development Roadmap & Stack

### Core Technologies
* **Frontend Ecosystem:** Next.js (App Router), Tailwind CSS, component layouts utilizing `shadcn/ui`, and micro-animations configured via `Framer Motion`.
* **Backend Ecosystem:** FastAPI (Python 3.11+), asynchronous connection pools, and strict schema isolation managed using `Pydantic v2`.
* **AI Integration:** Anthropic Claude Python SDK / OpenAI Structured Outputs APIs.

### Code Style & Implementation Standard Guidelines
1.  **Strict Contract Boundaries:** All inter-agent interaction models must explicitly inherit from a common `BaseModel` framework ensuring predictable execution graphs.
2.  **Explicit Execution Models:** Do not execute sequential agent processing loops where parallel topologies are available. Leverage `asyncio.gather` for concurrent processing across worker spaces.
3.  **Graceful Degraded States:** If a processing worker encounters an external API bottleneck, the pipeline must catch exceptions cleanly, report the structural failure inside the `Live Agent Reasoning` stream, and enable the Master Aggregator to make decisions using partial telemetry profiles.
4.  **Token Budget Management:** Cache match statistics and analysis states inside Supabase. Prevent re-compilation of AI orchestration workflows on identical match profiles unless variance thresholds on betting spreads exceed designated tolerances.
