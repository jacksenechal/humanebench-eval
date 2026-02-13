"use client";

import {
  FormEvent,
  KeyboardEvent,
  useEffect,
  useRef,
  useState
} from "react";
import type { ChatMessage } from "@/lib/types";

interface Props {
  messages: ChatMessage[];
  onSend: (text: string) => Promise<void>;
  sending: boolean;
}

function formatTime(ts: number): string {
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit"
  }).format(ts);
}

export function ChatWindow(
  { messages, onSend, sending }: Props
) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    fire();
  }

  function fire() {
    const text = input.trim();
    if (!text || sending) return;
    setInput("");
    onSend(text);
  }

  function onKey(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      fire();
    }
  }

  return (
    <section className="chat-window">
      <div className="messages">
        {messages.map((m) => (
          <div
            key={m.id}
            className={
              m.role === "user"
                ? "bubble-row bubble-right"
                : "bubble-row bubble-left"
            }
          >
            <div
              className={
                m.role === "user"
                  ? "bubble bubble-user"
                  : "bubble bubble-ai"
              }
            >
              <p>{m.content}</p>
              <span className="bubble-time">
                {formatTime(m.timestamp)}
              </span>
            </div>
          </div>
        ))}

        {sending && (
          <div className="bubble-row bubble-left">
            <div className="bubble bubble-ai typing">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <form className="composer" onSubmit={submit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKey}
          placeholder="Message Gemini..."
          autoComplete="off"
          disabled={sending}
        />
        <button
          type="submit"
          disabled={!input.trim() || sending}
          aria-label="Send"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M22 2 11 13" />
            <path d="M22 2 15 22 11 13 2 9z" />
          </svg>
        </button>
      </form>
    </section>
  );
}
