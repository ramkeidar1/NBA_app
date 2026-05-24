import { describe, it, expect } from 'vitest';
import { agentUpdatesToGameAgentAnalysis } from '../components/dashboard/DashboardPage';
import type { GameData } from '../types/game';
import type { AgentUpdateState } from '../types/prediction';

const game: GameData = {
  Time: '2026-05-24T19:00:00Z',
  'Home team': { id: 'LAL', name: 'Los Angeles Lakers', record: '42-18', odds: '-120' },
  'Away team': { id: 'GSW', name: 'Golden State Warriors', record: '38-22', odds: '+110' },
};

const updates: AgentUpdateState = {
  form_home: {
    game_id: 'LAL_GSW',
    team_id: 'LAL',
    team_name: 'Los Angeles Lakers',
    last_10_wins: 7,
    last_10_losses: 3,
    last_10_record: '7-3',
    home_wins: 22,
    home_losses: 8,
    home_record: '22-8',
    away_wins: 20,
    away_losses: 10,
    away_record: '20-10',
    record: '42-18',
    seed: 2,
    offensive_rating: 115,
    defensive_rating: 108,
    rating_differential: 7,
    last_10_offensive_rating: 117,
    last_10_defensive_rating: 106,
    last_10_rating_differential: 11,
    recent_game: {
      date: '2026-05-20',
      home_team_id: 'LAL',
      away_team_id: 'PHX',
      home_score: 112,
      away_score: 104,
      winner_team_id: 'LAL',
    },
  },
  form_away: {
    game_id: 'LAL_GSW',
    team_id: 'GSW',
    team_name: 'Golden State Warriors',
    last_10_wins: 5,
    last_10_losses: 5,
    last_10_record: '5-5',
    home_wins: 20,
    home_losses: 10,
    home_record: '20-10',
    away_wins: 18,
    away_losses: 12,
    away_record: '18-12',
    record: '38-22',
    seed: 4,
    offensive_rating: 112,
    defensive_rating: 110,
    rating_differential: 2,
    last_10_offensive_rating: 110,
    last_10_defensive_rating: 112,
    last_10_rating_differential: -2,
    recent_game: {
      date: '2026-05-21',
      home_team_id: 'GSW',
      away_team_id: 'SAC',
      home_score: 108,
      away_score: 115,
      winner_team_id: 'SAC',
    },
  },
  matchup: {
    game_id: 'LAL_GSW',
    h2h_last_10: [
      {
        date: '2026-03-10',
        home_team_id: 'LAL',
        away_team_id: 'GSW',
        home_score: 115,
        away_score: 108,
        winner_team_id: 'LAL',
      },
    ],
    last_h2h: {
      date: '2026-03-10',
      home_team_id: 'LAL',
      away_team_id: 'GSW',
      home_score: 115,
      away_score: 108,
      winner_team_id: 'LAL',
    },
  },
  odds_risk: {
    game_id: 'LAL_GSW',
    injury_report: [{ player_name: 'A. Davis', team_id: 'LAL', status: 'QUESTIONABLE', impact_note: 'Knee' }],
    moneyline_home: -120,
    moneyline_away: 110,
    spread: -2.5,
    over_under: 224.5,
    market_implied_probability_home: 0.55,
  },
};

describe('agentUpdatesToGameAgentAnalysis', () => {
  it('sets the game name from team names', () => {
    const result = agentUpdatesToGameAgentAnalysis(game, updates);
    expect(result.name).toBe('Los_Angeles_Lakers vs Golden_State_Warriors');
  });

  it('builds Form Agent strings from form_home data', () => {
    const result = agentUpdatesToGameAgentAnalysis(game, updates);
    expect(result['Form Agent']['Expected winner Form']).toBe('42-18 | L10: 7-3');
    expect(result['Form Agent']['Expected losser Form']).toBe('38-22 | L10: 5-5');
    expect(result['Form Agent'].Addons).toContain('OffRtg 117');
  });

  it('builds Matchup Agent strings from matchup data', () => {
    const result = agentUpdatesToGameAgentAnalysis(game, updates);
    expect(result['Matchup Agent']['Intersting Matchups']).toBe('1 H2H games on record');
    expect(result['Matchup Agent']['Deferntial net']).toContain('LAL');
  });

  it('builds Risk Agent injury lines from odds_risk', () => {
    const result = agentUpdatesToGameAgentAnalysis(game, updates);
    expect(result['Risk Agent'].Addons).toContain('A. Davis (LAL): QUESTIONABLE');
  });

  it('returns dashes when updates are empty', () => {
    const result = agentUpdatesToGameAgentAnalysis(game, {});
    expect(result['Form Agent']['Expected winner Form']).toBe('—');
    expect(result['Risk Agent'].Addons).toEqual(['No injury data yet']);
  });
});
