import type { ChatMessage, Principle } from "@/lib/types";

export const PRINCIPLES: Principle[] = [
  "respect_attention",
  "meaningful_choices",
  "transparency_honesty",
  "support_wellbeing",
  "privacy_data_rights",
  "fairness_non_discrimination",
  "accountability",
  "long_term_societal_impact"
];

export const PRINCIPLE_LABELS: Record<Principle, string> = {
  respect_attention: "Respect Attention",
  meaningful_choices: "Meaningful Choices",
  transparency_honesty: "Transparency & Honesty",
  support_wellbeing: "Support Well-being",
  privacy_data_rights: "Privacy & Data Rights",
  fairness_non_discrimination: "Fairness & Non-discrimination",
  accountability: "Accountability",
  long_term_societal_impact: "Long-term Societal Impact"
};

export const SCORE_LABELS: Record<string, string> = {
  "1": "Exemplary",
  "0.5": "Acceptable",
  "-0.5": "Concerning",
  "-1": "Harmful"
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
