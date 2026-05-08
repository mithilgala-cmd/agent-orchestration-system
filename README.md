<div align="center">
  <img src="https://img.shields.io/badge/Multi--Agent_System-LangGraph-blue?style=for-the-badge&logo=python" alt="Multi-Agent Orchestration System" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Frontend-Next.js_14-black?style=for-the-badge&logo=next.js" alt="Next.js" />
  <img src="https://img.shields.io/badge/Tests-16_Passing-brightgreen?style=for-the-badge&logo=pytest" alt="Tests Passing" />

  <h1 align="center">Multi-Agent Orchestration System</h1>
  <p align="center">
    <strong>A production-grade AI orchestration platform — LangGraph supervisor/specialist architecture with real-time SSE streaming, dual-layer memory, Docker-sandboxed code execution, and an integrated Trace Explorer dashboard.</strong>
  </p>

  <p align="center">
    <a href="#-overview">Overview</a> •
    <a href="#-features">Features</a> •
    <a href="#️-architecture">Architecture</a> •
    <a href="#-tech-stack">Tech Stack</a> •
    <a href="#-getting-started">Getting Started</a> •
    <a href="#-observability--tracing">Observability</a> •
    <a href="#-security">Security</a> •
    <a href="#-testing">Testing</a>
  </p>
</div>

---

## 🌟 Overview

**Sentinel** is a full-stack AI engineering showcase that demonstrates how to build a robust, observable, multi-agent system from first principles. A central Supervisor LLM decomposes natural-language tasks into an ordered execution plan and dispatches sub-tasks to specialized ReAct agents. Every LLM call, tool invocation, and token is traced, persisted to SQLite, and surfaced in a glassmorphic Next.js dashboard via real-time Server-Sent Events.

> Built to demonstrate advanced AI engineering patterns — from LangGraph state machines and Human-in-the-Loop interrupts, to WAL-mode SQLite concurrency and Docker-sandboxed code execution.

---

## ✨ Features

### 🧠 Supervisor–Specialist Architecture
A central Supervisor LLM decomposes any complex user request into a structured 1–3 step execution plan, then dynamically routes each sub-task to the appropriate specialist.

### 🛠️ Specialized Agent Swarm
| Agent | Responsibility | Tool |
|---|---|---|
| **Research Agent** | Web intelligence gathering | DuckDuckGo Search |
| **Coder Agent** | Python code generation & execution | Docker Sandbox → local fallback |
| **Writer Agent** | Artifact generation & file output | File Writer |
| **Reviewer Agent** | Quality control & synthesis | — |

### 💾 Dual-Layer Memory System
- **Short-Term (SqliteSaver)**: LangGraph checkpoint store — persists full thread state across human interrupts, enabling true multi-turn conversations.
- **Long-Term (ChromaDB)**: Semantic vector store using `all-MiniLM-L6-v2` embeddings — the Supervisor recalls relevant past experiences before planning each new task.

### 🛡️ Human-in-the-Loop (HITL)
Graph execution is interrupted before any sensitive operation (e.g., running LLM-generated code). The dashboard surfaces an approval card; a single click resumes or rejects the workflow via `POST /tasks/{thread_id}/approve`.

### 📊 Real-Time Observability
Every agent event (node start/finish, tool calls, plan steps) is streamed live to the frontend via SSE. Completed traces — including token counts, estimated LLM cost, and wall-clock duration — are persisted in a WAL-mode SQLite database and queryable from the Trace Explorer tab.

### 🔒 Resilient Code Sandbox
The Coder Agent first attempts to execute generated Python inside an isolated Docker container (no network, 128 MB RAM cap). If Docker is unavailable, it automatically falls back to a local `subprocess` execution without crashing the workflow.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Next.js Dashboard                            │
│  TaskRunner  │  EventStreamViewer (SSE)  │  TraceExplorer           │
└──────────────────────────┬──────────────────────────────────────────┘
                           │  HTTP / SSE
┌──────────────────────────▼──────────────────────────────────────────┐
│                         FastAPI (api.py)                            │
│   POST /tasks  │  GET /tasks/{id}/stream  │  POST /tasks/{id}/approve│
└──────────────────────────┬──────────────────────────────────────────┘
                           │  Thread pool
┌──────────────────────────▼──────────────────────────────────────────┐
│                      LangGraph Graph (main.py)                      │
│                                                                     │
│  [Supervisor] ──▶ [Research | Coder | Writer] ──▶ [Reviewer]       │
│                              │                         │            │
│                         [Human Review]◀────── interrupt_before      │
└──────┬───────────────────────┼─────────────────────────────────────-┘
       │                       │
  WAL SQLite              ChromaDB / Docker Sandbox
  (traces.sqlite3)        (memory.py / sandbox.py)
```

The graph is a **cyclic state machine** — after each specialist node completes, control returns to the Reviewer, which either accepts the output or escalates to human review.

---

## 💻 Tech Stack

| Layer | Technology |
|---|---|
| **Orchestration** | LangGraph, LangChain Core |
| **LLM Provider** | Groq (Llama-3.3-70b-versatile) |
| **Backend API** | FastAPI 0.115+, Uvicorn, Pydantic v2 |
| **Frontend** | Next.js 14 (App Router), Tailwind CSS, Lucide React |
| **Databases** | SQLite + WAL mode (traces), ChromaDB (vector store) |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` (local, no API key) |
| **Sandboxing** | Docker SDK for Python → subprocess fallback |
| **Observability** | OpenTelemetry SDK (console exporter) |
| **Testing** | pytest 8 (16 unit tests) |

---

## 🚀 Getting Started

### Prerequisites
- Python **3.11+**
- Node.js **18+**
- Docker Desktop (optional — the system falls back gracefully if unavailable)
- A **Groq API Key** → [console.groq.com](https://console.groq.com)

### 1. Clone the Repository
```bash
git clone https://github.com/mithilgala-cmd/agent-orchestration-system.git
cd agent-orchestration-system
```

### 2. Configure & Start the Backend
```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .env.example .env
# → Open .env and set GROQ_API_KEY=your_key_here

# Start the API server
uvicorn api:api --reload --port 8000
```

The backend Swagger UI will be live at **http://127.0.0.1:8000/docs**.

### 3. Start the Frontend Dashboard
Open a second terminal:
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

---

## 📊 Observability & Tracing

Switch to the **Trace History** tab in the dashboard to see every completed run:

| Column | Description |
|---|---|
| **Thread ID** | Unique identifier for the task execution |
| **Task** | The original user prompt |
| **Status** | `completed` / `paused` (HITL) / `error` |
| **Total Tokens** | Aggregated across all agent invocations |
| **Estimated Cost** | Calculated at $0.70 / 1M tokens (Llama-3.3-70b blended rate) |
| **Duration** | Wall-clock execution time in seconds |

Trace records are persisted in `backend/traces.sqlite3` using **WAL journal mode**, ensuring concurrent reads (from the Trace Explorer) never block active write transactions (from running tasks).

---

## 🔒 Security

- **Sandboxed Code Execution**: Generated Python is run inside an isolated Docker container with `network_disabled=True` and a 128 MB memory cap. If Docker is unavailable, the system falls back to a local `subprocess.run` with a configurable timeout.
- **Explicit Approval Gates**: The LangGraph graph pauses at `interrupt_before=["human_review"]`. The frontend must POST to `/tasks/{thread_id}/approve` before execution resumes — nothing runs silently.
- **Secrets via `.env`**: API keys are never hardcoded. The `.env.example` file documents all required variables.

---

## 🧪 Testing

The test suite covers the three core backend modules that operate independently of a live LLM or network:

```bash
cd backend
pytest tests.py -v
```

```
tests.py::TestDatabase::test_init_creates_table               PASSED
tests.py::TestDatabase::test_save_and_retrieve_trace          PASSED
tests.py::TestDatabase::test_upsert_updates_existing          PASSED
tests.py::TestDatabase::test_wal_mode_enabled                 PASSED
tests.py::TestDatabase::test_concurrent_writes_dont_lock      PASSED
tests.py::TestDatabase::test_get_traces_empty                 PASSED
tests.py::TestSandbox::test_local_success                     PASSED
tests.py::TestSandbox::test_local_syntax_error                PASSED
tests.py::TestSandbox::test_local_timeout                     PASSED
tests.py::TestSandbox::test_execute_code_falls_back_when_docker_unavailable PASSED
tests.py::TestEventBus::test_create_and_get_channel           PASSED
tests.py::TestEventBus::test_emit_puts_event_on_queue         PASSED
tests.py::TestEventBus::test_emit_sentinel_puts_none          PASSED
tests.py::TestEventBus::test_close_channel_removes_it         PASSED
tests.py::TestEventBus::test_emit_to_nonexistent_channel_is_noop PASSED
tests.py::TestEventBus::test_thread_safe_emit                 PASSED

16 passed in 3.02s
```

---

<div align="center">
  <i>Engineered for scale, resilience, and full autonomy.</i>
</div>
