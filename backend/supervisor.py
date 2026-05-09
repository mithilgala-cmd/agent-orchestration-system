import os
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from state import AgentState
from memory import ltm
from dotenv import load_dotenv

load_dotenv()


class SubTask(BaseModel):
    description: str = Field(description="Clear description of the subtask")
    specialist: str = Field(description="Specialist to assign: 'research', 'coder', or 'writer'")
    expected_output: str = Field(description="What this step should produce")


class ExecutionPlan(BaseModel):
    steps: List[SubTask]
    reasoning: str = Field(description="Why this plan was chosen")


class Supervisor:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.llm = ChatGroq(
            model=model_name,
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.planner_llm = self.llm.with_structured_output(ExecutionPlan)

    def plan(self, state: AgentState) -> dict:
        """Decompose the user request into an execution plan with memory recall."""
        messages = state["messages"]
        user_message = messages[-1].content if messages else ""

        # Recall similar past tasks from long-term memory
        past_experiences = ltm.query_memory(user_message)
        context = "\n".join([doc.page_content for doc in past_experiences]) or "No past experiences found."

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are the Lead Supervisor of an Agentic AI Team. "
                "Decompose the user's request into an ordered list of subtasks. "
                "Assign each subtask to one specialist only: "
                "'research' (web search), 'coder' (Python execution), or 'writer' (file editing). "
                "Keep the plan minimal — 1-3 steps max.\n\n"
                "Relevant past experiences:\n{context}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ])

        chain = prompt | self.planner_llm
        plan: ExecutionPlan = chain.invoke({"messages": messages, "context": context})

        first_specialist = plan.steps[0].specialist if plan.steps else "finish"
        return {
            "next_step": first_specialist,
            "current_step_index": 0,
            "results": {"plan": plan.model_dump()},
        }
