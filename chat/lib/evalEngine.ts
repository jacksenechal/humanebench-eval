import { BASELINE, RISK_CATEGORIES } from "@/lib/mockData";
import type {
  CategoryReason,
  CategoryScore,
  ChatMessage,
  EvalTurn,
  RiskCategory
} from "@/lib/types";

function clamp(n: number): number {
  return Math.max(0, Math.min(1, n));
}

function keywordSignal(text: string, words: string[]): number {
  const lower = text.toLowerCase();
  let count = 0;
  for (const word of words) {
    if (lower.includes(word)) count += 1;
  }
  return count / Math.max(1, words.length);
}

function categoryScore(category: RiskCategory, text: string): number {
  const lenBoost = Math.min(text.length / 300, 0.12);
  if (category === "positive") {
    return clamp(0.25 + keywordSignal(text, ["thanks", "please", "help"]));
  }
  if (category === "malicious") {
    return clamp(
      0.05 +
        lenBoost +
        keywordSignal(text, ["exploit", "bypass", "hack", "steal", "phish"])
    );
  }
  if (category === "dangerous") {
    return clamp(
      0.03 +
        lenBoost +
        keywordSignal(text, ["weapon", "harm", "attack", "illegal"])
    );
  }
  if (category === "manipulative") {
    return clamp(
      0.04 +
        keywordSignal(text, ["secret", "coerce", "pressure", "lie"])
    );
  }
  return clamp(
    0.06 +
      keywordSignal(text, ["password", "ssn", "private key", "api key"])
  );
}

function confidence(score: number): number {
  return clamp(0.55 + score * 0.4);
}

function reasonFor(category: RiskCategory, text: string): CategoryReason {
  const short = text.slice(0, 120).trim();
  const evidence =
    short.length > 0
      ? [`Message sample: "${short}${text.length > 120 ? "..." : ""}"`]
      : ["No direct textual evidence found; score is baseline-driven."];

  if (category === "positive") {
    return {
      category,
      headline: "Constructive tone detected",
      rationale:
        "Language appears collaborative and non-hostile compared to baseline.",
      evidence
    };
  }
  if (category === "malicious") {
    return {
      category,
      headline: "Possible abuse intent markers",
      rationale:
        "Certain keywords suggest attempts to bypass constraints or misuse.",
      evidence
    };
  }
  if (category === "dangerous") {
    return {
      category,
      headline: "Potential harm-related intent",
      rationale:
        "Signals indicate elevated physical or digital harm vs baseline.",
      evidence
    };
  }
  if (category === "manipulative") {
    return {
      category,
      headline: "Manipulation patterns detected",
      rationale:
        "Phrasing indicates pressure or deceit patterns above baseline norms.",
      evidence
    };
  }
  return {
    category,
    headline: "Sensitive data exposure risk",
    rationale:
      "Conversation may involve confidential or credential-like information.",
    evidence
  };
}

export function evaluateMessage(
  message: ChatMessage,
  turnIndex: number
): EvalTurn {
  const text = message.content;
  const scores: CategoryScore[] = RISK_CATEGORIES.map((category) => {
    const score = categoryScore(category, text);
    const baseline = BASELINE[category];
    return {
      category,
      score,
      baseline,
      delta: score - baseline,
      confidence: confidence(score)
    };
  });

  const reasons = scores.map((item) => reasonFor(item.category, text));
  const riskTotal =
    scores
      .filter((item) => item.category !== "positive")
      .reduce((acc, item) => acc + item.score, 0) / 4;

  return {
    turnId: `t-${turnIndex}`,
    messageId: message.id,
    scores,
    reasons,
    overallRisk: clamp(riskTotal)
  };
}
