"use client";

import { PRINCIPLE_LABELS } from "@/lib/mockData";
import type { PrincipleScore } from "@/lib/types";

interface Props {
  scores: PrincipleScore[];
  onSelect: (principle: PrincipleScore["principle"]) => void;
}

function scoreColor(score: number): string {
  if (score >= 0.75) return "#4ade80"; // green
  if (score >= 0.25) return "#facc15"; // yellow
  if (score >= -0.25) return "#fb923c"; // orange
  return "#f87171"; // red
}

export function CategoryBarChart({ scores, onSelect }: Props) {
  return (
    <div className="chart">
      {scores.map((item) => {
        const width = `${Math.round(((item.score + 1) / 2) * 100)}%`;
        const color = scoreColor(item.score);
        const label = item.score >= 0 ? `+${item.score.toFixed(1)}` : item.score.toFixed(1);
        return (
          <button
            key={item.principle}
            className="bar-row"
            onClick={() => onSelect(item.principle)}
            type="button"
          >
            <span className="bar-label">{PRINCIPLE_LABELS[item.principle]}</span>
            <span className="bar-track">
              <span
                className="bar-fill"
                style={{ width, background: color }}
              />
            </span>
            <span className="bar-value">{label}</span>
          </button>
        );
      })}
    </div>
  );
}
