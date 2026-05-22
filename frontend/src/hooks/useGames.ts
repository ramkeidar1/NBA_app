import { useEffect, useState } from 'react';
import type { GameData } from '../types/game';
import { fetchMatches } from '../services/api';

interface UseGamesResult {
  games: GameData[];
  loading: boolean;
  error: string | null;
}

export function useGames(): UseGamesResult {
  const [games, setGames] = useState<GameData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    fetchMatches(controller.signal)
      .then((data) => setGames(data))
      .catch((err: unknown) => {
        if (err instanceof Error && err.name === 'AbortError') return;
        setError(err instanceof Error ? err.message : 'Failed to load games');
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, []);

  return { games, loading, error };
}
