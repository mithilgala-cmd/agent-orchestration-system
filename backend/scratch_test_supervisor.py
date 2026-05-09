import os
from supervisor import Supervisor, ExecutionPlan
from state import AgentState
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

def test_supervisor():
    supervisor = Supervisor()
    state: AgentState = {
        "messages": [HumanMessage(content="Write a python function for fibonacci")],
        "thread_id": "test-supervisor",
        "next_step": "",
        "metrics": {},
        "agent_confidence": 1.0
    }
    
    print("Planning...")
    try:
        result = supervisor.plan(state)
        print(f"Plan Result: {result}")
    except Exception as e:
        print(f"Supervisor error: {e}")

if __name__ == "__main__":
    test_supervisor()
