import type { GameData, TeamProfile } from '../../types/game';
import { useTeamProfiles } from '../../hooks/useTeamProfiles';

interface StatRowProps {
  label: string;
  value: string | number;
}

function StatRow({ label, value }: StatRowProps) {
  return (
    <div className="sg-stat-row">
      <span className="sg-stat-label">{label}</span>
      <span className="sg-stat-value">{value}</span>
    </div>
  );
}

interface TeamColumnProps {
  teamId: string;
  teamName: string;
  side: 'home' | 'away';
  profile: TeamProfile | null;
}

function TeamColumn({ teamId, teamName, side, profile }: TeamColumnProps) {
  return (
    <div className={`sg-team-col sg-team-col--${side}`}>
      <div className="sg-team-header">
        <img
          className="sg-logo"
          src={`/icons/${teamId}.png`}
          alt={teamName}
        />
        <div className="sg-team-title">
          <span className="sg-team-name">{teamName}</span>
          <span className="sg-side-label">{side === 'home' ? 'Home' : 'Away'}</span>
        </div>
      </div>

      {profile ? (
        <div className="sg-stats">
          <StatRow label="Conference" value={profile.conference} />
          <StatRow label="Division" value={profile.division} />
          <StatRow label="Home Court" value={profile.home_court_name} />
          <StatRow label="Seed" value={`${profile.seed}`} />
          <StatRow label="Record" value={profile.record} />
          <StatRow label="Off. Rating" value={profile.offensive_rating} />
          <StatRow label="Def. Rating" value={profile.defensive_rating} />
          <StatRow label="Star Player" value={profile.star_player} />
        </div>
      ) : (
        <div className="sg-no-profile">No profile available</div>
      )}
    </div>
  );
}

interface SpecificGamePanelProps {
  game: GameData | null;
}

export default function SpecificGamePanel({ game }: SpecificGamePanelProps) {
  const home = game ? game['Home team'] : null;
  const away = game ? game['Away team'] : null;

  const { home: homeProfile, away: awayProfile, loading, error } = useTeamProfiles(
    home?.id ?? null,
    away?.id ?? null,
  );

  if (!game) {
    return (
      <div className="sg-empty">
        <span className="sg-empty-text">Select a game to view details</span>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="sg-empty">
        <span className="sg-empty-text">Loading team profiles…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="sg-empty">
        <span className="sg-empty-text" style={{ color: 'var(--risk-high)' }}>{error}</span>
      </div>
    );
  }

  return (
    <div className="sg-panel">
      <TeamColumn teamId={home!.id} teamName={home!.name} side="home" profile={homeProfile} />
      <div className="sg-divider" />
      <TeamColumn teamId={away!.id} teamName={away!.name} side="away" profile={awayProfile} />
    </div>
  );
}
