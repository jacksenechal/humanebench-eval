#!/bin/sh
set -e

DB_PATH="${HUMANEBENCH_DB_PATH:-./humanebench.db}"

# Seed demo data on first run (if DB doesn't exist yet and API key is set)
if [ ! -f "$DB_PATH" ] && [ -n "$OPENROUTER_API_KEY" ]; then
    echo "First run — seeding demo data..."
    python scripts/seed_demo.py || echo "Seed failed (non-fatal), continuing..."
fi

exec uvicorn humanebench.api:app --host 0.0.0.0 --port 8000
