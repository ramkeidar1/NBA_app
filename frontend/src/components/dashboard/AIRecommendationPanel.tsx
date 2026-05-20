import type { OrchestratorRecommendation } from '../../types/recommendation';
import rawData from '../../../mock_data_OrchestratorAgent.json';
import RecommendationCard from './RecommendationCard';

const recommendations = rawData as OrchestratorRecommendation[];

export default function AIRecommendationPanel() {
  return (
    <div className="ai-rec-panel">
      {recommendations.map((rec) => (
        <RecommendationCard key={rec.name} rec={rec} />
      ))}
    </div>
  );
}
