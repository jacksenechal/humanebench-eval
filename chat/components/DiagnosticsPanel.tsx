"use client";

import { useMemo } from "react";
import { CategoryExplain } from "@/components/CategoryExplain";
import { CategoryBarChart } from "@/components/charts/CategoryBarChart";
import { TrendChart } from "@/components/charts/TrendChart";
import type { EvalState, Principle } from "@/lib/types";

interface Props {
  evalState: EvalState;
  selectedPrinciple: Principle;
  onPrincipleSelect: (principle: Principle) => void;
}

export function DiagnosticsPanel({
  evalState,
  selectedPrinciple,
  onPrincipleSelect
}: Props) {
  const latest = evalState.latest;

  const trend = useMemo(() => {
    return evalState.turns.map((turn, idx) => ({
      label: `T${idx + 1}`,
      value: turn.overallScore
    }));
  }, [evalState.turns]);

  const selectedScore = latest?.scores.find(
    (item) => item.principle === selectedPrinciple
  );
  const selectedReason = latest?.reasons.find(
    (item) => item.principle === selectedPrinciple
  );

  return (
    <aside className="diag-panel">
      <div className="diag-section">
        <h2>Humaneness evaluation</h2>
        <p>
          HumaneBench principle scores for the latest conversation turn.
        </p>
      </div>

      <div className="diag-section">
        <h3>Overall humaneness trend</h3>
        <TrendChart points={trend} />
      </div>

      <div className="diag-section">
        <h3>Principle scores</h3>
        {latest ? (
          <CategoryBarChart
            scores={latest.scores}
            onSelect={onPrincipleSelect}
          />
        ) : (
          <p>No evaluation yet.</p>
        )}
      </div>

      <div className="diag-section">
        <h3>Why this principle?</h3>
        <CategoryExplain
          principle={selectedPrinciple}
          score={selectedScore}
          reason={selectedReason}
        />
      </div>
    </aside>
  );
}
