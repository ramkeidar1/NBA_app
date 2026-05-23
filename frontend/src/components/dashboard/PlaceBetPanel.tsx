import type { OrchestratorRecommendation } from '../../types/recommendation';
import BetForm from './BetForm';

interface PlaceBetPanelProps {
  recommendation: OrchestratorRecommendation | null;
}

export default function PlaceBetPanel({ recommendation }: PlaceBetPanelProps) {

  if (!recommendation) {
    return (
      <div className="sg-empty">
        <span className="sg-empty-text">Select a game to place a bet</span>
      </div>
    );
  }

  return <BetForm rec={recommendation} />;
}
