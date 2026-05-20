import type { GameData } from '../../types/game';
import mockData from '../../../mock_data.json';
import GameCard from './GameCard';

type PanelConfig = {
  id: string;
  label: string;
  index: number;
};

const games = mockData as GameData[];

const BOTTOM_PANELS: PanelConfig[] = [
  { id: 'specific-game',     label: 'Specific Game',     index: 2 },
  { id: 'agent-analysis',    label: 'Agent Analysis',    index: 3 },
  { id: 'ai-recommendation', label: 'AI Recommendation', index: 4 },
  { id: 'recent-meetings',   label: 'Recent Meetings',   index: 5 },
];

export default function DashboardPage() {
  return (
    <div className="dashboard">
      <div className="panel panel--top">
        <div className="panel-header">
          <span className="tab-index">1</span>
          <span className="panel-title">NBA Games Today</span>
        </div>
        <div className="panel-body panel-body--scroll">
          {games.map((game, i) => (
            <GameCard key={i} game={game} />
          ))}
        </div>
      </div>

      <div className="panels-row">
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
