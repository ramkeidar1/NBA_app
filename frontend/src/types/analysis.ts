export interface FormAgentData {
  'Expected winner Form': string;
  'Expected losser Form': string;
  Addons: string;
  Certainty: number;
}

export interface MatchupAgentData {
  'Expected winner Form': string;
  'Expected losser Form': string;
  'Deferntial net': string;
  'Intersting Matchups': string;
  Certainty: number;
}

export interface RiskAgentData {
  Addons: string[];
  Certainty: number;
}

export interface GameAgentAnalysis {
  'Form Agent': FormAgentData;
  'Matchup Agent': MatchupAgentData;
  'Risk Agent': RiskAgentData;
}

export type AgentAnalysisMap = Record<string, GameAgentAnalysis>;
