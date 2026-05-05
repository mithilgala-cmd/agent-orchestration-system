# Agent Orchestrator Backend

This directory contains the Python **FastAPI** backend and the **LangGraph** orchestration logic for the Multi-Agent System. It serves as the intelligent core of the application, managing agent routing, tool execution, persistent memory, and state persistence.

## ✨ Key Capabilities

- **LangGraph State Machine**: A complex, cyclic graph topology (`main.py`) that manages the control flow between the Supervisor, the Specialist agents, and the Human-in-the-Loop interrupt node.
- **FastAPI Event Streaming**: Exposes the asynchronous workflow via Server-Sent Events (SSE) so the frontend can display live agent thoughts and actions in real-time (`api.py`, `stream.py`).
- **Short & Long-Term Memory**:
  - Leverages `SqliteSaver` for checkpointing graph state across human interrupts.
  - Employs `ChromaDB` (`memory.py`) for semantic document retrieval and embedding-based experience tracking.
- **Docker Sandbox Execution**: The Coder Agent executes dynamically generated Python scripts within isolated Docker containers (`sandbox.py`) to ensure secure testing without risking the host machine.
- **Observability Persistence**: Logs token consumption, duration, and estimated LLM costs into a local `traces.sqlite3` database for comprehensive analytics (`db.py`).

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Orchestration**: [LangGraph](https://python.langchain.com/v0.1/docs/langgraph/) & [LangChain](https://python.langchain.com/)
- **LLM Provider**: Groq (Llama-3 models for ultra-low latency inference)
- **Database**: SQLite (State & Metrics), Chroma (Vector Embeddings)
- **Security**: Docker SDK for Python

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker (Required for the `sandbox.py` Coder Agent code execution environment)
- A valid Groq API Key

### Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   
   # On Windows:
   .venv\Scripts\activate
   
   # On macOS/Linux:
   source .venv/bin/activate
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Environment Variables:
   Copy the example config and add your Groq API key:
   ```bash
   cp .env.example .env
   ```

### Running the API Server

Start the development server with Uvicorn:

```bash
uvicorn api:api --reload --port 8000
```

The API will be accessible at `http://127.0.0.1:8000`. You can explore the automatic Swagger documentation at `http://127.0.0.1:8000/docs`.

## 📂 Core Files

- `main.py`: The entry point for the LangGraph definition. Contains the nodes, edges, and compilation logic for the agent graph.
- `api.py`: The FastAPI application defining endpoints for task creation, event streaming, human approval, and trace fetching.
- `state.py`: Defines the `AgentState` TypedDict, holding the strict schema passed between nodes.
- `tools.py`: Tool definitions exposed to the language models (e.g., DuckDuckGo Search, file editing).
- `supervisor.py`: The routing logic for the primary orchestrator LLM that delegates work.
- `sandbox.py`: The secure execution environment logic using the Docker daemon.

## 🧪 Testing

To run the internal unit tests (validating state generation and memory components):

```bash
pytest tests.py
```
