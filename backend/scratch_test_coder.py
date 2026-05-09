import os
from main import coder_agent
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

def test_coder():
    print("Running coder agent...")
    try:
        inputs = {"messages": [HumanMessage(content="Calculate 123 * 456 using python")]}
        result = coder_agent.invoke(inputs)
        print("Coder Result:")
        for msg in result["messages"]:
            print(f"[{type(msg).__name__}]: {msg.content}")
    except Exception as e:
        print(f"Coder error: {e}")

if __name__ == "__main__":
    test_coder()
