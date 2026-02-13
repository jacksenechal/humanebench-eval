import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

DB_PATH = os.environ.get("HUMANEBENCH_DB_PATH", "./humanebench.db")

_CREATE_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    user_prompt TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    model TEXT,
    history TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluations (
    id TEXT PRIMARY KEY,
    conversation_id TEXT REFERENCES conversations(id),
    principle TEXT NOT NULL,
    score REAL NOT NULL,
    rationale TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluation_runs (
    id TEXT PRIMARY KEY,
    conversation_id TEXT REFERENCES conversations(id),
    overall_score REAL,
    global_violations TEXT,
    confidence REAL,
    evaluator_model TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    conn.executescript(_CREATE_SQL)
    conn.commit()
    conn.close()


def insert_conversation(
    id: str,
    user_prompt: str,
    ai_response: str,
    model: Optional[str] = None,
    history: Optional[list] = None,
    metadata: Optional[dict] = None,
) -> None:
    conn = _connect()
    conn.execute(
        "INSERT OR IGNORE INTO conversations (id, user_prompt, ai_response, model, history, metadata) VALUES (?, ?, ?, ?, ?, ?)",
        (
            id,
            user_prompt,
            ai_response,
            model,
            json.dumps(history) if history else None,
            json.dumps(metadata) if metadata else None,
        ),
    )
    conn.commit()
    conn.close()


def insert_evaluation(
    id: str,
    conversation_id: str,
    principle: str,
    score: float,
    rationale: Optional[str] = None,
    confidence: Optional[float] = None,
) -> None:
    conn = _connect()
    conn.execute(
        "INSERT OR REPLACE INTO evaluations (id, conversation_id, principle, score, rationale, confidence) VALUES (?, ?, ?, ?, ?, ?)",
        (id, conversation_id, principle, score, rationale, confidence),
    )
    conn.commit()
    conn.close()


def insert_evaluation_run(
    id: str,
    conversation_id: str,
    overall_score: float,
    global_violations: list,
    confidence: float,
    evaluator_model: str,
) -> None:
    conn = _connect()
    conn.execute(
        "INSERT OR REPLACE INTO evaluation_runs (id, conversation_id, overall_score, global_violations, confidence, evaluator_model) VALUES (?, ?, ?, ?, ?, ?)",
        (
            id,
            conversation_id,
            overall_score,
            json.dumps(global_violations),
            confidence,
            evaluator_model,
        ),
    )
    conn.commit()
    conn.close()


def get_conversation(conversation_id: str) -> Optional[dict]:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_evaluations_for_conversation(conversation_id: str) -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM evaluations WHERE conversation_id = ? ORDER BY created_at",
        (conversation_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_evaluation_run(conversation_id: str) -> Optional[dict]:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM evaluation_runs WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 1",
        (conversation_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_conversations(limit: int = 50, offset: int = 0) -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM conversations ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _time_cutoff(time_range: str) -> Optional[datetime]:
    now = datetime.utcnow()
    if time_range == "24h":
        return now - timedelta(hours=24)
    elif time_range == "7d":
        return now - timedelta(days=7)
    elif time_range == "30d":
        return now - timedelta(days=30)
    return None


def get_overview_stats(time_range: str = "all") -> dict:
    conn = _connect()
    cutoff = _time_cutoff(time_range)

    where = ""
    params: list = []
    if cutoff:
        where = "WHERE e.created_at >= ?"
        params = [cutoff.isoformat()]

    rows = conn.execute(
        f"""
        SELECT e.principle, AVG(e.score) as avg_score, COUNT(*) as count
        FROM evaluations e
        {where}
        GROUP BY e.principle
        """,
        params,
    ).fetchall()

    total_evals = conn.execute(
        f"SELECT COUNT(DISTINCT conversation_id) FROM evaluations {where}", params
    ).fetchone()[0]

    violations = conn.execute(
        f"SELECT COUNT(*) FROM evaluations e {where} {'AND' if where else 'WHERE'} e.score < 0",
        params if where else [],
    ).fetchone()[0]

    conn.close()

    principle_scores = {r["principle"]: r["avg_score"] for r in rows}
    weakest = (
        min(principle_scores, key=lambda k: principle_scores[k])
        if principle_scores
        else None
    )
    avg_score = (
        sum(principle_scores.values()) / len(principle_scores) if principle_scores else 0
    )

    return {
        "total_evaluations": total_evals,
        "avg_score": round(avg_score, 3),
        "violations_count": violations,
        "weakest_principle": weakest,
        "principle_scores": principle_scores,
    }


def get_incidents(limit: int = 50, principle: Optional[str] = None) -> list[dict]:
    conn = _connect()
    where = "WHERE e.score < 0"
    params: list = []
    if principle:
        where += " AND e.principle = ?"
        params.append(principle)

    rows = conn.execute(
        f"""
        SELECT e.*, c.user_prompt, c.ai_response, c.created_at as conv_created_at
        FROM evaluations e
        JOIN conversations c ON c.id = e.conversation_id
        {where}
        ORDER BY e.score ASC, e.created_at DESC
        LIMIT ?
        """,
        params + [limit],
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_conversations_with_scores(limit: int = 50, offset: int = 0) -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        """
        SELECT c.*, er.overall_score, er.confidence
        FROM conversations c
        LEFT JOIN evaluation_runs er ON er.conversation_id = c.id
        ORDER BY c.created_at DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
