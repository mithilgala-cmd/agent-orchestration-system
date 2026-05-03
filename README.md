# Agent Orchestration System (Sentinal)

[![Tech Stack](https://img.shields.io/badge/Stack-Python%20|%20Next.js%20|%20LangGraph-blue)](#)
[![Status](https://img.shields.io/badge/Status-Production--Ready-green)](#)

An advanced multi-agent orchestration platform designed to decompose complex tasks, delegate to specialized tool-using agents, maintain persistent memory across sessions, and escalate to a human operator for sensitive approvals.

## 🏗️ Architecture
The system follows a **Supervisor-Specialist** pattern orchestrated by a **LangGraph** state machine:

1. **Supervisor Agent**: Decomposes user requests into structured execution plans.
2. **Specialist Agents**:
   - **Research Agent**: Gather real-time data using Web Search (MCP).
   - **Coder Agent**: Execute Python logic in a **Docker-sandboxed** environment.
   - **Reviewer Agent**: Perform quality control on all specialist outputs.
3. **Memory System**:
   - **Short-term**: `SqliteSaver` thread persistence for session continuity.
   - **Long-term**: `ChromaDB` vector storage for semantic experience recall.
4. **Human-in-the-Loop (HITL)**: Next.js dashboard for monitoring and approving sensitive actions.

## 🛠️ Tech Stack
- **Orchestration**: LangGraph
- **LLMs**: GPT-4o, Claude 3.5 Sonnet
- **Backend**: FastAPI, Python 3.11+
- **Frontend**: Next.js 14, Tailwind CSS, Framer Motion
- **Persistence**: Redis (Short-term), ChromaDB (Vector), PostgreSQL
- **Observability**: OpenTelemetry

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for agent sandboxing)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/mithilgala-cmd/agent-orchestration-system.git
   ```
2. Setup Backend:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Setup Frontend:
   ```bash
   cd frontend
   npm install
   ```

### Running the System
1. Start the Backend:
   ```bash
   python main.py
   ```
2. Start the Frontend Dashboard:
   ```bash
   npm run dev
   ```

## 📊 Observability
Every agent decision, tool call, and state transition is traced using **OpenTelemetry**. You can visualize the execution flow directly in the dashboard's "Execution Trace" section.
