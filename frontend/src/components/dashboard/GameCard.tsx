import type { GameData } from '../../types/game';

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

interface TeamRowProps {
  id: string;
  name: string;
  side: 'home' | 'away';
}

function TeamRow({ id, name, side }: TeamRowProps) {
  return (
    <div className={`game-card__team game-card__team--${side}`}>
      <img
        className="game-card__logo"
        src={`/icons/${id}.png`}
        alt={name}
      />
      <div className="game-card__team-info">
        <span className="game-card__team-name">{name}</span>
      </div>
    </div>
  );
}

interface GameCardProps {
  game: GameData;
  isSelected: boolean;
  onClick: () => void;
}

export default function GameCard({ game, isSelected, onClick }: GameCardProps) {
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
      </div>
      <div className="game-card__matchup">
        <TeamRow id={home.id} name={home.name} side="home" />
        <div className="game-card__vs">VS</div>
        <TeamRow id={away.id} name={away.name} side="away" />
      </div>
    </div>
  );
}
