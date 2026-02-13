import type { ChatMessage, ChatProvider } from "@/lib/types";
import { mockAssistantReply } from "@/lib/mockData";

function casualToneScore(history: ChatMessage[]): number {
  const joined = history.map((m) => m.content.toLowerCase()).join(" ");
  const markers = ["hey", "hi", "thanks", "cool", "great", "awesome"];
  let hits = 0;
  for (const marker of markers) {
    if (joined.includes(marker)) hits += 1;
  }
  return hits / markers.length;
}

export class MockGeminiAdapter implements ChatProvider {
  async sendMessage(input: string, history: ChatMessage[]): Promise<string> {
    const turns = history.length;
    const casual = casualToneScore(history);
    const base = mockAssistantReply(turns + input.length);
    const mode = casual > 0.35 ? "casual" : "neutral";
    return `${base} [tracking: ${mode}, turns: ${turns}]`;
  }
}

export class LiveGeminiAdapter implements ChatProvider {
  constructor(private readonly apiKey: string) {}

  async sendMessage(input: string): Promise<string> {
    if (!this.apiKey) {
      throw new Error("GEMINI_API_KEY is missing.");
    }
    void input;
    throw new Error("Live Gemini adapter is scaffolded but not wired yet.");
  }
}

export function getChatProvider(): ChatProvider {
  const mode = process.env.NEXT_PUBLIC_CHAT_MODE ?? "mock";
  const apiKey = process.env.GEMINI_API_KEY ?? "";
  if (mode === "gemini") return new LiveGeminiAdapter(apiKey);
  return new MockGeminiAdapter();
}
