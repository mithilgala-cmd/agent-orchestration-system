import asyncio
from main import app
from memory import ltm

async def test_workflow():
    print("--- Starting E2E Test ---")
    
    # 1. Test Research & Code task
    inputs = {"messages": [("user", "Search for the latest AI news and write a summary script.")]}
    config = {"configurable": {"thread_id": "test_e2e_1"}}
    
    print("\n[Step 1] Running Supervisor Planning...")
    for output in app.stream(inputs, config=config):
        for key, value in output.items():
            print(f"Node '{key}' completed.")
            if "next_step" in value:
                print(f"Next step: {value['next_step']}")

    # 2. Test Memory Retrieval
    print("\n[Step 2] Testing Memory Retrieval...")
    ltm.save_memory("Test Task", "Test Result", {"type": "test"})
    results = ltm.query_memory("Test Task")
    if len(results) > 0:
        print("Memory retrieval successful.")
    else:
        print("Memory retrieval failed.")

    print("\n--- E2E Test Completed ---")

if __name__ == "__main__":
    asyncio.run(test_workflow())
