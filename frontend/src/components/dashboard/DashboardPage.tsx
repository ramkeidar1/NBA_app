import { useEffect, useRef, useState } from 'react';
import { postCommand, openAnalysisStream, fetchCachedPrediction } from '../../services/api';
import type { GameData } from '../../types/game';
import type { GameAgentAnalysis } from '../../types/analysis';
import type { OrchestratorRecommendation, RiskLevel } from '../../types/recommendation';
import type { FinalPredictionJSON, FormEvalJSON, MatchupEvalJSON, OddsRiskEvalJSON, AgentUpdateState } from '../../types/prediction';
import { useGames } from '../../hooks/useGames';
import { usePredictionsStream } from '../../hooks/usePredictionsStream';
import { useAgentAnalysisStream } from '../../hooks/useAgentAnalysisStream';
import GameCard from './GameCard';
import SpecificGamePanel from './SpecificGamePanel';
import AIRecommendationPanel from './AIRecommendationPanel';
import AgentAnalysisPanel from './AgentAnalysisPanel';
import PlaceBetPanel from './PlaceBetPanel';

function gameKey(game: GameData): string {
  return `${game['Home team'].id}_${game['Away team'].id}`;
}

function gameLookupName(game: GameData): string {
  return `${game['Home team'].name.replace(/ /g, '_')} vs ${game['Away team'].name.replace(/ /g, '_')}`;
}

function findRecommendation(game: GameData, recommendations: OrchestratorRecommendation[]): OrchestratorRecommendation | null {
  return recommendations.find((r) => r.name === gameLookupName(game)) ?? null;
}

function findAgentAnalysis(game: GameData, analyses: GameAgentAnalysis[]): GameAgentAnalysis | null {
  return analyses.find((a) => a.name === gameLookupName(game)) ?? null;
}

function predictionToRecommendation(game: GameData, p: FinalPredictionJSON): OrchestratorRecommendation {
  return {
    name: gameLookupName(game),
    winnerTeam: p.predicted_winner_id,
    difference: 0,
    confidence: p.confidence,
    expectedValue: p.odds_risk_report.winner_odds - 1,
    riskLevel: p.risk_rating.toLowerCase() as RiskLevel,
    aiSummary: p.reasoning_narrative,
  };
}

function predictionToAgentAnalysis(game: GameData, p: FinalPredictionJSON): GameAgentAnalysis {
  return {
    name: gameLookupName(game),
    'Form Agent': {
      'Expected winner Form': p.form_report.winner_form,
      'Expected losser Form': p.form_report.loser_form,
      Addons: p.form_report.key_context,
      Certainty: Math.round(p.form_report.confidence * 100),
    },
    'Matchup Agent': {
      'Expected winner Form': p.matchup_report.last_match,
      'Expected losser Form': p.matchup_report.net_differential,
      'Deferntial net': p.matchup_report.net_differential,
      'Intersting Matchups': p.matchup_report.last_ten_matches,
      Certainty: Math.round(p.matchup_report.confidence * 100),
    },
    'Risk Agent': {
      Addons: p.odds_risk_report.key_context,
      Certainty: Math.round(p.odds_risk_report.confidence * 100),
    },
  };
}


function agentUpdatesToGameAgentAnalysis(game: GameData, updates: AgentUpdateState): GameAgentAnalysis {
  const { form_home, form_away, matchup, odds_risk } = updates;
  const home = game['Home team'];

  const homeWins = matchup?.h2h_last_10.filter(g => g.winner_team_id === home.id).length ?? 0;
  const total = matchup?.h2h_last_10.length ?? 1;
  const netDiff = matchup
    ? matchup.h2h_last_10.reduce((sum, g) => {
        const margin = g.home_team_id === home.id ? g.home_score - g.away_score : g.away_score - g.home_score;
        return sum + margin;
      }, 0) / total
    : 0;

  const injuryLines = odds_risk
    ? odds_risk.injury_report.map(e => `${e.player_name} (${e.team_id}): ${e.status}`)
    : ['No injury data yet'];

  return {
    name: gameLookupName(game),
    'Form Agent': {
      'Expected winner Form': form_home ? `${form_home.record} | L10: ${form_home.last_10_record}` : '—',
      'Expected losser Form': form_away ? `${form_away.record} | L10: ${form_away.last_10_record}` : '—',
      Addons: form_home ? `OffRtg ${form_home.last_10_offensive_rating} | DefRtg ${form_home.last_10_defensive_rating}` : '—',
      Certainty: form_home ? Math.round(Math.min(100, Math.max(0, (form_home.last_10_rating_differential + 15) / 30 * 100))) : 0,
    },
    'Matchup Agent': {
      'Expected winner Form': matchup ? `${matchup.last_h2h.home_team_id} ${matchup.last_h2h.home_score}–${matchup.last_h2h.away_score} (${matchup.last_h2h.date})` : '—',
      'Expected losser Form': matchup ? `${home.id} ${homeWins}–${total - homeWins} last ${total}` : '—',
      'Deferntial net': matchup ? `${home.id} ${netDiff >= 0 ? '+' : ''}${netDiff.toFixed(1)} avg` : '—',
      'Intersting Matchups': matchup ? `${total} H2H games on record` : '—',
      Certainty: matchup ? Math.round((homeWins / total) * 100) : 0,
    },
    'Risk Agent': {
      Addons: injuryLines,
      Certainty: odds_risk ? Math.round(odds_risk.market_implied_probability_home * 100) : 0,
    },
  };
}

export default function DashboardPage() {
  const { games, loading, error } = useGames();
  const { recommendations, loading: recsLoading, error: recsError } = usePredictionsStream();
  const { analyses, loading: analysisLoading, error: analysisError } = useAgentAnalysisStream();
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [pipelineResults, setPipelineResults] = useState<Record<string, FinalPredictionJSON>>({});
  const [agentUpdatesByGame, setAgentUpdatesByGame] = useState<Record<string, AgentUpdateState>>({});
  const analysisStreamRef = useRef<EventSource | null>(null);

  useEffect(() => {
    return () => {
      analysisStreamRef.current?.close();
    };
  }, []);

  useEffect(() => {
    if (selectedIndex === null) return;
    const game = games[selectedIndex];
    if (!game) return;
    const key = gameKey(game);
    if (pipelineResults[key]) return;

    const controller = new AbortController();
    fetchCachedPrediction(key, controller.signal)
      .then((prediction) => {
        setPipelineResults((prev) => ({ ...prev, [key]: prediction }));
      })
      .catch((err: unknown) => {
        if (err instanceof Error && err.name === 'AbortError') return;
        if (err instanceof Error && err.message.includes('404')) {
          triggerPipeline(key, 'soft');
          return;
        }
        console.error('[fetchCachedPrediction]', err);
      });

    return () => controller.abort();
  }, [selectedIndex, games]);

  function triggerPipeline(game_id: string, mode: 'soft' | 'hard') {
    analysisStreamRef.current?.close();
    postCommand(game_id, 'GetFullPredictionData', mode)
      .then((res) => {
        if (res.stream_url) {
          const es = openAnalysisStream(game_id, mode);
          analysisStreamRef.current = es;
          es.addEventListener('agent_update', (e) => {
            console.log('[agent_update]', e.data);
            try {
              const { agent, data } = JSON.parse(e.data) as { agent: string; data: unknown };
              setAgentUpdatesByGame(prev => {
                const current = prev[game_id] ?? {};
                if (agent === 'form_workflow_home') return { ...prev, [game_id]: { ...current, form_home: data as FormEvalJSON } };
                if (agent === 'form_workflow_away') return { ...prev, [game_id]: { ...current, form_away: data as FormEvalJSON } };
                if (agent === 'matchup_workflow')   return { ...prev, [game_id]: { ...current, matchup: data as MatchupEvalJSON } };
                if (agent === 'odds_risk_workflow') return { ...prev, [game_id]: { ...current, odds_risk: data as OddsRiskEvalJSON } };
                return prev;
              });
            } catch {
              console.error('[agent_update] failed to parse', e.data);
            }
          });
          es.addEventListener('agent_error',  (e) => console.error('[agent_error]', e.data));
          es.addEventListener('status', (e) => console.log('[status]', e.data));
          es.addEventListener('final_prediction', (e) => {
            console.log('[final_prediction]', e.data);
            try {
              const prediction = JSON.parse(e.data) as FinalPredictionJSON;
              setPipelineResults((prev) => ({ ...prev, [prediction.game_id]: prediction }));
            } catch {
              console.error('[final_prediction] failed to parse', e.data);
            }
          });
          es.addEventListener('done', () => { es.close(); analysisStreamRef.current = null; });
          es.onerror = () => { console.error('Analysis stream error'); es.close(); };
        }
      })
      .catch((err: unknown) => console.error('[postCommand]', err));
  }

  const selectedGame = selectedIndex !== null ? games[selectedIndex] : null;
  const selectedGameKey = selectedGame ? gameKey(selectedGame) : null;
  const selectedPipeline = selectedGameKey ? pipelineResults[selectedGameKey] ?? null : null;

  const selectedAgentUpdates = selectedGameKey ? agentUpdatesByGame[selectedGameKey] ?? null : null;

  const selectedRec = selectedGame && selectedPipeline
    ? predictionToRecommendation(selectedGame, selectedPipeline)
    : null;

  const selectedAnalysis = selectedGame
    ? (selectedPipeline
        ? predictionToAgentAnalysis(selectedGame, selectedPipeline)
        : selectedAgentUpdates
          ? agentUpdatesToGameAgentAnalysis(selectedGame, selectedAgentUpdates)
          : null)
    : null;

  return (
    <div className="dashboard">
      <div className="panel panel--top">
        <div className="panel-header">
          <span className="tab-index">1</span>
          <span className="panel-title">NBA Games Today</span>
        </div>
        <div className={loading || error ? 'panel-body' : 'panel-body panel-body--scroll'}>
          {loading && (
            <div className="sg-empty">
              <span className="sg-empty-text">Loading games…</span>
            </div>
          )}
          {error && (
            <div className="sg-empty">
              <span className="sg-empty-text" style={{ color: 'var(--risk-high)' }}>
                {error}
              </span>
            </div>
          )}
          {!loading && !error && games.map((game, i) => (
            <GameCard
              key={gameKey(game)}
              game={game}
              isSelected={selectedIndex === i}
              onClick={() => setSelectedIndex(selectedIndex === i ? null : i)}
              onRefresh={(mode) => triggerPipeline(gameKey(game), mode)}
            />
          ))}
        </div>
      </div>

      <div className="panels-row">
        <div className="panel">
          <div className="panel-header">
            <span className="tab-index">2</span>
            <span className="panel-title">Specific Game</span>
          </div>
          <div className="panel-body">
            <SpecificGamePanel game={selectedGame} />
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <span className="tab-index">3</span>
            <span className="panel-title">AI Recommendation</span>
          </div>
          <div className="panel-body panel-body--overflow">
            {recsLoading && (
              <div className="sg-empty">
                <span className="sg-empty-text">Loading predictions…</span>
              </div>
            )}
            {!recsLoading && recsError && (
              <div className="sg-empty">
                <span className="sg-empty-text" style={{ color: 'var(--risk-high)' }}>
                  {recsError}
                </span>
              </div>
            )}
            {!recsLoading && !recsError && (
              <AIRecommendationPanel recommendation={selectedRec} />
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <span className="tab-index">4</span>
            <span className="panel-title">Agent Analysis</span>
          </div>
          <div className="panel-body panel-body--overflow">
            {analysisLoading && (
              <div className="sg-empty">
                <span className="sg-empty-text">Loading agent analysis…</span>
              </div>
            )}
            {!analysisLoading && analysisError && (
              <div className="sg-empty">
                <span className="sg-empty-text" style={{ color: 'var(--risk-high)' }}>
                  {analysisError}
                </span>
              </div>
            )}
            {!analysisLoading && !analysisError && (
              <AgentAnalysisPanel analysis={selectedAnalysis} />
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <span className="tab-index">5</span>
            <span className="panel-title">Place Bet</span>
          </div>
          <div className="panel-body panel-body--overflow">
            <PlaceBetPanel recommendation={selectedRec} />
          </div>
        </div>
      </div>
    </div>
  );
}