import type { OrchestratorRecommendation } from '../../types/recommendation';
import BetForm from './BetForm';
import LoadingDots from '../ui/LoadingDots';

interface PlaceBetPanelProps {
  recommendation: OrchestratorRecommendation | null;
  isStreaming: boolean;
}

export default function PlaceBetPanel({ recommendation, isStreaming }: PlaceBetPanelProps) {
  if (isStreaming) {
    return <LoadingDots />;
  }

  if (!recommendation) {
    return (
      <div className="sg-empty">
        <span className="sg-empty-text">Select a game to place a bet</span>
      </div>
    );
  }

  return <BetForm rec={recommendation} />;
}
