import type { GameData, TeamProfile } from '../types/game';
import type { OrchestratorRecommendation } from '../types/recommendation';
import type { GameAgentAnalysis } from '../types/analysis';
import type { FinalPredictionJSON, MatchupEvalJSON } from '../types/prediction';
import { refresh } from './authService';
import { useAuthStore } from '../store/authStore';

const BACKEND_BASE = 'http://127.0.0.1:8000';

// ─── Helpers ────────────────────────────────────────────────────────────────

function authHeaders(): HeadersInit {
  const token = useAuthStore.getState().accessToken;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function fetchJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(url, { signal, headers: authHeaders() });

  if (res.status === 401) {
    // attempt silent token refresh once
    try {
      const { access_token } = await refresh();
      useAuthStore.getState().setAccessToken(access_token);
      const retried = await fetch(url, {
        signal,
        headers: { Authorization: `Bearer ${access_token}` },
      });
      if (!retried.ok) throw new Error(`HTTP ${retried.status}`);
      return retried.json() as Promise<T>;
    } catch {
      useAuthStore.getState().logout();
      throw new Error('Session expired — please log in again.');
    }
  }

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

export function fetchTeam(teamId: string, signal?: AbortSignal): Promise<TeamProfile> {
  return fetchJson<TeamProfile>(`/api/teams/${teamId}`, signal);
}

export function fetchCachedPrediction(game_id: string, signal?: AbortSignal): Promise<FinalPredictionJSON> {
  return fetchJson<FinalPredictionJSON>(`/api/predictions/${game_id}`, signal);
}

export function fetchCachedMatchup(game_id: string, signal?: AbortSignal): Promise<MatchupEvalJSON> {
  return fetchJson<MatchupEvalJSON>(`/api/matchup/${game_id}`, signal);
}

// ─── SSE streams ─────────────────────────────────────────────────────────────

export function openAnalysisStream(game_id: string, mode: 'hard' | 'soft' = 'hard'): EventSource {
  return new EventSource(`/api/analysis/stream/${game_id}?mode=${mode}`);
}

export type { OrchestratorRecommendation, GameAgentAnalysis };

// ─── Commands ────────────────────────────────────────────────────────────────

interface CommandRequest {
  game_id: string;
  command: string;
  mode: 'soft' | 'hard';
}

interface CommandResponse {
  status: string;
  message?: string;
  stream_url?: string;
}

export async function postCommand(game_id: string, command: string, mode: 'soft' | 'hard'): Promise<CommandResponse> {
  const body: CommandRequest = { game_id, command, mode };
  const res = await fetch(`${BACKEND_BASE}/command`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST /command failed: ${res.status}`);
  return res.json() as Promise<CommandResponse>;
}
