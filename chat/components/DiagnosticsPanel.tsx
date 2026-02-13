"use client";

import { useMemo } from "react";
import { CategoryExplain } from "@/components/CategoryExplain";
import { CategoryBarChart } from "@/components/charts/CategoryBarChart";
import { TrendChart } from "@/components/charts/TrendChart";
import type { EvalState, RiskCategory } from "@/lib/types";

interface Props {
  evalState: EvalState;
  selectedCategory: RiskCategory;
  onCategorySelect: (category: RiskCategory) => void;
}

export function DiagnosticsPanel({
  evalState,
  selectedCategory,
  onCategorySelect
}: Props) {
  const latest = evalState.latest;

  const trend = useMemo(() => {
    return evalState.turns.map((turn, idx) => ({
      label: `T${idx + 1}`,
      value: turn.overallRisk
    }));
  }, [evalState.turns]);

  const selectedScore = latest?.scores.find(
    (item) => item.category === selectedCategory
  );
  const selectedReason = latest?.reasons.find(
    (item) => item.category === selectedCategory
  );

  return (
    <aside className="diag-panel">
      <div className="diag-section">
        <h2>Live diagnostics</h2>
        <p>
          Baseline comparison and risk drift for the latest conversation turn.
        </p>
      </div>

      <div className="diag-section">
        <h3>Overall risk trend</h3>
        <TrendChart points={trend} />
      </div>

      <div className="diag-section">
        <h3>Category scores</h3>
        {latest ? (
          <CategoryBarChart
            scores={latest.scores}
            onSelect={onCategorySelect}
          />
        ) : (
          <p>No evaluation yet.</p>
        )}
      </div>

      <div className="diag-section">
        <h3>Why this category?</h3>
        <CategoryExplain
          category={selectedCategory}
          score={selectedScore}
          reason={selectedReason}
        />
      </div>
    </aside>
  );
}
