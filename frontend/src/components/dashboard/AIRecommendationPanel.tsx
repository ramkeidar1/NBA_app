import type { OrchestratorRecommendation } from '../../types/recommendation';
import RecommendationCard from './RecommendationCard';

interface AIRecommendationPanelProps {
  recommendation: OrchestratorRecommendation | null;
}

export default function AIRecommendationPanel({ recommendation }: AIRecommendationPanelProps) {
  if (!recommendation) {
    return (
      <div className="sg-empty">
        <span className="sg-empty-text">Select a game to view AI recommendation</span>
      </div>
    );
  }

  return (
    <div className="ai-rec-panel">
      <RecommendationCard rec={recommendation} />
    </div>
  );
}
