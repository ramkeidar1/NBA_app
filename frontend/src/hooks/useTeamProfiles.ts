import { useEffect, useState } from 'react';
import type { TeamProfile } from '../types/game';
import { fetchTeam } from '../services/api';

interface UseTeamProfilesResult {
  home: TeamProfile | null;
  away: TeamProfile | null;
  loading: boolean;
  error: string | null;
}

export function useTeamProfiles(homeId: string | null, awayId: string | null): UseTeamProfilesResult {
  const [home, setHome] = useState<TeamProfile | null>(null);
  const [away, setAway] = useState<TeamProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!homeId || !awayId) return;

    const controller = new AbortController();

    Promise.all([
      fetchTeam(homeId, controller.signal),
      fetchTeam(awayId, controller.signal),
    ])
      .then(([homeProfile, awayProfile]) => {
        setHome(homeProfile);
        setAway(awayProfile);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (err instanceof Error && err.name === 'AbortError') return;
        setError(err instanceof Error ? err.message : 'Failed to load team profiles');
        setLoading(false);
      });

    return () => controller.abort();
  }, [homeId, awayId]);

  return { home, away, loading, error };
}
