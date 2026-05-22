import type { GameData, TeamProfile } from '../types/game';
import type { OrchestratorRecommendation } from '../types/recommendation';
import type { GameAgentAnalysis } from '../types/analysis';

const BACKEND_BASE = 'http://127.0.0.1:8000';

// ─── Helpers ────────────────────────────────────────────────────────────────

async function fetchJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const ct = res.headers.get('content-type') ?? '';
  if (!ct.includes('application/json')) {
    throw new Error(`Expected JSON but got ${ct || 'unknown'} — is the backend running?`);
  }
  return res.json() as Promise<T>;
}

// ─── REST endpoints ──────────────────────────────────────────────────────────

export function fetchMatches(signal?: AbortSignal): Promise<GameData[]> {
  return fetchJson<GameData[]>('/api/matches', signal);
}

export function fetchTeams(signal?: AbortSignal): Promise<TeamProfile[]> {
  return fetchJson<TeamProfile[]>('/api/teams', signal);
}

// ─── SSE streams ─────────────────────────────────────────────────────────────

export function openPredictionsStream(): EventSource {
  return new EventSource('/api/predictions/stream');
}

export function openAgentAnalysisStream(): EventSource {
  return new EventSource('/api/agent_analysis/stream');
}

export type { OrchestratorRecommendation, GameAgentAnalysis };

// ─── Commands ────────────────────────────────────────────────────────────────

interface CommandRequest {
  game_id: string;
  command: string;
}

interface CommandResponse {
  status: string;
  message?: string;
}

export async function postCommand(game_id: string, command: string): Promise<CommandResponse> {
  const body: CommandRequest = { game_id, command };
  const res = await fetch(`${BACKEND_BASE}/command`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST /command failed: ${res.status}`);
  return res.json() as Promise<CommandResponse>;
}
