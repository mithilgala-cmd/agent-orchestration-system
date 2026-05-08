"""
tests.py — Unit tests for the Agent Orchestration System backend.

Tests are written with pytest and cover the three core backend modules
that don't require a live LLM or network connection:

  - db.py        : trace persistence and WAL-mode concurrency
  - sandbox.py   : local subprocess fallback execution
  - stream.py    : thread-safe EventBus channel mechanics

Run with:
    pytest tests.py -v
"""
import json
import os
import sqlite3
import tempfile
import threading

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_temp_db(monkeypatch) -> str:
    """Point db.DB_PATH to a fresh temp file for each test."""
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
    tmp.close()
    import db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp.name)
    db_module.init_db()          # create schema in temp file
    return tmp.name


# ---------------------------------------------------------------------------
# db.py tests
# ---------------------------------------------------------------------------

class TestDatabase:
    def test_init_creates_table(self, monkeypatch, tmp_path):
        """init_db() must create the traces table without raising."""
        import db as db_module
        db_path = str(tmp_path / "test.sqlite3")
        monkeypatch.setattr(db_module, "DB_PATH", db_path)
        db_module.init_db()

        conn = sqlite3.connect(db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='traces'"
        ).fetchall()
        conn.close()
        assert len(tables) == 1, "traces table was not created"

    def test_save_and_retrieve_trace(self, monkeypatch, tmp_path):
        """save_trace() persists a record; get_traces() returns it."""
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.sqlite3"))
        db_module.init_db()

        metrics = {"total_tokens": 500, "duration": 1.23}
        db_module.save_trace("thread-001", "Test task", "completed", metrics)

        traces = db_module.get_traces()
        assert len(traces) == 1
        t = traces[0]
        assert t["thread_id"] == "thread-001"
        assert t["status"] == "completed"
        assert t["total_tokens"] == 500
        assert abs(t["duration_seconds"] - 1.23) < 1e-6
        # Estimated cost: 500 / 1_000_000 * 0.70
        assert abs(t["estimated_cost"] - 0.00035) < 1e-9

    def test_upsert_updates_existing(self, monkeypatch, tmp_path):
        """Saving twice with the same thread_id should update, not duplicate."""
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.sqlite3"))
        db_module.init_db()

        db_module.save_trace("thread-002", "My task", "running",  {"total_tokens": 100})
        db_module.save_trace("thread-002", "My task", "completed", {"total_tokens": 200})

        traces = db_module.get_traces()
        assert len(traces) == 1
        assert traces[0]["status"] == "completed"
        assert traces[0]["total_tokens"] == 200

    def test_wal_mode_enabled(self, monkeypatch, tmp_path):
        """The WAL journal mode must be set on every new connection."""
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.sqlite3"))
        db_module.init_db()

        with db_module.get_connection() as conn:
            mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        assert mode == "wal", f"Expected WAL mode, got '{mode}'"

    def test_concurrent_writes_dont_lock(self, monkeypatch, tmp_path):
        """Multiple threads writing concurrently must not raise 'database is locked'."""
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.sqlite3"))
        db_module.init_db()

        errors: list = []

        def write(tid: str):
            try:
                db_module.save_trace(tid, f"Task {tid}", "completed", {"total_tokens": 10})
            except Exception as exc:  # pragma: no cover
                errors.append(exc)

        threads = [threading.Thread(target=write, args=(f"t-{i}",)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Concurrent write errors: {errors}"
        assert len(db_module.get_traces()) == 10

    def test_get_traces_empty(self, monkeypatch, tmp_path):
        """get_traces() must return an empty list when no traces exist."""
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.sqlite3"))
        db_module.init_db()
        assert db_module.get_traces() == []


# ---------------------------------------------------------------------------
# sandbox.py tests
# ---------------------------------------------------------------------------

class TestSandbox:
    def test_local_success(self):
        """_execute_local() returns status=success for valid code."""
        from sandbox import DockerSandbox
        sb = DockerSandbox()
        result = sb._execute_local("print('hello sandbox')", timeout=10)
        assert result["status"] == "success"
        assert "hello sandbox" in result["output"]

    def test_local_syntax_error(self):
        """_execute_local() returns status=error for broken code."""
        from sandbox import DockerSandbox
        sb = DockerSandbox()
        result = sb._execute_local("this is not python!!!", timeout=10)
        assert result["status"] == "error"
        assert result["output"]  # some error message present

    def test_local_timeout(self):
        """_execute_local() returns status=error when execution exceeds timeout."""
        from sandbox import DockerSandbox
        sb = DockerSandbox()
        result = sb._execute_local("import time; time.sleep(60)", timeout=1)
        assert result["status"] == "error"
        assert "timed out" in result["output"].lower()

    def test_execute_code_falls_back_when_docker_unavailable(self, monkeypatch):
        """execute_code() must fall back to _execute_local on DockerException."""
        import docker
        from sandbox import DockerSandbox

        sb = DockerSandbox()

        # Force the .client property to raise DockerException
        monkeypatch.setattr(
            type(sb), "client",
            property(lambda self: (_ for _ in ()).throw(
                docker.errors.DockerException("Docker not available")
            ))
        )

        result = sb.execute_code("print(42)")
        assert result["status"] == "success"
        assert "42" in result["output"]


# ---------------------------------------------------------------------------
# stream.py tests
# ---------------------------------------------------------------------------

class TestEventBus:
    def test_create_and_get_channel(self):
        """create_channel() followed by get_channel() must return the same queue."""
        from stream import EventBus
        bus = EventBus()
        q = bus.create_channel("ch-1")
        assert bus.get_channel("ch-1") is q

    def test_emit_puts_event_on_queue(self):
        """emit() places a typed dict on the channel queue."""
        from stream import EventBus
        bus = EventBus()
        bus.create_channel("ch-2")
        bus.emit("ch-2", "node_start", {"node": "Supervisor"})

        event = bus.get_channel("ch-2").get_nowait()
        assert event["type"] == "node_start"
        assert event["data"]["node"] == "Supervisor"

    def test_emit_sentinel_puts_none(self):
        """emit_sentinel() places None on the queue (SSE termination signal)."""
        from stream import EventBus
        bus = EventBus()
        bus.create_channel("ch-3")
        bus.emit_sentinel("ch-3")
        assert bus.get_channel("ch-3").get_nowait() is None

    def test_close_channel_removes_it(self):
        """close_channel() must make get_channel() return None."""
        from stream import EventBus
        bus = EventBus()
        bus.create_channel("ch-4")
        bus.close_channel("ch-4")
        assert bus.get_channel("ch-4") is None

    def test_emit_to_nonexistent_channel_is_noop(self):
        """Emitting to an unknown channel must not raise."""
        from stream import EventBus
        bus = EventBus()
        bus.emit("ghost-channel", "test", {})  # should not raise

    def test_thread_safe_emit(self):
        """Multiple threads emitting concurrently must not lose events."""
        from stream import EventBus
        bus = EventBus()
        bus.create_channel("ch-5")
        n = 50

        def emit_events():
            for i in range(n):
                bus.emit("ch-5", "ping", {"i": i})

        threads = [threading.Thread(target=emit_events) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        q = bus.get_channel("ch-5")
        count = 0
        while not q.empty():
            q.get_nowait()
            count += 1
        assert count == n * 4, f"Expected {n * 4} events, got {count}"
