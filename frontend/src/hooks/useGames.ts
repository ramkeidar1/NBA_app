import { useEffect, useState } from 'react';
import type { GameData } from '../types/game';

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

    fetch('/api/matches', { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const ct = res.headers.get('content-type') ?? '';
        if (!ct.includes('application/json')) {
          throw new Error(`Expected JSON but got ${ct || 'unknown content type'} — is the backend running?`);
        }
        return res.json();
      })
      .then((data: GameData[]) => setGames(data))
      .catch((err: unknown) => {
        if (err instanceof Error && err.name === 'AbortError') return;
        setError(err instanceof Error ? err.message : 'Failed to load games');
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, []);

  return { games, loading, error };
}
