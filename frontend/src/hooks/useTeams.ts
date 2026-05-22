import { useEffect, useState } from 'react';
import type { TeamProfile } from '../types/game';
import { fetchTeams } from '../services/api';

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

    fetchTeams(controller.signal)
      .then((data) => setTeams(data))
      .catch((err: unknown) => {
        if (err instanceof Error && err.name === 'AbortError') return;
        setError(err instanceof Error ? err.message : 'Failed to load teams');
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, []);

  return { teams, loading, error };
}
