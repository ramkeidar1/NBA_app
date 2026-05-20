import { useEffect, useState } from 'react';
import type { TeamProfile } from '../types/game';

interface UseTeamsResult {
  teams: TeamProfile[];
  loading: boolean;
  error: string | null;
}

export function useTeams(): UseTeamsResult {
  const [teams, setTeams] = useState<TeamProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    fetch('/api/teams', { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const ct = res.headers.get('content-type') ?? '';
        if (!ct.includes('application/json')) {
          throw new Error(`Expected JSON but got ${ct || 'unknown content type'} — is the backend running?`);
        }
        return res.json();
      })
      .then((data: TeamProfile[]) => setTeams(data))
      .catch((err: unknown) => {
        if (err instanceof Error && err.name === 'AbortError') return;
        setError(err instanceof Error ? err.message : 'Failed to load teams');
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, []);

  return { teams, loading, error };
}
