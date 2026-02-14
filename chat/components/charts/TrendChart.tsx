"use client";

interface Point {
  label: string;
  value: number;
}

interface Props {
  points: Point[];
}

function scoreColor(score: number): string {
  if (score >= 0.75) return "#4ade80"; // green
  if (score >= 0.25) return "#facc15"; // yellow
  if (score >= -0.25) return "#fb923c"; // orange
  return "#f87171"; // red
}

export function TrendChart({ points }: Props) {
  if (points.length === 0) {
    return <div className="chart-empty">No trend data yet.</div>;
  }

  return (
    <div className="trend-grid">
      {points.map((point) => {
        const height = `${Math.round(((point.value + 1) / 2) * 100)}%`;
        const color = scoreColor(point.value);
        return (
          <div key={point.label} className="trend-col">
            <span className="trend-bar-wrap">
              <span className="trend-bar" style={{ height, background: color }} />
            </span>
            <span className="trend-label">{point.label}</span>
          </div>
        );
      })}
    </div>
  );
}
