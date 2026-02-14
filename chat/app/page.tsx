"use client";

import { useState } from "react";
import { ChatWindow } from "@/components/ChatWindow";
import { DiagnosticsPanel } from "@/components/DiagnosticsPanel";
import { INITIAL_MESSAGES } from "@/lib/mockData";
import type {
  ChatEvalApiResponse,
  ChatMessage,
  EvalState,
  EvalTurn,
  Principle
} from "@/lib/types";

function makeId(prefix: string, n: number): string {
  return `${prefix}-${Date.now()}-${n}`;
}

export default function HomePage() {
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [sending, setSending] = useState(false);
  const [showPanel, setShowPanel] = useState(true);
  const [selectedPrinciple, setSelectedPrinciple] =
    useState<Principle>("respect_attention");
  const [evalState, setEvalState] = useState<EvalState>({
    turns: [],
    latest: null
  });

  async function onSend(text: string): Promise<void> {
    setSending(true);
    try {
      const userMsg: ChatMessage = {
        id: makeId("u", messages.length + 1),
        role: "user",
        content: text,
        timestamp: Date.now()
      };
      const withUser = [...messages, userMsg];
      setMessages(withUser);

      const res = await fetch("/api/chat-eval", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: text, history: withUser })
      });

      if (!res.ok) {
        const raw = await res.text();
        throw new Error(raw || "Failed to run Gemini chat evaluation.");
      }

      const payload = (await res.json()) as ChatEvalApiResponse;
      const assistantMsg: ChatMessage = {
        id: makeId("a", messages.length + 2),
        role: "assistant",
        content: payload.assistantReply,
        timestamp: Date.now()
      };
      setMessages((prev) => [...prev, assistantMsg]);

      const turn: EvalTurn = {
        turnId: `t-${evalState.turns.length + 1}`,
        messageId: assistantMsg.id,
        scores: payload.eval.scores,
        reasons: payload.eval.reasons,
        overallScore: payload.eval.overallScore
      };
      setEvalState((prev) => {
        const turns = [...prev.turns, turn];
        return { turns, latest: turn };
      });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unknown request error.";
      const assistantMsg: ChatMessage = {
        id: makeId("a", messages.length + 2),
        role: "assistant",
        content: `Gemini request failed: ${message}`,
        timestamp: Date.now()
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <h1>Live Interaction Eval</h1>
        <button type="button" onClick={() => setShowPanel((s) => !s)}>
          {showPanel ? "Hide diagnostics" : "Show diagnostics"}
        </button>
      </header>

      <section
        className={
          showPanel
            ? "content-shell panel-open"
            : "content-shell"
        }
      >
        <ChatWindow
          messages={messages}
          onSend={onSend}
          sending={sending}
        />
        {showPanel && (
          <DiagnosticsPanel
            evalState={evalState}
            selectedPrinciple={selectedPrinciple}
            onPrincipleSelect={setSelectedPrinciple}
          />
        )}
      </section>
    </main>
  );
}
