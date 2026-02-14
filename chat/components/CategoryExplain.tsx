"use client";

import { PRINCIPLE_LABELS, SCORE_LABELS } from "@/lib/mockData";
import type { PrincipleReason, PrincipleScore, Principle } from "@/lib/types";

interface Props {
  principle: Principle;
  score?: PrincipleScore;
  reason?: PrincipleReason;
}

export function CategoryExplain({ principle, score, reason }: Props) {
  if (!score || !reason) {
    return (
      <div className="explain-box">
        <h3>{PRINCIPLE_LABELS[principle]}</h3>
        <p>No detail available yet for this principle.</p>
      </div>
    );
  }

  const scoreLabel = SCORE_LABELS[score.score.toString()] ?? "Unknown";
  const scoreText = score.score >= 0 ? `+${score.score.toFixed(1)}` : score.score.toFixed(1);

  return (
    <div className="explain-box">
      <h3>{PRINCIPLE_LABELS[principle]}</h3>
      <p>{reason.headline}</p>
      <p>{reason.rationale}</p>
      <p>
        Score: {scoreText} ({scoreLabel}) | Confidence: {score.confidence.toFixed(2)}
      </p>
      <ul>
        {reason.evidence.map((ev, idx) => (
          <li key={idx}>{ev}</li>
        ))}
      </ul>
    </div>
  );
}
