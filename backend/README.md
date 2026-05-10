# Sentinel Backend: LangGraph Orchestration Engine

This directory contains the core intelligence of the Sentinel platform—a high-performance, FastAPI-wrapped LangGraph engine.

## 🛠️ Core Components

| Module | Responsibility | Engineering Focus |
|---|---|---|
| `main.py` | Graph Definition | LangGraph cyclic state machine with conditional routing. |
| `api.py` | FastAPI Interface | SSE event streaming & asynchronous task management. |
| `db.py` | Traceability Layer | **WAL-mode** SQLite implementation for concurrent data access. |
| `sandbox.py` | Code Execution | Isolated Docker environment with local subprocess fallback. |
| `memory.py` | Dual-Layer Memory | ChromaDB (Vector) + SQLite (Checkpoints). |
| `supervisor.py` | Task Planning | Decomposition logic and dynamic specialist routing. |

---

## ⚙️ Technical Features

### 1. LangGraph State Machine
The workflow is defined as a directed cyclic graph. Each node transitions state based on a central `AgentState` object:
- **Cyclic Loops**: If the `Reviewer Agent` detects an error, it can route back to a specialist for corrections.
- **Persistence**: Using `SqliteSaver`, every state transition is serialized, allowing for "long-running" tasks that persist across system restarts.

### 2. High-Concurrency Logging
The `db.py` module is optimized for a modern web-app environment:
- **Write-Ahead Logging (WAL)**: Enabled to solve the "SQLite is busy" error during simultaneous read/write operations.
- **Context Manager Pattern**: Ensures every database connection is safely closed, even during unhandled agent exceptions.

### 3. Secure Sandboxing
The `Coder Agent` uses `sandbox.py` to run generated Python code:
- **Containerization**: Uses the Docker SDK to create temporary containers with no network access.
- **Resource Limits**: Containers are capped at 128MB RAM and 30s execution time.
- **Fallback**: Gracefully falls back to `subprocess.run` with identical timeout constraints if Docker is not present.

---

## 🚀 Setup & Execution

### Prerequisites
- Python 3.11+
- [Groq API Key](https://console.groq.com)
- Docker Desktop (Optional, for full sandboxing)

### Installation
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
cp .env.example .env
# Edit .env and add GROQ_API_KEY
```

### Running the Server
```bash
uvicorn api:api --reload --port 8000
```

---

## 🧪 Automated Testing
The backend is covered by a comprehensive **pytest** suite:
```bash
pytest tests.py -v
```
- **DB Concurrency**: Tests WAL-mode with 10 simultaneous writer threads.
- **Sandbox Fallback**: Verifies local execution when Docker is forced to fail.
- **Streaming Mechanics**: Ensures thread-safe event emission via the EventBus.

---
*Backing your agents with production-grade engineering.*
