# Agent Orchestrator — Frontend Dashboard

This directory contains the **Next.js 16** frontend for the Multi-Agent Orchestration System. It is the primary operator interface for dispatching tasks, watching live agent execution, issuing Human-in-the-Loop approvals, and reviewing historical trace data.

---

## ✨ Key Capabilities

### 📡 Real-Time Event Streaming
Connects to the FastAPI backend via the browser's native `EventSource` API (Server-Sent Events). Every agent event — node start/finish, tool calls, plan steps, HITL alerts — is rendered live without polling.

### 🛡️ Human-in-the-Loop (HITL) Controls
When the backend graph pauses at the `human_review` interrupt node, the `EventStreamViewer` surfaces a full-width approval card with **Approve** and **Reject** buttons. Approving sends a `POST /tasks/{thread_id}/approve` to resume the workflow; rejection gracefully closes the event channel.

### 📊 Trace Explorer
The **Trace History** tab fetches all completed task records from `GET /traces` and renders them in a structured table showing thread ID, task summary, status badge, token count, estimated LLM cost, and wall-clock duration.

### 🎨 Premium Glassmorphic Design
- **Dark-mode first**: All backgrounds use deep zinc/slate tones (`#09090b` base) with layered `bg-black/40` overlays.
- **Glassmorphism**: Panels use `backdrop-blur-md` + `border-white/5` for a premium frosted-glass effect.
- **Semantic color coding**: Each agent has a distinct identity color (Blue → Supervisor, Purple → Research, Cyan → Coder, Emerald → Writer, Amber → Reviewer).
- **Micro-animations**: Framer Motion powers the live agent pipeline visualization; Tailwind CSS `animate-pulse` / `animate-spin` provide heartbeat and loading indicators.

---

## 📂 Directory Structure

```
src/
├── app/
│   ├── page.tsx          # Root page — tabbed layout (Live Run / Trace History)
│   ├── layout.tsx        # Root layout with font and metadata
│   └── globals.css       # Global styles, CSS variables, glassmorphic utilities
└── components/
    ├── TaskRunner.tsx        # Input form for dispatching new tasks
    ├── EventStreamViewer.tsx # Live SSE console with HITL approve/reject UI
    ├── AgentPipeline.tsx     # Animated pipeline visualization of the execution plan
    ├── TraceExplorer.tsx     # Historical observability dashboard
    └── TraceLog.tsx          # Individual trace record card component
```

---

## 🛠️ Tech Stack

| Technology | Version | Role |
|---|---|---|
| Next.js | 16 (App Router) | Framework, routing, SSR |
| React | 19 | UI component library |
| Tailwind CSS | v4 | Utility-first styling |
| Framer Motion | 12 | Pipeline and transition animations |
| Lucide React | Latest | Icon system |
| TypeScript | 5 | Type safety |
| clsx / tailwind-merge | Latest | Conditional class name utilities |

---

## 🚀 Getting Started

### Prerequisites
- **Node.js 18+**
- The Python backend must be running on `http://127.0.0.1:8000`

### Installation

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)** in your browser.

### Linting

```bash
npm run lint
```

---

## 🔗 Backend API Integration

The frontend communicates with these backend endpoints:

| Method | Endpoint | Used By |
|---|---|---|
| `POST` | `/tasks` | `TaskRunner` — starts a new agent workflow |
| `GET` | `/tasks/{thread_id}/stream` | `EventStreamViewer` — SSE live event feed |
| `POST` | `/tasks/{thread_id}/approve` | `EventStreamViewer` — HITL approval button |
| `POST` | `/tasks/{thread_id}/reject` | `EventStreamViewer` — HITL reject button |
| `GET` | `/traces` | `TraceExplorer` — historical trace records |

---

## 🎨 Design System

The UI uses CSS custom properties defined in `globals.css` for consistent theming:

| Variable | Value | Usage |
|---|---|---|
| `--background` | `#09090b` | Page background |
| `--surface` | `rgba(255,255,255,0.03)` | Glass panel fills |
| `--border` | `rgba(255,255,255,0.07)` | Subtle panel borders |
| `--blue` | `#3b82f6` | Supervisor identity |
| `--purple` | `#a855f7` | Research Agent identity |
| `--cyan` | `#06b6d4` | Coder Agent identity |
| `--green` | `#10b981` | Writer Agent / success states |
| `--yellow` | `#f59e0b` | Reviewer Agent identity |
| `--red` | `#ef4444` | Human Review / error states |
