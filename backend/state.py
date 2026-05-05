from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # The list of messages in the conversation
    messages: Annotated[List[BaseMessage], add_messages]
    # The current task routing step
    next_step: str
    # Results from specialists
    results: dict
    # Current agent confidence (0-1)
    agent_confidence: float
    # Any human feedback or approval status
    human_approval: str
    # The final output to return to the user
    final_output: str
    # Thread ID for event bus routing
    thread_id: str
    # Metrics for trace logging
    metrics: dict
