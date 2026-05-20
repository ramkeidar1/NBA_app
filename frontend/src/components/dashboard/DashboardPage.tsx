import { useState } from 'react';
import type { GameData } from '../../types/game';
import type { OrchestratorRecommendation } from '../../types/recommendation';
import type { AgentAnalysisMap, GameAgentAnalysis } from '../../types/analysis';
import mockGames from '../../../mock_data_games.json';
import rawRecs_AIReccommendations from '../../../mock_data_OrchestratorAgent_AIReccomendation.json';
import rawAgentAnalysis from '../../../mock_data_OrechestratorAgent_AgentAnalysis.json';
import GameCard from './GameCard';
import SpecificGamePanel from './SpecificGamePanel';
import AIRecommendationPanel from './AIRecommendationPanel';
import AgentAnalysisPanel from './AgentAnalysisPanel';

const games = mockGames as GameData[];
const recommendations = rawRecs_AIReccommendations as OrchestratorRecommendation[];
const agentAnalysisMap = rawAgentAnalysis as AgentAnalysisMap;

function gameKey(game: GameData): string {
  return `${game['Home team'].name.replace(/ /g, '_')} vs ${game['Away team'].name.replace(/ /g, '_')}`;
}

function findRecommendation(game: GameData): OrchestratorRecommendation | null {
  const key = gameKey(game);
  return recommendations.find((r) => r.name === key) ?? null;
}

function findAgentAnalysis(game: GameData): GameAgentAnalysis | null {
  return agentAnalysisMap[gameKey(game)] ?? null;
}


export default function DashboardPage() {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  const selectedGame = selectedIndex !== null ? games[selectedIndex] : null;
  const selectedRec = selectedGame ? findRecommendation(selectedGame) : null;
  const selectedAnalysis = selectedGame ? findAgentAnalysis(selectedGame) : null;

  return (
    <div className="dashboard">
      <div className="panel panel--top">
        <div className="panel-header">
          <span className="tab-index">1</span>
          <span className="panel-title">NBA Games Today</span>
        </div>
        <div className="panel-body panel-body--scroll">
          {games.map((game, i) => (
            <GameCard
              key={i}
              game={game}
              isSelected={selectedIndex === i}
              onClick={() => setSelectedIndex(selectedIndex === i ? null : i)}
            />
          ))}
        </div>
      </div>

      <div className="panels-row">
        <div className="panel">
          <div className="panel-header">
            <span className="tab-index">2</span>
            <span className="panel-title">Specific Game</span>
          </div>
          <div className="panel-body">
            <SpecificGamePanel game={selectedGame} />
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <span className="tab-index">3</span>
            <span className="panel-title">AI Recommendation</span>
          </div>
          <div className="panel-body panel-body--overflow">
            <AIRecommendationPanel recommendation={selectedRec} />
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <span className="tab-index">4</span>
            <span className="panel-title">Agent Analysis</span>
          </div>
          <div className="panel-body panel-body--overflow">
            <AgentAnalysisPanel analysis={selectedAnalysis} />
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <span className="tab-index">5</span>
            <span className="panel-title">Recent Meetings</span>
          </div>
          <div className="panel-body" />
        </div>
      </div>
    </div>
  );
}
