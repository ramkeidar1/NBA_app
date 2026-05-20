import { useEffect, useState } from 'react';
import type { OrchestratorRecommendation } from '../types/recommendation';

interface UsePredictionsStreamResult {
  recommendations: OrchestratorRecommendation[];
  loading: boolean;
  error: string | null;
}

export function usePredictionsStream(): UsePredictionsStreamResult {
  const [recommendations, setRecommendations] = useState<OrchestratorRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const es = new EventSource('/api/predictions/stream');

    es.onmessage = (e) => {
      try {
        const rec = JSON.parse(e.data as string) as OrchestratorRecommendation;
        setRecommendations((prev) => [...prev, rec]);
        setLoading(false);
      } catch {
        setError('Failed to parse prediction event');
        es.close();
        setLoading(false);
      }
    };

    es.addEventListener('done', () => {
      es.close();
      setLoading(false);
    });

    es.onerror = () => {
      setError('Stream connection failed — is the backend running?');
      es.close();
      setLoading(false);
    };

    return () => es.close();
  }, []);

  return { recommendations, loading, error };
}
