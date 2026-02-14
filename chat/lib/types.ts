export type Role = "user" | "assistant";

export type Principle =
  | "respect_attention"
  | "meaningful_choices"
  | "transparency_honesty"
  | "support_wellbeing"
  | "privacy_data_rights"
  | "fairness_non_discrimination"
  | "accountability"
  | "long_term_societal_impact";

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  timestamp: number;
}

export interface PrincipleScore {
  principle: Principle;
  score: number;
  confidence: number;
}

export interface PrincipleReason {
  principle: Principle;
  headline: string;
  rationale: string;
  evidence: string[];
}

export interface EvalTurn {
  turnId: string;
  messageId: string;
  scores: PrincipleScore[];
  reasons: PrincipleReason[];
  overallScore: number;
}

export interface EvalState {
  turns: EvalTurn[];
  latest: EvalTurn | null;
}

export interface ChatProvider {
  sendMessage(input: string, history: ChatMessage[]): Promise<string>;
}

export interface EvalApiPayload {
  scores: PrincipleScore[];
  reasons: PrincipleReason[];
  overallScore: number;
}

export interface ChatEvalApiResponse {
  assistantReply: string;
  eval: EvalApiPayload;
  tracking: {
    casualTone: number;
    toneLabel: "casual" | "neutral";
  };
}
