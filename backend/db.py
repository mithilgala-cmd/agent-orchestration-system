"""
db.py — SQLite traceability layer with concurrent-access safety.

Improvements:
  - WAL (Write-Ahead Logging) journal mode: readers never block writers,
    enabling safe simultaneous SSE queries from the frontend.
  - Central get_connection() helper with timeout + check_same_thread=False.
  - Context-manager usage ensures connections are closed even on error.
"""
import sqlite3
import json
import logging
from contextlib import contextmanager
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

DB_PATH = "traces.sqlite3"


@contextmanager
def get_connection():
    """
    Yield a SQLite connection configured for concurrent, multi-threaded access.

    Settings:
        timeout=15.0         – wait up to 15 s if the DB is locked before raising.
        check_same_thread=False – allow the connection to be used from any thread,
                                  which is required when FastAPI workers hand off
                                  connections across async/thread-pool boundaries.

    WAL mode is applied once per connection so that simultaneous read queries
    (e.g. Trace Explorer SSE polling) do not block active write transactions.
    """
    conn = sqlite3.connect(DB_PATH, timeout=15.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the traces table if it does not already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                thread_id        TEXT PRIMARY KEY,
                task             TEXT,
                status           TEXT,
                total_tokens     INTEGER DEFAULT 0,
                estimated_cost   REAL    DEFAULT 0.0,
                duration_seconds REAL    DEFAULT 0.0,
                created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metrics          JSON
            )
        """)


def save_trace(thread_id: str, task: str, status: str, metrics: Dict[str, Any]) -> None:
    """Upsert a task trace record into the database."""
    total_tokens: int = metrics.get("total_tokens", 0)
    # Llama-3.3-70b-versatile pricing: ~$0.59/1M input + $0.79/1M output tokens.
    # Using a flat blended rate of $0.70 per 1M tokens for a simple estimate.
    estimated_cost: float = (total_tokens / 1_000_000) * 0.70
    duration_seconds: float = metrics.get("duration", 0.0)

    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO traces
                    (thread_id, task, status, total_tokens, estimated_cost, duration_seconds, metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(thread_id) DO UPDATE SET
                    status           = excluded.status,
                    total_tokens     = excluded.total_tokens,
                    estimated_cost   = excluded.estimated_cost,
                    duration_seconds = excluded.duration_seconds,
                    metrics          = excluded.metrics
            """, (
                thread_id, task, status,
                total_tokens, estimated_cost, duration_seconds,
                json.dumps(metrics),
            ))
    except Exception as exc:
        logger.error("Failed to save trace for thread %s: %s", thread_id, exc)


def get_traces() -> List[Dict[str, Any]]:
    """Return the 100 most recent traces, ordered newest first."""
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM traces ORDER BY created_at DESC LIMIT 100"
            )
            return [dict(row) for row in cursor.fetchall()]
    except Exception as exc:
        logger.error("Failed to fetch traces: %s", exc)
        return []


# Initialise schema on first import
init_db()
