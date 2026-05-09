import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def test_llm():
    api_key = os.getenv("GROQ_API_KEY")
    print(f"API Key found: {bool(api_key)}")
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
    try:
        response = llm.invoke("Hi, are you working?")
        print(f"LLM Response: {response.content}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_llm()
