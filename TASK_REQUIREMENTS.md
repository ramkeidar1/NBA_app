# Task: Fetch Games from Supabase `matches` Table

## Objective
Replace the static `games.json` mock with live data from the Supabase `matches` table.

## Requirements
- `GET /api/matches` must read from the `matches` DB table, not the file system
- `record` and `odds` fields dropped from `TeamData` (not available in `matches` table)
- Frontend renders game cards with team name and ID only

## Changes
- `backend/app/api/games.py` — removed file I/O; maps `matches` rows via `_row_to_fixture()`
- `backend/app/schemas/__init__.py` — `TeamData` stripped to `id` + `name`
- `frontend/src/types/game.ts` — `TeamData` stripped to `id` + `name`
- `frontend/src/components/dashboard/GameCard.tsx` — removed `record`/`odds` from `TeamRow`
- `frontend/src/__tests__/GameCard.test.tsx` — updated fixtures to match new schema

## Verification
- `npx tsc --noEmit` — clean
- `npx vitest run` — 14/14 tests pass
