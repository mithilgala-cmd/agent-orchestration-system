# Portfolio Deep Dive: Sentinel AI Orchestrator

This document serves as a technical case study for the **Sentinel** project, detailing the architectural decisions, trade-offs, and engineering challenges solved.

## 🎯 Project Objective
Build a production-grade multi-agent system that is **observable**, **persistent**, and **resilient**, moving beyond simple "demo" scripts to a system capable of handling complex, multi-step tasks with human oversight.

---

## 🏗️ Technical Architecture

### 1. Orchestration: Why LangGraph?
While libraries like AutoGen or CrewAI offer high-level abstractions, I chose **LangGraph** because it treats agentic workflows as a **state machine**.
- **Control**: It allows for fine-grained control over the transition between nodes (e.g., forcing a Reviewer step after every Specialist action).
- **Persistence**: Built-in support for checkpointers (I implemented `SqliteSaver`) means the system is "fault-tolerant" by design.

### 2. Concurrency: The WAL Mode Decision
A common issue with SQLite in multi-threaded environments (like FastAPI) is the `database is locked` error.
- **Problem**: The frontend polls for traces via SSE (Read) while the agent is actively writing new logs (Write).
- **Solution**: I enabled **Write-Ahead Logging (WAL)** mode.
- **Trade-off**: WAL mode slightly increases disk usage but allows **concurrent readers and writers** to operate simultaneously without blocking, which was essential for a smooth UI experience.

### 3. Security: The Sandbox Layer
Running LLM-generated code is inherently risky. I implemented a **Dual-Layer Sandbox**:
- **Layer 1 (Docker)**: The primary execution environment is a `python:3.11-slim` container with no network access and a 128MB RAM limit.
- **Layer 2 (Local Subprocess)**: If Docker is unavailable (common in local dev or limited CI environments), the system falls back to a restricted `subprocess.run` with a strict timeout.
- **Decision**: I prioritized **availability over strict isolation** in the fallback, but included clear logging to warn the operator when Layer 1 is skipped.

---

## 🚀 Key Engineering Challenges Solved

### Handling "Human-in-the-Loop" (HITL)
One of the hardest parts of agentic systems is pausing mid-execution.
- **Mechanism**: I utilized LangGraph's `interrupt_before` feature.
- **Solution**: When the graph reaches the `human_review` node, it serializes its entire state to `checkpoints.sqlite` and yields control back to the API.
- **UI Integration**: The frontend detects the `awaiting_approval` event via SSE and renders a specialized approval card.

### Real-Time Observability at Scale
To provide a "glassbox" experience, the system must stream internal thought processes without latency.
- **Implementation**: Used **Server-Sent Events (SSE)** via `sse-starlette`.
- **Optimization**: I built a central `EventBus` in `stream.py` that uses thread-safe queues. This decouples the agent's execution thread from the FastAPI request/response cycle, preventing performance bottlenecks.

---

## 🛠️ Lessons Learned
1.  **State Management is King**: In complex workflows, the biggest challenge isn't the LLM prompt, but keeping track of the shared state across multiple turns.
2.  **Telemetry is Non-Negotiable**: Without tracing (OpenTelemetry/SQLite logs), debugging an agent that has "gone rogue" or is stuck in a loop is impossible.

---

## 📈 Future Scalability
- **Redis Integration**: For truly distributed systems, the SQLite checkpointer would be replaced with a Redis-based one to support horizontal scaling.
- **Multi-Tenant Support**: Adding `user_id` to the state to isolate threads between different concurrent users.

---
*Developed by [Mithil Gala](https://github.com/mithilgala-cmd)*
