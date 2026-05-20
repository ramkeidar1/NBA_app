import type { GameAgentAnalysis, FormAgentData, MatchupAgentData, RiskAgentData } from '../../types/analysis';

interface AgentAnalysisPanelProps {
  analysis: GameAgentAnalysis | null;
}

interface CertaintyBarProps {
  value: number;
  colorVar: string;
}

function CertaintyBar({ value, colorVar }: CertaintyBarProps) {
  return (
    <div className="aa-certainty-wrap">
      <div className="aa-certainty-header">
        <span className="aa-certainty-label">Certainty</span>
        <span className="aa-certainty-pct" style={{ color: `var(${colorVar})` }}>{value}%</span>
      </div>
      <div className="aa-certainty-track">
        <div
          className="aa-certainty-fill"
          style={{ width: `${value}%`, background: `var(${colorVar})` }}
        />
      </div>
    </div>
  );
}

interface FieldRowProps {
  label: string;
  value: string;
}

function FieldRow({ label, value }: FieldRowProps) {
  return (
    <div className="aa-field-row">
      <span className="aa-field-label">{label}</span>
      <span className="aa-field-value">{value}</span>
    </div>
  );
}

interface FormAgentCardProps {
  data: FormAgentData;
}

function FormAgentCard({ data }: FormAgentCardProps) {
  return (
    <div className="aa-agent-card aa-agent-card--form">
      <div className="aa-agent-header">
        <span className="aa-agent-badge aa-agent-badge--form">Form Agent</span>
      </div>
      <CertaintyBar value={data.Certainty} colorVar="--accent" />
      <div className="aa-fields">
        <FieldRow label="Winner Form" value={data['Expected winner Form']} />
        <FieldRow label="Loser Form" value={data['Expected losser Form']} />
        <FieldRow label="Context" value={data.Addons} />
      </div>
    </div>
  );
}

interface MatchupAgentCardProps {
  data: MatchupAgentData;
}

function MatchupAgentCard({ data }: MatchupAgentCardProps) {
  return (
    <div className="aa-agent-card aa-agent-card--matchup">
      <div className="aa-agent-header">
        <span className="aa-agent-badge aa-agent-badge--matchup">Matchup Agent</span>
      </div>
      <CertaintyBar value={data.Certainty} colorVar="--spread-color" />
      <div className="aa-fields">
        <FieldRow label="Winner Form" value={data['Expected winner Form']} />
        <FieldRow label="Loser Form" value={data['Expected losser Form']} />
        <FieldRow label="Net Differential" value={data['Deferntial net']} />
        <FieldRow label="Key Matchup" value={data['Intersting Matchups']} />
      </div>
    </div>
  );
}

interface RiskAgentCardProps {
  data: RiskAgentData;
}

function RiskAgentCard({ data }: RiskAgentCardProps) {
  return (
    <div className="aa-agent-card aa-agent-card--risk">
      <div className="aa-agent-header">
        <span className="aa-agent-badge aa-agent-badge--risk">Risk Agent</span>
      </div>
      <CertaintyBar value={data.Certainty} colorVar="--risk-high" />
      <div className="aa-fields">
        {data.Addons.map((addon, i) => (
          <div key={i} className="aa-risk-flag">
            <span className="aa-risk-dot" />
            <span className="aa-risk-text">{addon}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function AgentAnalysisPanel({ analysis }: AgentAnalysisPanelProps) {
  if (!analysis) {
    return (
      <div className="sg-empty">
        <span className="sg-empty-text">Select a game to view agent analysis</span>
      </div>
    );
  }

  return (
    <div className="aa-panel">
      <FormAgentCard data={analysis['Form Agent']} />
      <MatchupAgentCard data={analysis['Matchup Agent']} />
      <RiskAgentCard data={analysis['Risk Agent']} />
    </div>
  );
}
