# SPEC: Agent Orchestration System

## 1. Project Overview
A multi-agent orchestration platform where a supervisor agent decomposes complex tasks, delegates to specialized tool-using agents, maintains persistent memory, and escalates to humans when necessary.

## 2. Goals
- Build a production-grade multi-agent system using LangGraph.
- Implement persistent memory (short-term & long-term).
- Provide full observability into agent decision-making.
- Create a Human-in-the-loop (HITL) interface for approvals.

## 3. Tech Stack
- **Backend**: Python 3.11+, LangGraph, FastAPI, Redis, PostgreSQL, ChromaDB.
- **Frontend**: Next.js, Tailwind CSS.
- **Sandbox**: Docker-based Python execution environment.
- **Protocols**: MCP (Google Search, File System, GitHub).
- **LLMs**: GPT-4o (OpenAI), Claude 3.5 Sonnet (Anthropic).
- **Orchestration**: Docker Compose.

## 4. Agent Architecture
- **Supervisor Agent**: Plans and delegates tasks.
- **Specialist Agents**:
    - Research Agent (Tools: Web Search)
    - Coder Agent (Tools: Python REPL)
    - Writing Agent (Tools: File Editor)
- **Reviewer Agent**: Validates outputs.

## 5. Roadmap
### Phase 1: Core Architecture
- [x] Project Scaffolding.
- [x] LangGraph basic workflow.
- [x] Task decomposition engine.
- [x] Tool registry.

### Phase 2: Memory & Context
- [x] Redis working memory.
- [x] ChromaDB vector memory.
- [x] Planning with memory recall.

### Phase 3: Human-in-the-Loop
- [x] Escalation triggers.
- [x] HITL Approval Queue API.
- [x] React Review UI.

### Phase 4: Observability
- [x] Tracing with OpenTelemetry.
- [ ] Trace Explorer UI.
- [ ] Performance & Cost tracking.
