import type { OrchestratorRecommendation } from '../../types/recommendation';
import RecommendationCard from './RecommendationCard';

interface AIRecommendationPanelProps {
  recommendation: OrchestratorRecommendation | null;
  onRefresh: (mode: 'soft' | 'hard') => void;
}

export default function AIRecommendationPanel({ recommendation, onRefresh }: AIRecommendationPanelProps) {
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
      <div className="ai-rec-panel__actions">
        <button
          className="ai-rec-panel__btn ai-rec-panel__btn--soft"
          onClick={() => onRefresh('soft')}
        >
          Soft Update
        </button>
        <button
          className="ai-rec-panel__btn ai-rec-panel__btn--hard"
          onClick={() => onRefresh('hard')}
        >
          Hard Update
        </button>
      </div>
    </div>
  );
}
