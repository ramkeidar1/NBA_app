import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useGames } from '../hooks/useGames';
import * as api from '../services/api';
import type { GameData } from '../types/game';

vi.mock('../services/api');

const mockGames: GameData[] = [
  {
    Time: '2026-05-24T20:30:00Z',
    'Home team': { id: 'LAL', name: 'Los Angeles Lakers', record: '42-18', odds: '-120' },
    'Away team': { id: 'GSW', name: 'Golden State Warriors', record: '38-22', odds: '+110' },
  },
];

beforeEach(() => {
  vi.resetAllMocks();
});

describe('useGames', () => {
  it('starts in loading state', () => {
    vi.mocked(api.fetchMatches).mockReturnValue(new Promise(() => {}));
    const { result } = renderHook(() => useGames());
    expect(result.current.loading).toBe(true);
    expect(result.current.games).toEqual([]);
    expect(result.current.error).toBeNull();
  });

  it('populates games and clears loading on success', async () => {
    vi.mocked(api.fetchMatches).mockResolvedValue(mockGames);
    const { result } = renderHook(() => useGames());

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.games).toEqual(mockGames);
    expect(result.current.error).toBeNull();
  });

  it('sets error and clears loading on fetch failure', async () => {
    vi.mocked(api.fetchMatches).mockRejectedValue(new Error('Network error'));
    const { result } = renderHook(() => useGames());

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.error).toBe('Network error');
    expect(result.current.games).toEqual([]);
  });
});
