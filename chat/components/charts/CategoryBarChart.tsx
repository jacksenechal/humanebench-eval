"use client";

import type { CategoryScore } from "@/lib/types";

interface Props {
  scores: CategoryScore[];
  onSelect: (category: CategoryScore["category"]) => void;
}

export function CategoryBarChart({ scores, onSelect }: Props) {
  return (
    <div className="chart">
      {scores.map((item) => {
        const width = `${Math.round(item.score * 100)}%`;
        const isRisky = item.category !== "positive" && item.delta > 0;
        return (
          <button
            key={item.category}
            className="bar-row"
            onClick={() => onSelect(item.category)}
            type="button"
          >
            <span className="bar-label">{item.category}</span>
            <span className="bar-track">
              <span
                className={isRisky ? "bar-fill risk" : "bar-fill"}
                style={{ width }}
              />
            </span>
            <span className="bar-value">{item.score.toFixed(2)}</span>
          </button>
        );
      })}
    </div>
  );
}
