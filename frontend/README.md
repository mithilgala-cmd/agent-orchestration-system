# Sentinel Frontend: Real-Time AI Dashboard

A modern, glassmorphic Next.js interface for orchestrating, approving, and tracing multi-agent workflows.

## 🚀 Key Features

- **📡 Real-Time SSE Integration**: Consumes Server-Sent Events from the backend to visualize agent thought processes live.
- **🛡️ Approval Workflow**: A dedicated UI for Human-in-the-Loop gates, allowing users to inspect and approve agent actions.
- **📊 Trace Explorer**: A historical log viewer for reviewing past task outcomes, token costs, and duration.
- **✨ Premium UI/UX**: Built with **Tailwind CSS**, **Lucide React**, and custom glassmorphic components for a high-end "sentinel" feel.

---

## 🏗️ Technical Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Streaming**: Native EventSource (SSE)
- **State Management**: React `useState` + `useEffect` for live event handling.

---

## 🧩 Core Components

| Component | Responsibility |
|---|---|
| `EventStreamViewer.tsx` | Main real-time terminal. Handles SSE parsing and status rendering. |
| `TraceExplorer.tsx` | Data table for historical traces. Fetches from `/traces`. |
| `TaskRunner.tsx` | Input interface for dispatching new tasks to the orchestrator. |
| `AgentPipeline.tsx` | Visual representation of the active Specialist in the workflow. |

---

## ⚙️ Development

### Setup
```bash
npm install
```

### Running Locally
```bash
npm run dev
```

The app will be available at **http://localhost:3000**. It expects the backend to be running at **http://localhost:8000**.

### Environment Variables
Create a `.env.local` if you need to point to a different backend:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 💡 Engineering Detail: SSE Handling
The frontend uses a custom event listener loop in `EventStreamViewer` to manage the lifecycle of a task:
1.  **Initialize**: Subscribes to `/tasks/{id}/stream`.
2.  **Dispatch**: Maps JSON events (`node_start`, `tool_call`, `node_finish`) to UI state updates.
3.  **Interrupt**: Detects `awaiting_approval` and renders the HITL modal.
4.  **Cleanup**: Automatically closes the `EventSource` when the `done` event is received.

---
*Visualizing the future of autonomous systems.*
