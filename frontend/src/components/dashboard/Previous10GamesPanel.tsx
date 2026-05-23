import { useEffect, useRef, useState } from 'react';
import type { H2HGame } from '../../types/prediction';

interface Previous10GamesPanelProps {
  games: H2HGame[];
  homeTeamId: string;
  awayTeamId: string;
}

const SVG_H = 120;
const PADDING = { top: 20, right: 16, bottom: 24, left: 36 };
const SIDE_LEGEND_W = 42; // legend column + gap

function formatDate(iso: string): string {
  const d = new Date(iso);
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  return `${dd}/${mm}`;
}

export default function Previous10GamesPanel({ games, homeTeamId, awayTeamId }: Previous10GamesPanelProps) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [wrapWidth, setWrapWidth] = useState(0);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver(entries => {
      setWrapWidth(entries[0].contentRect.width);
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  if (games.length === 0) {
    return (
      <div className="h2h-empty">
        <span className="sg-empty-text">Select a game and run analysis to see H2H history</span>
      </div>
    );
  }

  const sorted = [...games].sort((a, b) => a.date.localeCompare(b.date));

  const allScores = sorted.flatMap(g => [g.home_score, g.away_score]);
  const maxScore = Math.max(...allScores);
  const minScore = Math.min(...allScores);
  const yPad = Math.ceil((maxScore - minScore) * 0.12) || 5;
  const yMax = maxScore + yPad;
  const yMin = Math.max(0, minScore - yPad);

  const n = sorted.length;
  const svgW = Math.max(100, wrapWidth - SIDE_LEGEND_W);
  const plotW = Math.max(60, svgW - PADDING.left - PADDING.right);
  const plotH = SVG_H;
  const chartH = plotH + PADDING.top + PADDING.bottom;

  function xPos(i: number): number {
    return PADDING.left + (n === 1 ? plotW / 2 : (i / (n - 1)) * plotW);
  }

  function yPos(score: number): number {
    return PADDING.top + plotH - ((score - yMin) / (yMax - yMin)) * plotH;
  }

  const homePoints = sorted.map((g, i) => {
    const score = g.home_team_id === homeTeamId ? g.home_score : g.away_score;
    return { x: xPos(i), y: yPos(score), score, won: g.winner_team_id === homeTeamId };
  });

  const awayPoints = sorted.map((g, i) => {
    const score = g.home_team_id === awayTeamId ? g.home_score : g.away_score;
    return { x: xPos(i), y: yPos(score), score, won: g.winner_team_id === awayTeamId };
  });

  const toPolyline = (pts: { x: number; y: number }[]) =>
    pts.map(p => `${p.x},${p.y}`).join(' ');

  const ticks = 4;
  const tickValues = Array.from({ length: ticks + 1 }, (_, i) =>
    Math.round(yMin + ((yMax - yMin) * i) / ticks)
  );

  return (
    <div className="h2h-chart-wrap" ref={wrapRef}>
      <div className="h2h-side-legend">
        <div className="h2h-side-legend-item">
          <span className="h2h-side-legend-line h2h-side-legend-line--home" />
          <span className="h2h-side-legend-label">{homeTeamId}</span>
        </div>
        <div className="h2h-side-legend-item">
          <span className="h2h-side-legend-line h2h-side-legend-line--away" />
          <span className="h2h-side-legend-label">{awayTeamId}</span>
        </div>
      </div>

      {wrapWidth > 0 && (
        <svg
          width={svgW}
          height={chartH}
          className="h2h-chart"
          aria-label="Previous head-to-head games"
        >
          {/* Gridlines */}
          {tickValues.map(tick => {
            const y = yPos(tick);
            return (
              <g key={tick}>
                <line
                  x1={PADDING.left}
                  x2={PADDING.left + plotW}
                  y1={y}
                  y2={y}
                  stroke="#252830"
                  strokeWidth={1}
                />
                <text x={PADDING.left - 6} y={y + 4} textAnchor="end" fontSize={9} fill="#4a4e62">
                  {tick}
                </text>
              </g>
            );
          })}

          {/* X-axis */}
          <line
            x1={PADDING.left}
            x2={PADDING.left + plotW}
            y1={PADDING.top + plotH}
            y2={PADDING.top + plotH}
            stroke="#252830"
            strokeWidth={1}
          />

          {/* Date labels */}
          {sorted.map((game, i) => (
            <text
              key={`date-${i}`}
              x={xPos(i)}
              y={PADDING.top + plotH + 14}
              textAnchor="middle"
              fontSize={8}
              fill="#4a4e62"
            >
              {formatDate(game.date)}
            </text>
          ))}

          {/* Home line */}
          <polyline
            points={toPolyline(homePoints)}
            fill="none"
            stroke="#6366f1"
            strokeWidth={2}
            strokeLinejoin="round"
            strokeLinecap="round"
          />

          {/* Away line */}
          <polyline
            points={toPolyline(awayPoints)}
            fill="none"
            stroke="#f59e0b"
            strokeWidth={2}
            strokeLinejoin="round"
            strokeLinecap="round"
          />

          {/* Home dots + labels */}
          {homePoints.map((pt, i) => (
            <g key={`home-${i}`}>
              <circle
                cx={pt.x}
                cy={pt.y}
                r={pt.won ? 5 : 3.5}
                fill={pt.won ? '#6366f1' : '#1a1d27'}
                stroke="#6366f1"
                strokeWidth={1.5}
              />
              <text
                x={pt.x}
                y={pt.y - (pt.won ? 12 : 9)}
                textAnchor="middle"
                fontSize={8}
                fill="#6366f1"
              >
                {pt.score}
              </text>
            </g>
          ))}

          {/* Away dots + labels */}
          {awayPoints.map((pt, i) => (
            <g key={`away-${i}`}>
              <circle
                cx={pt.x}
                cy={pt.y}
                r={pt.won ? 5 : 3.5}
                fill={pt.won ? '#f59e0b' : '#1a1d27'}
                stroke="#f59e0b"
                strokeWidth={1.5}
              />
              <text
                x={pt.x}
                y={pt.y - (pt.won ? 12 : 9)}
                textAnchor="middle"
                fontSize={8}
                fill="#f59e0b"
              >
                {pt.score}
              </text>
            </g>
          ))}
        </svg>
      )}
    </div>
  );
}
