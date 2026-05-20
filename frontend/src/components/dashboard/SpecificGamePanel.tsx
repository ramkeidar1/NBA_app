import type { GameData, TeamProfile } from '../../types/game';
import { useTeams } from '../../hooks/useTeams';

function findTeamProfile(displayName: string, teams: TeamProfile[]): TeamProfile | undefined {
  const key = displayName.replace(/ /g, '_');
  return teams.find((t) => t.name === key);
}

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
  teamName: string;
  side: 'home' | 'away';
  teams: TeamProfile[];
}

function TeamColumn({ teamName, side, teams }: TeamColumnProps) {
  const profile = findTeamProfile(teamName, teams);

  return (
    <div className={`sg-team-col sg-team-col--${side}`}>
      <div className="sg-team-header">
        <img
          className="sg-logo"
          src={`/icons/${teamName.replace(/ /g, '_')}.png`}
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
          <StatRow label="Home Court" value={profile.homeCourtName} />
          <StatRow label="Standing" value={`${profile.standing.wins}W – ${profile.standing.losses}L · Seed #${profile.standing.seed}`} />
          <StatRow label="Off. Rating" value={profile.offensiveRating} />
          <StatRow label="Def. Rating" value={profile.defensiveRating} />
          <StatRow label="Star Player" value={profile.starPlayer} />
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
  const { teams } = useTeams();

  if (!game) {
    return (
      <div className="sg-empty">
        <span className="sg-empty-text">Select a game to view details</span>
      </div>
    );
  }

  const home = game['Home team'];
  const away = game['Away team'];

  return (
    <div className="sg-panel">
      <TeamColumn teamName={home.name} side="home" teams={teams} />
      <div className="sg-divider" />
      <TeamColumn teamName={away.name} side="away" teams={teams} />
    </div>
  );
}
