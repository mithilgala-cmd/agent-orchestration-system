# Agent Orchestrator — Backend

This directory contains the **FastAPI** server and **LangGraph** orchestration engine for the Multi-Agent System. It is the intelligent core of the platform — managing agent routing, secure code execution, dual-layer memory, SSE event streaming, and SQLite-backed observability.

---

## ✨ Key Capabilities

### 🔄 LangGraph State Machine (`main.py`)
A cyclic graph topology that manages control flow between the Supervisor, three specialist ReAct agents, and the Human-in-the-Loop interrupt node. All agent nodes emit events to the `EventBus` for live SSE streaming.

### 📡 FastAPI Event Streaming (`api.py`, `stream.py`)
Exposes a thread-safe `EventBus` over Server-Sent Events so the Next.js frontend can display live agent reasoning, tool calls, and state transitions without polling. The `EventBus` uses `queue.SimpleQueue` — safe to call from any thread, including LangGraph's thread-pool workers.

### 💾 Dual-Layer Memory (`memory.py`)
- **Short-Term**: `MemorySaver` (LangGraph's in-memory checkpointer) persists full thread state across human review interrupts.
- **Long-Term**: ChromaDB vector store with `all-MiniLM-L6-v2` local embeddings. The Supervisor queries relevant past experiences before constructing each new execution plan.

### 🔒 Resilient Code Sandbox (`sandbox.py`)
The Coder Agent executes LLM-generated Python inside an isolated Docker container:
- Network disabled, 128 MB RAM cap, automatic container removal.
- **Graceful fallback**: If Docker is unavailable or raises `DockerException`/`APIError`, the sandbox logs a warning and transparently routes execution to a local `subprocess.run` with the same timeout — the workflow never crashes.

### 📊 WAL-Mode Observability (`db.py`)
Token consumption, LLM cost estimates, and wall-clock duration for every task are persisted to `traces.sqlite3`. Key implementation details:
- **WAL journal mode** (`PRAGMA journal_mode=WAL`) — readers never block writers, preventing "database is locked" errors when the Trace Explorer SSE tab polls concurrently with an active task.
- **Context-manager pattern** — every connection is committed on success and rolled back on error, with guaranteed `close()` via `finally`.
- **Upsert semantics** — `INSERT … ON CONFLICT DO UPDATE` so re-running a thread ID updates the existing record.

### 📈 OpenTelemetry Tracing (`observability.py`)
`AgentTracer` wraps each specialist node in an OpenTelemetry span, recording `agent.name`, `agent.decision`, and tool invocation events. Currently exports to the console exporter; swap in an OTLP exporter for production.

---

## 📂 File Reference

| File | Role |
|---|---|
| `main.py` | LangGraph graph definition: nodes, conditional edges, graph compilation |
| `api.py` | FastAPI application: task creation, SSE streaming, HITL approve/reject, traces endpoint |
| `state.py` | `AgentState` TypedDict — the strict schema passed between all graph nodes |
| `supervisor.py` | Supervisor LLM — decomposes user requests into structured `ExecutionPlan` objects |
| `tools.py` | LangChain `@tool` definitions: web search, Python execution, file writer |
| `sandbox.py` | Docker-based code execution with subprocess fallback |
| `memory.py` | `LongTermMemory` class wrapping ChromaDB for semantic recall |
| `stream.py` | Thread-safe `EventBus` using `queue.SimpleQueue` |
| `db.py` | SQLite traceability layer with WAL mode and context-manager connections |
| `observability.py` | OpenTelemetry `AgentTracer` for structured span-level logging |
| `tests.py` | pytest unit tests (16 tests, no LLM or network required) |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Framework** | FastAPI 0.115+, Uvicorn |
| **Orchestration** | LangGraph 0.2+, LangChain Core 0.3+ |
| **LLM Provider** | Groq (Llama-3.3-70b-versatile) |
| **Databases** | SQLite + WAL mode, ChromaDB |
| **Embeddings** | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` |
| **Sandboxing** | Docker SDK for Python, subprocess fallback |
| **Observability** | OpenTelemetry SDK 1.25+ |
| **Testing** | pytest 8+ |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker Desktop (optional — falls back gracefully)
- Groq API Key

### Installation

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# Install all dependencies (including pytest)
pip install -r requirements.txt

# Configure secrets
cp .env.example .env
# Edit .env and set your GROQ_API_KEY
```

### Running the API Server

```bash
uvicorn api:api --reload --port 8000
```

- **API Base**: `http://127.0.0.1:8000`
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/health`

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tasks` | Create a new task and start the agent workflow |
| `GET` | `/tasks/{thread_id}/stream` | SSE stream of real-time agent events |
| `GET` | `/tasks/{thread_id}/status` | Get current LangGraph state for a thread |
| `POST` | `/tasks/{thread_id}/approve` | Resume a graph paused at human review |
| `POST` | `/tasks/{thread_id}/reject` | Reject and close a paused task |
| `GET` | `/traces` | Fetch all historical trace records |
| `GET` | `/health` | Health check |

---

## 🧪 Testing

The test suite covers `db.py`, `sandbox.py`, and `stream.py` without requiring a live LLM, network access, or Docker:

```bash
pytest tests.py -v
```

**Test coverage:**

| Module | Tests | What's verified |
|---|---|---|
| `db.py` | 6 | Table creation, save/retrieve, upsert, WAL mode, concurrent writes (10 threads), empty state |
| `sandbox.py` | 4 | Successful execution, syntax error handling, timeout enforcement, Docker fallback |
| `stream.py` | 6 | Channel lifecycle, event emission, sentinel value, channel close, noop on missing channel, 4-thread concurrent emit |

```
16 passed in 3.02s
```
