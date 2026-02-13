"use client";

import type { CategoryReason, CategoryScore, RiskCategory } from "@/lib/types";

interface Props {
  category: RiskCategory;
  score?: CategoryScore;
  reason?: CategoryReason;
}

export function CategoryExplain({ category, score, reason }: Props) {
  if (!score || !reason) {
    return (
      <div className="explain-box">
        <h3>{category}</h3>
        <p>No detail available yet for this category.</p>
      </div>
    );
  }

  return (
    <div className="explain-box">
      <h3>{category}</h3>
      <p>{reason.headline}</p>
      <p>{reason.rationale}</p>
      <p>
        Score: {score.score.toFixed(2)} | Baseline:{" "}
        {score.baseline.toFixed(2)} | Delta: {score.delta.toFixed(2)} |
        Confidence:{" "}
        {score.confidence.toFixed(2)}
      </p>
      <ul>
        {reason.evidence.map((ev) => (
          <li key={ev}>{ev}</li>
        ))}
      </ul>
    </div>
  );
}
