import React from 'react';
import type { H2HGame } from '../../types/prediction';

interface Previous10GamesPanelProps {
  games: H2HGame[];
  homeTeamId: string;
  awayTeamId: string;
}

const SVG_H = 160;
const BAR_W = 14;
const BAR_GAP = 4;
const GROUP_GAP = 20;
const PADDING = { top: 24, right: 16, bottom: 36, left: 36 };

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export default function Previous10GamesPanel({ games, homeTeamId, awayTeamId }: Previous10GamesPanelProps) {
  if (games.length === 0) {
    return (
      <div className="h2h-empty">
        <span className="sg-empty-text">Select a game and run analysis to see H2H history</span>
      </div>
    );
  }

  // Sort chronologically (oldest to newest)
  const sorted = [...games].sort((a, b) => a.date.localeCompare(b.date));

  const allScores = sorted.flatMap(g => [g.home_score, g.away_score]);
  const maxScore = Math.max(...allScores);
  const yMax = Math.ceil(maxScore * 1.12);

  const chartW =
    sorted.length * (BAR_W * 2 + BAR_GAP + GROUP_GAP) - GROUP_GAP + PADDING.left + PADDING.right;
  const chartH = SVG_H + PADDING.top + PADDING.bottom;
  const plotH = SVG_H;

  function yPos(score: number): number {
    return PADDING.top + plotH - (score / yMax) * plotH;
  }

  function barHeight(score: number): number {
    return (score / yMax) * plotH;
  }

  const ticks = [0, 0.25, 0.5, 0.75, 1].map(t => Math.round(t * yMax));

  return (
    <div className="h2h-chart-wrap">
      <svg
        width={chartW}
        height={chartH}
        className="h2h-chart"
        aria-label="Previous 10 head-to-head games"
      >
        {/* Y-axis ticks & gridlines */}
        {ticks.map(tick => {
          const y = yPos(tick);
          return (
            <g key={tick}>
              <line
                x1={PADDING.left}
                x2={chartW - PADDING.right}
                y1={y}
                y2={y}
                stroke="#252830"
                strokeWidth={1}
              />
              <text
                x={PADDING.left - 6}
                y={y + 4}
                textAnchor="end"
                fontSize={9}
                fill="#4a4e62"
              >
                {tick}
              </text>
            </g>
          );
        })}

        {/* Bars */}
        {sorted.map((game, i) => {
          const groupX = PADDING.left + i * (BAR_W * 2 + BAR_GAP + GROUP_GAP);

          // Find scores relative to the current fixture configuration
          const isHomeTeamTheHistoricalHome = game.home_team_id === homeTeamId;
          
          const targetHomeScore = isHomeTeamTheHistoricalHome ? game.home_score : game.away_score;
          const targetAwayScore = isHomeTeamTheHistoricalHome ? game.away_score : game.home_score;

          const homeWon = game.winner_team_id === homeTeamId;
          const awayWon = game.winner_team_id === awayTeamId;

          const leftX = groupX;
          const rightX = groupX + BAR_W + BAR_GAP;

          return (
            <g key={`${game.date}-${i}`}>
              {/* Home team bar (Left side of group - Consistent color) */}
              <rect
                x={leftX}
                y={yPos(targetHomeScore)}
                width={BAR_W}
                height={barHeight(targetHomeScore)}
                fill={homeWon ? '#6366f1' : 'rgba(99,102,241,0.35)'}
                rx={2}
              />
              {homeWon && (
                <text
                  x={leftX + BAR_W / 2}
                  y={yPos(targetHomeScore) - 5}
                  textAnchor="middle"
                  fontSize={11}
                  fill="#6366f1"
                >
                  ★
                </text>
              )}

              {/* Away team bar (Right side of group - Consistent color) */}
              <rect
                x={rightX}
                y={yPos(targetAwayScore)}
                width={BAR_W}
                height={barHeight(targetAwayScore)}
                fill={awayWon ? '#f59e0b' : 'rgba(245,158,11,0.35)'}
                rx={2}
              />
              {awayWon && (
                <text
                  x={rightX + BAR_W / 2}
                  y={yPos(targetAwayScore) - 5}
                  textAnchor="middle"
                  fontSize={11}
                  fill="#f59e0b"
                >
                  ★
                </text>
              )}

              {/* Score labels */}
              <text
                x={leftX + BAR_W / 2}
                y={yPos(targetHomeScore) - (homeWon ? 17 : 5)}
                textAnchor="middle"
                fontSize={8}
                fill="#7b7f96"
              >
                {targetHomeScore}
              </text>
              <text
                x={rightX + BAR_W / 2}
                y={yPos(targetAwayScore) - (awayWon ? 17 : 5)}
                textAnchor="middle"
                fontSize={8}
                fill="#7b7f96"
              >
                {targetAwayScore}
              </text>

              {/* Date label */}
              <text
                x={groupX + BAR_W + BAR_GAP / 2}
                y={chartH - 6}
                textAnchor="middle"
                fontSize={8}
                fill="#4a4e62"
              >
                {formatDate(game.date)}
              </text>
            </g>
          );
        })}

        {/* X axis line */}
        <line
          x1={PADDING.left}
          x2={chartW - PADDING.right}
          y1={PADDING.top + plotH}
          y2={PADDING.top + plotH}
          stroke="#252830"
          strokeWidth={1}
        />
      </svg>

      {/* Legend */}
      <div className="h2h-legend">
        <span className="h2h-legend-dot h2h-legend-dot--home" />
        <span className="h2h-legend-label">{homeTeamId} (Home)</span>
        <span className="h2h-legend-dot h2h-legend-dot--away" />
        <span className="h2h-legend-label">{awayTeamId} (Away)</span>
        <span className="h2h-legend-star">★</span>
        <span className="h2h-legend-label">Winner</span>
      </div>
    </div>
  );
}