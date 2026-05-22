import { useEffect, useState } from 'react';
import type { GameAgentAnalysis } from '../types/analysis';
import { openAgentAnalysisStream } from '../services/api';

interface UseAgentAnalysisStreamResult {
  analyses: GameAgentAnalysis[];
  loading: boolean;
  error: string | null;
}

export function useAgentAnalysisStream(): UseAgentAnalysisStreamResult {
  const [analyses, setAnalyses] = useState<GameAgentAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const es = openAgentAnalysisStream();

    es.onmessage = (e) => {
      try {
        const latestAnalysis = JSON.parse(e.data) as GameAgentAnalysis[];
        setAnalyses([...latestAnalysis]);
        setLoading(false);
      } catch {
        setError('Failed to parse agent analysis event');
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

  return { analyses, loading, error };
}
