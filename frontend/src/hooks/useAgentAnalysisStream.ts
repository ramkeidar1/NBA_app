import { useEffect, useState } from 'react';
import type { GameAgentAnalysis } from '../types/analysis';

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
    const es = new EventSource('/api/agent_analysis/stream');

    es.onmessage = (e) => {
      try {
        const analysis = JSON.parse(e.data as string) as GameAgentAnalysis;
        setAnalyses((prev) => [...prev, analysis]);
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
