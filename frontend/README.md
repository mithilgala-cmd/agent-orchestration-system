# Agent Orchestrator Dashboard

This directory contains the **Next.js** frontend dashboard for the Multi-Agent Orchestration System. It serves as the primary interface for monitoring agent activities, observing execution traces, and providing Human-in-the-Loop (HITL) approvals.

## ✨ Key Capabilities

- **Real-Time Event Streaming**: Connects to the FastAPI backend via Server-Sent Events (SSE) to display a live feed of agent reasoning, tool usage, and state transitions.
- **Human-in-the-Loop (HITL)**: Specialized UI components that intercept workflow execution when a sensitive action (like running code) requires manual approval.
- **Trace Explorer**: A dedicated observability tab that fetches and visualizes historical task execution data from the SQLite metrics database, displaying token consumption, estimated costs, and run durations.
- **Premium Aesthetics**: Built with a sleek, dark-mode glassmorphic design utilizing Tailwind CSS, Lucide React icons, and subtle micro-animations for an enterprise-grade feel.

## 🛠️ Tech Stack

- **Framework**: [Next.js 14](https://nextjs.org/) (App Router)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Data Fetching**: Native Fetch & Server-Sent Events (`EventSource`)

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- The Python Backend must be running on `http://127.0.0.1:8000`

### Installation

Install the project dependencies:

```bash
npm install
```

### Running the Development Server

Start the application:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the dashboard.

## 📂 Directory Structure

- `src/app/page.tsx`: The main application entry point, containing the tabbed navigation layout.
- `src/app/globals.css`: Global styles including custom glassmorphic utility classes and animations.
- `src/components/TaskRunner.tsx`: The input form for dispatching new orchestration tasks to the backend.
- `src/components/EventStreamViewer.tsx`: The real-time console rendering the live SSE event feed from the active agent run.
- `src/components/TraceExplorer.tsx`: The historical observability dashboard visualizing past runs.

## 🎨 Design Philosophy
The UI follows strict modern web design principles:
- **No pure blacks or whites**: Backgrounds use deep zinc/slate tones (`#09090b`), and text uses varied opacities for depth.
- **Subtle borders**: 1px borders with low opacity (`border-white/10`) to separate sections without harsh lines.
- **Semantic colors**: Clear visual hierarchy for agent identities (e.g., Blue for Supervisor, Purple for Researcher, Cyan for Coder).
