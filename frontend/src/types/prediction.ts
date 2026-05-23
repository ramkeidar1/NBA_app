// ─── Raw workflow agent output types (mirrors backend schemas) ───────────────

export interface H2HGame {
  date: string;
  home_team_id: string;
  away_team_id: string;
  home_score: number;
  away_score: number;
  winner_team_id: string;
}

export interface FormEvalJSON {
  game_id: string;
  team_id: string;
  team_name: string;
  last_10_wins: number;
  last_10_losses: number;
  last_10_record: string;
  home_wins: number;
  home_losses: number;
  home_record: string;
  away_wins: number;
  away_losses: number;
  away_record: string;
  record: string;
  seed: number;
  offensive_rating: number;
  defensive_rating: number;
  rating_differential: number;
  last_10_offensive_rating: number;
  last_10_defensive_rating: number;
  last_10_rating_differential: number;
  recent_game: H2HGame;
}

export interface MatchupEvalJSON {
  game_id: string;
  h2h_last_10: H2HGame[];
  last_h2h: H2HGame;
}

export interface InjuryEntry {
  player_name: string;
  team_id: string;
  status: 'OUT' | 'QUESTIONABLE' | 'AVAILABLE';
  impact_note: string;
}

export interface OddsRiskEvalJSON {
  game_id: string;
  injury_report: InjuryEntry[];
  moneyline_home: number;
  moneyline_away: number;
  spread: number;
  over_under: number;
  market_implied_probability_home: number;
}

export interface AgentUpdateState {
  form_home?: FormEvalJSON;
  form_away?: FormEvalJSON;
  matchup?: MatchupEvalJSON;
  odds_risk?: OddsRiskEvalJSON;
}

// ─── Final prediction types ───────────────────────────────────────────────────

export interface FormWorkflowJSON {
  confidence: number;
  workflow_weight: number;
  winner_form: string;
  loser_form: string;
  key_context: string;
}

export interface MatchupWorkflowJSON {
  confidence: number;
  workflow_weight: number;
  last_match: string;
  last_ten_matches: string;
  net_differential: string;
}

export interface OddsRiskWorkflowJSON {
  confidence: number;
  workflow_weight: number;
  winner_odds: number;
  key_context: string[];
}

export interface FinalPredictionJSON {
  game_id: string;
  predicted_winner_id: string;
  predicted_winner_name: string;
  confidence: number;
  risk_rating: 'LOW' | 'MEDIUM' | 'HIGH';
  reasoning_narrative: string;
  form_report: FormWorkflowJSON;
  matchup_report: MatchupWorkflowJSON;
  odds_risk_report: OddsRiskWorkflowJSON;
  signal_disagreement_flag: boolean;
  partial_telemetry: boolean;
  extended_thinking: boolean;
}
