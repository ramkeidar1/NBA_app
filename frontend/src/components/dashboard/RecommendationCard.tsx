import type { OrchestratorRecommendation, RiskLevel } from '../../types/recommendation';

function teamLogoPath(name: string): string {
  return `/icons/${name}.png`;
}

function formatMatchupName(raw: string): string {
  return raw.replace(/_/g, ' ').replace(' vs ', ' vs ');
}

function formatTeamName(raw: string): string {
  return raw.replace(/_/g, ' ');
}

const RISK_LABELS: Record<RiskLevel, string> = {
  low: 'LOW RISK',
  medium: 'MEDIUM RISK',
  high: 'HIGH RISK',
};

interface ConfidenceBarProps {
  value: number;
}

function ConfidenceBar({ value }: ConfidenceBarProps) {
  const pct = Math.round(value * 100);
  return (
    <div className="rc-confidence-wrap">
      <div className="rc-confidence-header">
        <span className="rc-confidence-label">Confidence</span>
        <span className="rc-confidence-pct">{pct}%</span>
      </div>
      <div className="rc-confidence-track">
        <div className="rc-confidence-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

interface RiskBadgeProps {
  level: RiskLevel;
}

function RiskBadge({ level }: RiskBadgeProps) {
  return (
    <span className={`rc-risk-badge rc-risk-badge--${level}`}>
      {RISK_LABELS[level]}
    </span>
  );
}

interface RecommendationCardProps {
  rec: OrchestratorRecommendation;
}

export default function RecommendationCard({ rec }: RecommendationCardProps) {
  return (
    <div className={`rec-card rec-card--${rec.riskLevel}`}>

      {/* Header: matchup + winner */}
      <div className="rc-header">
        <div className="rc-matchup-name">{formatMatchupName(rec.name)}</div>
        <div className="rc-winner-row">
          <img
            className="rc-winner-logo"
            src={teamLogoPath(rec.winnerTeam)}
            alt={rec.winnerTeam}
          />
          <div className="rc-winner-info">
            <span className="rc-winner-label">Predicted Winner</span>
            <span className="rc-winner-name">{formatTeamName(rec.winnerTeam)}</span>
          </div>
          <RiskBadge level={rec.riskLevel} />
        </div>
      </div>

      {/* Metrics row */}
      <div className="rc-metrics">
        <div className="rc-metric rc-metric--ev">
          <span className="rc-metric-value">+{rec.expectedValue.toFixed(2)}</span>
          <span className="rc-metric-label">Exp. Value</span>
        </div>
        <div className="rc-metric-divider" />
        <div className="rc-metric rc-metric--spread">
          <span className="rc-metric-value">{rec.difference > 0 ? '+' : ''}{rec.difference}</span>
          <span className="rc-metric-label">Pt Spread</span>
        </div>
        <div className="rc-metric-divider" />
        <div className="rc-metric">
          <span className="rc-metric-value">{Math.round(rec.confidence * 100)}%</span>
          <span className="rc-metric-label">Confidence</span>
        </div>
      </div>

      {/* Confidence bar */}
      <ConfidenceBar value={rec.confidence} />

      {/* AI Summary */}
      <div className="rc-summary">
        <div className="rc-summary-tag">AI Analysis</div>
        <p className="rc-summary-text">{rec.aiSummary}</p>
      </div>

    </div>
  );
}
