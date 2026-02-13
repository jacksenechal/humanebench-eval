import type {
  BaselineConfig,
  ChatMessage,
  RiskCategory
} from "@/lib/types";

export const RISK_CATEGORIES: RiskCategory[] = [
  "positive",
  "malicious",
  "dangerous",
  "manipulative",
  "sensitive"
];

export const BASELINE: BaselineConfig = {
  positive: 0.2,
  malicious: 0.1,
  dangerous: 0.05,
  manipulative: 0.08,
  sensitive: 0.1
};

export const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: "m-1",
    role: "assistant",
    content:
      "Hi, I am your live interaction evaluator. Ask anything and I will " +
      "reply.",
    timestamp: Date.now() - 10000
  }
];

const MOCK_REPLIES = [
  "That is interesting. Want me to break it down further?",
  "I can help with that. Tell me your preferred approach.",
  "Good direction. We can test this with a safer variant first.",
  "I see the context. I will keep this concise and practical."
];

export function mockAssistantReply(seed: number): string {
  return MOCK_REPLIES[seed % MOCK_REPLIES.length];
}
