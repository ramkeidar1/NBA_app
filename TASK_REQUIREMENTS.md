# Task Requirements — Game Selection & Specific Game Panel

## Branch
`feature/game-selection-specific-panel`

## Objective
Clicking a game card in the NBA Games Today panel selects it and populates the Specific Game panel with full team details from `mock_data_teams.json`.

## Requirements
- [x] Clicking a `GameCard` selects it (highlighted with accent border + glow)
- [x] Clicking the same card deselects it
- [x] Selected game index stored in local `useState` in `DashboardPage`
- [x] `SpecificGamePanel` shows empty state when no game is selected
- [x] `SpecificGamePanel` shows both teams side-by-side when a game is selected
- [x] Each team column shows: logo, name, home/away label, conference, division, home court, standing, offensive rating, defensive rating, star player
- [x] Team data looked up from `mock_data_teams.json` via underscore-formatted name key
- [x] Strict TypeScript — `TeamProfile`, `TeamStanding` interfaces, no implicit any
- [x] Zero type errors (`tsc --noEmit`)
- [x] Clean production build (`npm run build`)

## Files Changed
- `frontend/src/types/game.ts` — added `TeamProfile`, `TeamStanding` interfaces
- `frontend/src/components/dashboard/SpecificGamePanel.tsx` — new team detail panel
- `frontend/src/components/dashboard/GameCard.tsx` — added `isSelected`, `onClick` props
- `frontend/src/components/dashboard/DashboardPage.tsx` — selection state, wired panels
- `frontend/src/index.css` — selected card styles, specific game panel styles
