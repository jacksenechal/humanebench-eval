# Live Eval

A chat interface paired with a humaneness evaluation dashboard. The **chat** app lets users converse with a Gemini-powered assistant and shows real-time safety risk scores. Each conversation is also sent to the **dashboard**, which scores responses against 8 principles of humane AI design.

## Architecture

```
User ──▶ Chat UI (Next.js, port 3000)
           │
           ├──▶ Gemini Flash ── chat reply
           ├──▶ Gemini Pro ──── safety risk scores (shown in chat UI)
           └──▶ Dashboard /evaluate (fire-and-forget)
                  │
                  ├──▶ Gemini 2.0 Flash via OpenRouter ── humaneness scores
                  └──▶ Dashboard UI (FastAPI, port 8000)
```

Both UIs are exposed publicly via Cloudflare quick tunnels with nginx basic auth in front.

## Prerequisites

- Docker and Docker Compose
- A [Google Gemini API key](https://aistudio.google.com/apikey)
- An [OpenRouter API key](https://openrouter.ai/keys)

## Quick Start

1. **Clone and enter the repo:**

   ```sh
   git clone git@github.com:jacksenechal/humanebench-eval.git
   cd humanebench-eval
   ```

2. **Create your `.env`:**

   ```sh
   cp .env.example .env
   ```

   Edit `.env` and fill in your API keys:

   ```
   GEMINI_API_KEY=your-gemini-key
   OPENROUTER_API_KEY=your-openrouter-key
   ```

   Optionally change `AUTH_USER` and `AUTH_PASS` (default: `admin` / `changeme`).

3. **Generate the basic auth file:**

   ```sh
   # Using openssl (available on most systems):
   printf '%s:%s\n' "$(grep AUTH_USER .env | cut -d= -f2)" \
     "$(openssl passwd -apr1 "$(grep AUTH_PASS .env | cut -d= -f2)")" > .htpasswd
   ```

4. **Start everything:**

   ```sh
   docker compose up -d
   ```

   This brings up 5 containers: chat, dashboard, nginx, and two Cloudflare tunnels.

5. **Get your public URLs:**

   ```sh
   docker compose logs tunnel-chat 2>&1 | grep -o 'https://.*trycloudflare.com' | tail -1
   docker compose logs tunnel-dashboard 2>&1 | grep -o 'https://.*trycloudflare.com' | tail -1
   ```

6. **Verify:**

   ```sh
   # Local (via nginx)
   curl -u admin:changeme http://localhost:8080/   # chat
   curl -u admin:changeme http://localhost:8081/   # dashboard

   # Auth enforced
   curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/   # → 401
   ```

## Services

| Service | Port | Description |
|---------|------|-------------|
| `chat` | 3000 (internal) | Next.js chat UI with Gemini safety eval |
| `dashboard` | 8000 (internal) | FastAPI humaneness dashboard with 8-principle scoring |
| `nginx` | 8080, 8081 (host) | Reverse proxy with basic auth |
| `tunnel-chat` | — | Cloudflare quick tunnel → chat |
| `tunnel-dashboard` | — | Cloudflare quick tunnel → dashboard |

## Environment Variables

| Variable | Required | Default | Used by |
|----------|----------|---------|---------|
| `GEMINI_API_KEY` | Yes | — | chat |
| `GEMINI_CHAT_MODEL` | No | `gemini-2.5-flash-lite` | chat |
| `GEMINI_EVAL_MODEL` | No | `gemini-3-pro-preview` | chat |
| `OPENROUTER_API_KEY` | Yes | — | dashboard |
| `AUTH_USER` | No | `admin` | nginx |
| `AUTH_PASS` | No | `changeme` | nginx |

## Development

To work on individual services without Docker:

```sh
# Chat
cd chat && npm install && npm run dev    # http://localhost:3000

# Dashboard
cd dashboard && pip install -e ".[dev]"
python scripts/seed_demo.py              # seed demo data
uvicorn humanebench.api:app --port 8000 --reload
```

## How It Works

1. User sends a message in the chat UI
2. Chat backend calls Gemini Flash for a reply, then Gemini Pro for safety risk scores
3. Chat backend fires-and-forgets a POST to the dashboard's `/evaluate` endpoint with the conversation
4. Dashboard queues the conversation for async evaluation against 8 humaneness principles using Gemini 2.0 Flash (via OpenRouter)
5. Results appear in the dashboard UI (auto-refreshes every 30s)

The chat's built-in eval measures **safety risk** (malicious, dangerous, manipulative, sensitive). The dashboard measures **humaneness** (respect for attention, meaningful choices, dignity, healthy relationships, etc.). They're complementary.
