# Task Requirements — NBA Games Panel Slides

## Branch
`feature/nba-games-panel-slides`

## Objective
Populate the NBA Games Today top panel with game cards sourced from mock data.

## Requirements
- [x] Each game in `mock_data.json` renders as a card in the top panel
- [x] Card displays: game time (formatted from ISO), home team, away team
- [x] Each team row shows: logo (from `public/icons/`), name, record, odds
- [x] Cards scroll horizontally inside the panel
- [x] Strict TypeScript interfaces — no implicit any
- [x] Zero type errors (`tsc --noEmit`)
- [x] Clean production build (`npm run build`)

## Files Changed
- `frontend/public/icons/` — team logo PNGs (moved from `frontend/icons/`)
- `frontend/src/types/game.ts` — `GameData`, `TeamData` interfaces
- `frontend/src/components/dashboard/GameCard.tsx` — single game card component
- `frontend/src/components/dashboard/DashboardPage.tsx` — imports mock data, maps to GameCard
- `frontend/src/index.css` — game card and scrollable panel styles
