import sqlite3
import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

DB_PATH = "traces.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traces (
            thread_id TEXT PRIMARY KEY,
            task TEXT,
            status TEXT,
            total_tokens INTEGER DEFAULT 0,
            estimated_cost REAL DEFAULT 0.0,
            duration_seconds REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metrics JSON
        )
    """)
    conn.commit()
    conn.close()

def save_trace(thread_id: str, task: str, status: str, metrics: Dict[str, Any]):
    total_tokens = metrics.get("total_tokens", 0)
    # Llama-3.3-70b-versatile pricing is approx $0.59 / 1M input tokens and $0.79 / 1M output tokens.
    # For a simple estimated cost, let's use a flat $0.70 per 1M tokens.
    estimated_cost = (total_tokens / 1_000_000) * 0.70
    duration_seconds = metrics.get("duration", 0.0)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Upsert logic
        cursor.execute("""
            INSERT INTO traces (thread_id, task, status, total_tokens, estimated_cost, duration_seconds, metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(thread_id) DO UPDATE SET
                status=excluded.status,
                total_tokens=excluded.total_tokens,
                estimated_cost=excluded.estimated_cost,
                duration_seconds=excluded.duration_seconds,
                metrics=excluded.metrics
        """, (thread_id, task, status, total_tokens, estimated_cost, duration_seconds, json.dumps(metrics)))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to save trace to DB: {e}")

def get_traces() -> List[Dict[str, Any]]:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM traces ORDER BY created_at DESC LIMIT 100")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to fetch traces: {e}")
        return []

# Initialize on import
init_db()
