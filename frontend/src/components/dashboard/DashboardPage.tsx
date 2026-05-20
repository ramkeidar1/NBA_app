type PanelConfig = {
  id: string;
  label: string;
  index: number;
};

const PANELS: PanelConfig[] = [
  { id: 'nba-games-today',   label: 'NBA Games Today',   index: 1 },
  { id: 'specific-game',     label: 'Specific Game',     index: 2 },
  { id: 'agent-analysis',    label: 'Agent Analysis',    index: 3 },
  { id: 'ai-recommendation', label: 'AI Recommendation', index: 4 },
  { id: 'recent-meetings',   label: 'Recent Meetings',   index: 5 },
];

const [top, ...rest] = PANELS;

export default function DashboardPage() {
  return (
    <div className="dashboard">
      <div className="panel panel--top">
        <div className="panel-header">
          <span className="tab-index">{top.index}</span>
          <span className="panel-title">{top.label}</span>
        </div>
        <div className="panel-body" />
      </div>

      <div className="panels-row">
        {rest.map((panel) => (
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
