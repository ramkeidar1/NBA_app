import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import GameCard from '../components/dashboard/GameCard';
import type { GameData } from '../types/game';

const game: GameData = {
  Time: '2026-05-24T20:30:00Z',
  'Home team': { id: 'LAL', name: 'Los Angeles Lakers', record: '42-18', odds: '-120' },
  'Away team': { id: 'GSW', name: 'Golden State Warriors', record: '38-22', odds: '+110' },
};

describe('GameCard', () => {
  it('renders both team names', () => {
    render(<GameCard game={game} isSelected={false} onClick={vi.fn()} />);
    expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
    expect(screen.getByText('Golden State Warriors')).toBeInTheDocument();
  });

  it('renders a formatted game time', () => {
    render(<GameCard game={game} isSelected={false} onClick={vi.fn()} />);
    const time = new Date(game.Time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    expect(screen.getByText(time)).toBeInTheDocument();
  });

  it('applies selected class when isSelected is true', () => {
    const { container } = render(<GameCard game={game} isSelected={true} onClick={vi.fn()} />);
    expect(container.firstChild).toHaveClass('game-card--selected');
  });

  it('does not apply selected class when isSelected is false', () => {
    const { container } = render(<GameCard game={game} isSelected={false} onClick={vi.fn()} />);
    expect(container.firstChild).not.toHaveClass('game-card--selected');
  });
});
