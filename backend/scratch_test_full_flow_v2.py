import os
import logging
import sys
from main import app
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
# Set encoding for stdout to utf-8
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def test_full_flow():
    print("Starting full flow test...")
    config = {"configurable": {"thread_id": "full-flow-test-2"}}
    inputs = {
        "messages": [HumanMessage(content="Search for the current weather in Tokyo and save it to a file called tokyo.txt")],
        "thread_id": "full-flow-test-2",
    }
    
    try:
        for output in app.stream(inputs, config=config):
            for node_name, node_output in output.items():
                print(f"--- Node: {node_name} ---")
                if "next_step" in node_output:
                    print(f"Next Step: {node_output['next_step']}")
                if "current_step_index" in node_output:
                    print(f"Step Index: {node_output['current_step_index']}")
    except Exception as e:
        print(f"Error during flow: {e}")

if __name__ == "__main__":
    test_full_flow()
