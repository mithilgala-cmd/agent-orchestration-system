import os
from typing import List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()


class LongTermMemory:
    def __init__(self, persist_directory: str = "./chroma_db"):
        # Uses a small local model — no API key required
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )
        self.vector_store = Chroma(
            collection_name="agent_memory",
            embedding_function=self.embeddings,
            persist_directory=persist_directory,
        )

    def save_memory(self, task: str, result: str, metadata: Optional[dict] = None):
        """Save a completed task and its result to semantic memory."""
        doc = Document(
            page_content=f"Task: {task}\nResult: {result}",
            metadata=metadata or {},
        )
        self.vector_store.add_documents([doc])

    def query_memory(self, query: str, k: int = 3) -> List[Document]:
        """Retrieve the most relevant past experiences."""
        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception:
            return []


# Singleton for reuse across modules
ltm = LongTermMemory()
