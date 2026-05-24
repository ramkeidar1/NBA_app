import { describe, it, expect } from 'vitest';
import { gameKey } from '../components/dashboard/DashboardPage';
import type { GameData } from '../types/game';

function makeGame(homeId: string, awayId: string): GameData {
  return {
    Time: '2026-05-24T19:00:00Z',
    'Home team': { id: homeId, name: `${homeId} Team`, record: '40-20', odds: '-110' },
    'Away team': { id: awayId, name: `${awayId} Team`, record: '35-25', odds: '+100' },
  };
}

describe('gameKey', () => {
  it('formats home_away from team ids', () => {
    expect(gameKey(makeGame('LAL', 'GSW'))).toBe('LAL_GSW');
  });

  it('uses ids not names so spaces in names do not affect the key', () => {
    const game: GameData = {
      Time: '2026-05-24T19:00:00Z',
      'Home team': { id: 'BOS', name: 'Boston Celtics', record: '50-10', odds: '-150' },
      'Away team': { id: 'MIA', name: 'Miami Heat',     record: '30-30', odds: '+130' },
    };
    expect(gameKey(game)).toBe('BOS_MIA');
  });
});
