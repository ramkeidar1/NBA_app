import type { GameData } from '../../types/game';

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

interface TeamRowProps {
  id: string;
  name: string;
  record: string;
  odds: string;
  side: 'home' | 'away';
}

function TeamRow({ id, name, record, odds, side }: TeamRowProps) {
  return (
    <div className={`game-card__team game-card__team--${side}`}>
      <img
        className="game-card__logo"
        src={`/icons/${id}.png`}
        alt={name}
      />
      <div className="game-card__team-info">
        <span className="game-card__team-name">{name}</span>
        <span className="game-card__record">{record}</span>
      </div>
      <span className="game-card__odds">{odds}</span>
    </div>
  );
}

interface GameCardProps {
  game: GameData;
  isSelected: boolean;
  onClick: () => void;
  onRefresh: () => void;
}

export default function GameCard({ game, isSelected, onClick, onRefresh }: GameCardProps) {
  const home = game['Home team'];
  const away = game['Away team'];

  return (
    <div
      className={`game-card${isSelected ? ' game-card--selected' : ''}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      <div className="game-card__header">
        <div className="game-card__time">{formatTime(game.Time)}</div>
        <button
          className="game-card__refresh"
          onClick={(e) => { e.stopPropagation(); onRefresh(); }}
          title="Run pipeline"
          aria-label="Run pipeline"
        >
          ↻
        </button>
      </div>
      <div className="game-card__matchup">
        <TeamRow id={home.id} name={home.name} record={home.record} odds={home.odds} side="home" />
        <div className="game-card__vs">VS</div>
        <TeamRow id={away.id} name={away.name} record={away.record} odds={away.odds} side="away" />
      </div>
    </div>
  );
}
