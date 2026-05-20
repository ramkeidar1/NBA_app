export type RiskLevel = 'low' | 'medium' | 'high';

export interface OrchestratorRecommendation {
  name: string;
  winnerTeam: string;
  difference: number;
  confidence: number;
  expectedValue: number;
  riskLevel: RiskLevel;
  aiSummary: string;
}
