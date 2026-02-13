export type Role = "user" | "assistant";

export type RiskCategory =
  | "positive"
  | "malicious"
  | "dangerous"
  | "manipulative"
  | "sensitive";

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  timestamp: number;
}

export interface CategoryScore {
  category: RiskCategory;
  score: number;
  baseline: number;
  delta: number;
  confidence: number;
}

export interface CategoryReason {
  category: RiskCategory;
  headline: string;
  rationale: string;
  evidence: string[];
}

export interface EvalTurn {
  turnId: string;
  messageId: string;
  scores: CategoryScore[];
  reasons: CategoryReason[];
  overallRisk: number;
}

export interface EvalState {
  turns: EvalTurn[];
  latest: EvalTurn | null;
}

export interface BaselineConfig {
  [key: string]: number;
}

export interface ChatProvider {
  sendMessage(input: string, history: ChatMessage[]): Promise<string>;
}

export interface EvalApiPayload {
  scores: CategoryScore[];
  reasons: CategoryReason[];
  overallRisk: number;
}

export interface ChatEvalApiResponse {
  assistantReply: string;
  eval: EvalApiPayload;
  tracking: {
    casualTone: number;
    toneLabel: "casual" | "neutral";
  };
}
