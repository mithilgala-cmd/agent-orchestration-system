"""
main.py — LangGraph workflow with real ReAct agents.
Each node emits events to the EventBus for SSE streaming.
"""
import os
import logging
from typing import Literal

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from state import AgentState
from supervisor import Supervisor
from tools import web_search_tool, execute_python_tool, write_file_tool
from stream import event_bus
from memory import ltm
from observability import AgentTracer

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── LLMs ─────────────────────────────────────────────────────────────────────
_groq_key = os.getenv("GROQ_API_KEY")
_base_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=_groq_key)

# ── Specialist Agents (ReAct) ─────────────────────────────────────────────────
research_agent = create_react_agent(_base_llm, [web_search_tool])
coder_agent    = create_react_agent(_base_llm, [execute_python_tool])
writer_agent   = create_react_agent(_base_llm, [write_file_tool])

# ── Supervisor ────────────────────────────────────────────────────────────────
supervisor = Supervisor()


def _emit(state: AgentState, event_type: str, data: dict):
    event_bus.emit(state.get("thread_id", ""), event_type, data)


# ── Nodes ─────────────────────────────────────────────────────────────────────
def supervisor_node(state: AgentState):
    _emit(state, "node_start", {"node": "Supervisor", "message": "Decomposing task and building execution plan..."})
    result = supervisor.plan(state)
    plan = result.get("results", {}).get("plan", {})
    steps = plan.get("steps", [])
    _emit(state, "plan_ready", {
        "node": "Supervisor",
        "reasoning": plan.get("reasoning", ""),
        "steps": [{"specialist": s["specialist"], "description": s["description"]} for s in steps],
    })
    return result


def _run_specialist(state: AgentState, agent, node_name: str, icon: str) -> dict:
    tid = state.get("thread_id", "")
    _emit(state, "node_start", {"node": node_name, "icon": icon, "message": f"{node_name} starting work..."})

    import time
    start_time = time.time()
    
    with AgentTracer.start_span(node_name.lower().replace(" ", "_")) as span:
        AgentTracer.log_decision(span, node_name, "running")
        result = agent.invoke({"messages": state["messages"]})
        
    duration = time.time() - start_time

    # Initialize metrics if not present
    metrics = state.get("metrics", {})
    metrics["total_tokens"] = metrics.get("total_tokens", 0)
    metrics["prompt_tokens"] = metrics.get("prompt_tokens", 0)
    metrics["completion_tokens"] = metrics.get("completion_tokens", 0)
    metrics["duration"] = metrics.get("duration", 0.0) + duration

    # Extract token usage from final message
    if result["messages"] and hasattr(result["messages"][-1], "response_metadata"):
        usage = result["messages"][-1].response_metadata.get("token_usage", {})
        metrics["total_tokens"] += usage.get("total_tokens", 0)
        metrics["prompt_tokens"] += usage.get("prompt_tokens", 0)
        metrics["completion_tokens"] += usage.get("completion_tokens", 0)

    # Collect tool calls for observability
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                _emit(state, "tool_call", {
                    "node": node_name,
                    "tool": tc["name"],
                    "input": str(tc.get("args", ""))[:300],
                })

    last_content = result["messages"][-1].content if result["messages"] else ""
    _emit(state, "node_finish", {"node": node_name, "result": last_content[:500]})

    return {"messages": result["messages"], "next_step": "review", "metrics": metrics}


def research_node(state: AgentState):
    return _run_specialist(state, research_agent, "Research Agent", "search")


def coder_node(state: AgentState):
    return _run_specialist(state, coder_agent, "Coder Agent", "code")


def writer_node(state: AgentState):
    return _run_specialist(state, writer_agent, "Writer Agent", "pen")


def reviewer_node(state: AgentState):
    _emit(state, "node_start", {"node": "Reviewer", "message": "Validating outputs..."})
    confidence = state.get("agent_confidence", 1.0)
    if confidence < 0.7:
        _emit(state, "awaiting_approval", {
            "node": "Reviewer",
            "message": "Confidence below threshold. Escalating to human review.",
        })
        return {"next_step": "human_review"}

    # Save completed task to long-term memory
    messages = state.get("messages", [])
    if messages:
        task_text = messages[0].content
        result_text = messages[-1].content
        ltm.save_memory(task_text, result_text)

    _emit(state, "node_finish", {"node": "Reviewer", "result": "All outputs validated."})
    return {"next_step": "finish"}


def human_review_node(state: AgentState):
    _emit(state, "awaiting_approval", {
        "node": "Human Review",
        "message": "Paused. Waiting for human approval to proceed.",
    })
    return {"human_approval": "pending", "next_step": "finish"}


# ── Routing ───────────────────────────────────────────────────────────────────
def route(state: AgentState) -> Literal["research", "coder", "writer", "review", "human_review", "finish"]:
    return state.get("next_step", "finish")


# ── Graph ─────────────────────────────────────────────────────────────────────
workflow = StateGraph(AgentState)
workflow.add_node("supervisor",   supervisor_node)
workflow.add_node("research",     research_node)
workflow.add_node("coder",        coder_node)
workflow.add_node("writer",       writer_node)
workflow.add_node("review",       reviewer_node)
workflow.add_node("human_review", human_review_node)

workflow.set_entry_point("supervisor")

workflow.add_conditional_edges("supervisor", route, {
    "research":     "research",
    "coder":        "coder",
    "writer":       "writer",
    "review":       "review",
    "human_review": "human_review",
    "finish":       END,
})
workflow.add_edge("research", "review")
workflow.add_edge("coder",    "review")
workflow.add_edge("writer",   "review")
workflow.add_conditional_edges("review", route, {
    "human_review": "human_review",
    "finish":       END,
})
workflow.add_edge("human_review", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["human_review"])


if __name__ == "__main__":
    logger.info("Starting test workflow run — thread_id=test-1")
    config = {"configurable": {"thread_id": "test-1"}}
    inputs = {
        "messages": [HumanMessage(content="What is the capital of France? Answer briefly.")],
        "thread_id": "test-1",
    }
    for output in app.stream(inputs, config=config):
        logger.info("Graph output: %s", output)
