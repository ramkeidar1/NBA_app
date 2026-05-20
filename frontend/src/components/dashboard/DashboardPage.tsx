import { useState } from 'react';
import type { GameData } from '../../types/game';
import type { OrchestratorRecommendation } from '../../types/recommendation';
import mockGames from '../../../mock_data_games.json';
import rawRecs from '../../../mock_data_OrchestratorAgent.json';
import GameCard from './GameCard';
import SpecificGamePanel from './SpecificGamePanel';
import AIRecommendationPanel from './AIRecommendationPanel';

type PanelConfig = {
  id: string;
  label: string;
  index: number;
};

const games = mockGames as GameData[];
const recommendations = rawRecs as OrchestratorRecommendation[];

function findRecommendation(game: GameData): OrchestratorRecommendation | null {
  const key = `${game['Home team'].name.replace(/ /g, '_')} vs ${game['Away team'].name.replace(/ /g, '_')}`;
  return recommendations.find((r) => r.name === key) ?? null;
}

const BOTTOM_PANELS: PanelConfig[] = [
  { id: 'agent-analysis',  label: 'Agent Analysis',  index: 4 },
  { id: 'recent-meetings', label: 'Recent Meetings', index: 5 },
];

export default function DashboardPage() {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  const selectedGame = selectedIndex !== null ? games[selectedIndex] : null;
  const selectedRec = selectedGame ? findRecommendation(selectedGame) : null;

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

        {BOTTOM_PANELS.map((panel) => (
          <div key={panel.id} className="panel">
            <div className="panel-header">
              <span className="tab-index">{panel.index}</span>
              <span className="panel-title">{panel.label}</span>
            </div>
            <div className="panel-body" />
          </div>
        ))}
      </div>
    </div>
  );
}
