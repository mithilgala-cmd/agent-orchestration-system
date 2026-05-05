"""
api.py — FastAPI with CORS, SSE streaming, and background task execution.
"""
import asyncio
import uuid
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from stream import event_bus
import db

logger = logging.getLogger(__name__)


# ── Lazy import of the compiled graph (avoids circular import during startup) ──
def _get_app():
    from main import app as agent_app
    return agent_app


# ── Models ────────────────────────────────────────────────────────────────────
# Represents the core request structure for initializing an agentic task
class TaskRequest(BaseModel):
    task: str


class TaskResponse(BaseModel):
    thread_id: str
    status: str


# ── FastAPI ───────────────────────────────────────────────────────────────────
api = FastAPI(title="Agent Orchestration API", version="2.0.0")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Background graph runner ───────────────────────────────────────────────────
def _run_graph(thread_id: str, task: str):
    """Runs the LangGraph workflow synchronously in a thread pool worker."""
    from langchain_core.messages import HumanMessage

    agent_app = _get_app()
    config = {"configurable": {"thread_id": thread_id}}
    inputs = {"messages": [HumanMessage(content=task)], "thread_id": thread_id}

    try:
        for chunk in agent_app.stream(inputs, config=config):
            # Events are already emitted inside each node via event_bus.emit()
            pass

        # Check if we stopped at an interrupt
        state = agent_app.get_state(config)
        metrics = state.values.get("metrics", {}) if state.values else {}
        
        if state.next and "human_review" in state.next:
            # Already emitted awaiting_approval inside the node — just return
            db.save_trace(thread_id, task, "paused", metrics)
            pass
        else:
            db.save_trace(thread_id, task, "completed", metrics)
            event_bus.emit(thread_id, "finished", {"message": "Task completed successfully."})
    except Exception as e:
        logger.error(f"Graph error for {thread_id}: {e}")
        db.save_trace(thread_id, task, "error", {})
        event_bus.emit(thread_id, "error", {"message": str(e)})
    finally:
        event_bus.emit_sentinel(thread_id)


# ── Endpoints ─────────────────────────────────────────────────────────────────
@api.post("/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """Create a new task and start the agent workflow in the background."""
    thread_id = str(uuid.uuid4())
    event_bus.create_channel(thread_id)

    # Run the blocking graph in a thread pool so the API returns immediately
    asyncio.get_event_loop().run_in_executor(None, _run_graph, thread_id, request.task)

    return TaskResponse(thread_id=thread_id, status="started")


@api.get("/tasks/{thread_id}/stream")
async def stream_task(thread_id: str):
    """SSE endpoint — streams real-time agent events to the frontend."""
    q = event_bus.get_channel(thread_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Task not found")

    async def generator():
        while True:
            # Async-friendly blocking get (runs in thread pool)
            event = await asyncio.to_thread(q.get)
            if event is None:  # sentinel — stream is done
                yield {"data": json.dumps({"type": "done", "data": {}})}
                break
            yield {"data": json.dumps(event)}

    return EventSourceResponse(generator())


@api.get("/tasks/{thread_id}/status")
async def get_task_status(thread_id: str):
    """Get the current LangGraph state for a thread."""
    agent_app = _get_app()
    config = {"configurable": {"thread_id": thread_id}}
    state = agent_app.get_state(config)
    if not state:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"values": state.values, "next": list(state.next)}


@api.post("/tasks/{thread_id}/approve")
async def approve_task(thread_id: str):
    """Resume a graph that is paused at a human_review interrupt."""
    agent_app = _get_app()
    config = {"configurable": {"thread_id": thread_id}}

    # Re-create the channel for the resumed stream
    event_bus.create_channel(thread_id)
    asyncio.get_event_loop().run_in_executor(
        None, lambda: _resume_graph(thread_id, config, agent_app)
    )
    return {"status": "resumed"}


@api.post("/tasks/{thread_id}/reject")
async def reject_task(thread_id: str):
    """Reject a task and close its event channel."""
    event_bus.emit(thread_id, "rejected", {"message": "Task rejected by human reviewer."})
    event_bus.emit_sentinel(thread_id)
    event_bus.close_channel(thread_id)
    return {"status": "rejected"}


@api.get("/traces")
async def get_all_traces():
    """Returns a list of all historical traces for the Trace Explorer UI."""
    return {"traces": db.get_traces()}


def _resume_graph(thread_id: str, config: dict, agent_app):
    task = "Resumed Task"
    try:
        # Fetch the current state to get original task name if needed (optional)
        state = agent_app.get_state(config)
        if state and state.values and state.values.get("messages"):
            task = state.values["messages"][0].content

        for chunk in agent_app.stream(None, config=config):
            pass
            
        final_state = agent_app.get_state(config)
        metrics = final_state.values.get("metrics", {}) if final_state.values else {}
        db.save_trace(thread_id, task, "completed", metrics)
        event_bus.emit(thread_id, "finished", {"message": "Task completed after human approval."})
    except Exception as e:
        db.save_trace(thread_id, task, "error", {})
        event_bus.emit(thread_id, "error", {"message": str(e)})
    finally:
        event_bus.emit_sentinel(thread_id)


@api.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
