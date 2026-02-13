"use client";

interface Point {
  label: string;
  value: number;
}

interface Props {
  points: Point[];
}

export function TrendChart({ points }: Props) {
  if (points.length === 0) {
    return <div className="chart-empty">No trend data yet.</div>;
  }

  const max = Math.max(...points.map((p) => p.value), 0.01);

  return (
    <div className="trend-grid">
      {points.map((point) => {
        const height = `${Math.round((point.value / max) * 100)}%`;
        return (
          <div key={point.label} className="trend-col">
            <span className="trend-bar-wrap">
              <span className="trend-bar" style={{ height }} />
            </span>
            <span className="trend-label">{point.label}</span>
          </div>
        );
      })}
    </div>
  );
}
