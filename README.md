<div align="center">
  <img src="https://img.shields.io/badge/Agent-Orchestration_System-blue?style=for-the-badge&logo=openai" alt="Agent Orchestration System" />
  <h1 align="center">Multi-Agent Orchestration System</h1>
  <p align="center">
    <strong>A high-performance, resilient AI orchestration platform built with LangGraph, FastAPI, and Next.js.</strong>
  </p>
  
  <p align="center">
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#getting-started">Getting Started</a> •
    <a href="#observability">Observability</a>
  </p>
</div>

---

## 🌟 Overview

The **Multi-Agent Orchestration System (Sentinal)** is a portfolio project and a production-grade AI platform designed to break down complex tasks, delegate execution to specialized LLM-powered agents, and maintain persistent memory across sessions. It features a modern Human-in-the-Loop (HITL) interface for secure execution and an integrated observability layer for auditing agent reasoning and costs.

This project was built to demonstrate advanced AI engineering patterns, scalable backend system design, and premium frontend UI development.

## ✨ Features

- 🧠 **Supervisor-Specialist Architecture**: A central supervisor agent decomposes complex queries into a structured execution plan, dynamically routing sub-tasks to specialized worker agents.
- 🛠️ **Specialized Agent Swarm**:
  - **Research Agent**: Scours the web for real-time data using the Model Context Protocol (MCP).
  - **Coder Agent**: Writes, executes, and validates Python code within a secure, sandboxed Docker environment.
  - **Reviewer Agent**: Conducts rigorous quality control and synthesis on all specialist outputs before delivery.
- 💾 **Dual-Layer Memory System**:
  - **Short-Term Memory**: Utilizes `SqliteSaver` to persist thread state, ensuring agents retain context during multi-turn conversations.
  - **Long-Term Memory**: Integrates `ChromaDB` for semantic vector storage, allowing the system to recall past experiences and learnings across different sessions.
- 🛡️ **Human-in-the-Loop (HITL)**: Sensitive actions (e.g., executing code, API transactions) are intercepted and escalated to a human operator via a premium Next.js dashboard for explicit approval.
- 📊 **Real-time Observability & Tracing**: Every LLM call, tool execution, and token usage is captured. A built-in Trace Explorer dashboard visualizes execution costs, latencies, and agent reasoning.

## 🏗️ Architecture

The system is powered by a **State Machine** driven by `LangGraph`, separating control flow from execution logic.

1. **Frontend (Next.js)**: A glassmorphic, real-time dashboard tracking agent events via Server-Sent Events (SSE).
2. **Backend (FastAPI)**: Serves as the orchestration layer, managing the LangGraph event loop, human interrupts, and database connections.
3. **Agent Graph (LangGraph)**: The core reasoning engine where nodes represent agents and edges define conditional routing logic.

## 💻 Tech Stack

- **Orchestration**: [LangGraph](https://python.langchain.com/v0.1/docs/langgraph/), LangChain Core
- **LLM Integration**: Groq (Llama-3-70b for fast inference)
- **Backend API**: FastAPI, Python 3.11+, Pydantic
- **Frontend Dashboard**: Next.js 14 (App Router), Tailwind CSS, Lucide React, Framer Motion
- **Database & Memory**: SQLite (State persistence), ChromaDB (Vector store)
- **Execution Environment**: Docker SDK for Python (Secure code execution)

## 🚀 Getting Started

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **Docker** (Must be running for the Coder Agent's sandbox)
- **Groq API Key** (or substitute with OpenAI/Anthropic keys)

### 1. Clone the Repository
```bash
git clone https://github.com/mithilgala-cmd/agent-orchestration-system.git
cd agent-orchestration-system
```

### 2. Setup Backend (FastAPI & LangGraph)
Navigate to the backend directory, set up the virtual environment, and configure secrets:
```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt

# Create .env file based on .env.example
cp .env.example .env
```
*Note: Ensure you add your `GROQ_API_KEY` to the `.env` file.*

Start the backend server:
```bash
uvicorn api:api --reload --port 8000
```

### 3. Setup Frontend (Next.js)
In a new terminal window, navigate to the frontend directory:
```bash
cd frontend
npm install
```

Start the dashboard:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## 📊 Traceability & Observability
The system natively tracks its own performance. By switching to the **Trace History** tab in the frontend dashboard, operators can review:
- **Total Tokens Used** per task.
- **Estimated Costs** based on the configured LLM pricing.
- **Execution Duration** for performance bottlenecks.
- **Task Statuses** (Completed, Paused for HITL, Error).

## 🔒 Security
- **Sandboxed Execution**: The Coder agent writes code to temporary directories and executes them inside isolated Docker containers, preventing host-system compromise.
- **Explicit Approval Gates**: State execution is paused before sensitive operations, requiring an explicit `POST /tasks/{thread_id}/approve` from the dashboard.

---
<div align="center">
  <i>Engineered for scale, resilience, and full autonomy.</i>
</div>
