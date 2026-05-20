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
      if (!e.data || e.data.trim() === '') return;
      try {
        const latestPredictions = JSON.parse(e.data) as OrchestratorRecommendation[];        
        console.log(latestPredictions)
        setRecommendations([...latestPredictions]);
        console.log(latestPredictions)
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
