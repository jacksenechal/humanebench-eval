# Live Interaction Eval

ChatGPT-style browser chat with a hideable right diagnostics panel for
live risk analysis against baseline values.

## Features

- Chat UI similar to ChatGPT flow.
- Right-side diagnostics panel with hide/show toggle.
- Gemini evaluation categories:
  - positive
  - malicious
  - dangerous
  - manipulative
  - sensitive
- Trend and category graphs.
- Category click-through to explain score and evidence.
- Live Gemini response + evaluation in one API call.

## Local Development

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## Environment

Copy `.env.example` to `.env.local` and set:

- `GEMINI_API_KEY=your_real_key`
- `GEMINI_CHAT_MODEL=gemini-3-flash-preview` (chat replies)
- `GEMINI_EVAL_MODEL=gemini-3-pro-preview` (risk evaluation)

## Vercel Deploy

1. Import repository in Vercel.
2. Framework preset: Next.js (auto-detected).
3. Add environment variables from `.env.example`.
4. Deploy.

## Notes

Gemini runs server-side in `app/api/chat-eval/route.ts`.
This keeps your API key out of browser code.
