import { useEffect, useRef, useState } from 'react';
import { postCommand, openAnalysisStream } from '../../services/api';
import type { GameData } from '../../types/game';
import type { GameAgentAnalysis } from '../../types/analysis';
import type { OrchestratorRecommendation } from '../../types/recommendation';
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


export default function DashboardPage() {
  const { games, loading, error } = useGames();
  const { recommendations, loading: recsLoading, error: recsError } = usePredictionsStream();
  const { analyses, loading: analysisLoading, error: analysisError } = useAgentAnalysisStream();
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const analysisStreamRef = useRef<EventSource | null>(null);

  useEffect(() => {
    return () => {
      analysisStreamRef.current?.close();
    };
  }, []);

  function triggerPipeline(game_id: string) {
    analysisStreamRef.current?.close();
    postCommand(game_id, 'GetFullPredictionData')
      .then((res) => {
        if (res.stream_url) {
          const es = openAnalysisStream(game_id);
          analysisStreamRef.current = es;
          es.addEventListener('agent_update', (e) => console.log('[agent_update]', e.data));
          es.addEventListener('agent_error',  (e) => console.error('[agent_error]', e.data));
          es.addEventListener('final_prediction', (e) => console.log('[final_prediction]', e.data));
          es.addEventListener('status', (e) => console.log('[status]', e.data));
          es.addEventListener('done', () => { es.close(); analysisStreamRef.current = null; });
          es.onerror = () => { console.error('Analysis stream error'); es.close(); };
        }
      })
      .catch((err: unknown) => console.error('[postCommand]', err));
  }

  const selectedGame = selectedIndex !== null ? games[selectedIndex] : null;
  const selectedRec = selectedGame ? findRecommendation(selectedGame, recommendations) : null;
  const selectedAnalysis = selectedGame ? findAgentAnalysis(selectedGame, analyses) : null;

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
              onClick={() => {
                setSelectedIndex(selectedIndex === i ? null : i);
                triggerPipeline(gameKey(game));
              }}
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