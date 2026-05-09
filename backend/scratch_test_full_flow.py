import os
import logging
from main import app
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

def test_full_flow():
    print("Starting full flow test...")
    config = {"configurable": {"thread_id": "full-flow-test"}}
    inputs = {
        "messages": [HumanMessage(content="Search for the current weather in Tokyo and save it to a file called tokyo.txt")],
        "thread_id": "full-flow-test",
    }
    
    # We expect: Supervisor -> Research -> Review -> Writer -> Review -> Finish
    for output in app.stream(inputs, config=config):
        print(f"--- Node Output ---")
        print(output)

if __name__ == "__main__":
    test_full_flow()
