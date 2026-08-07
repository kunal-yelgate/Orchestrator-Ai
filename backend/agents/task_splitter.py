from pydantic import BaseModel, Field
from typing import List
import json


class Task(BaseModel):
    task_id: str = Field(..., description="Unique Task ID")

    title: str = Field(..., description="Task title")

    agent: str = Field(..., description="Assigned Agent")

    dependencies: List[str] = Field(
        default_factory=list,
        description="Dependent Task IDs"
    )

    status: str = Field(
        default="pending",
        description="Task Status"
    )


class TaskSplitterResponse(BaseModel):
    success: bool

    parallel: bool

    tasks: List[Task]

    

from models.task_model import TaskSplitterResponse
from prompts.splitter_prompt import (
    TASK_SPLITTER_SYSTEM_PROMPT,
    build_task_splitter_prompt,
)


class TaskSplitter:

    def __init__(self, llm_provider):
        """
        llm_provider is an abstraction over Gemini/Ollama/OpenAI.

        Example:
            GeminiProvider()
            OllamaProvider()
        """
        self.llm = llm_provider



def build_prompt(self, goal: str):

    system_prompt = TASK_SPLITTER_SYSTEM_PROMPT

    user_prompt = build_task_splitter_prompt(goal)

    return system_prompt, user_prompt


def call_llm(self, system_prompt: str, user_prompt: str):

    response = self.llm.generate(

        system_prompt=system_prompt,

        user_prompt=user_prompt,

        temperature=0.2
    )

    return response

def parse_response(self, response: str):

    try:

        return json.loads(response)

    except json.JSONDecodeError:

        raise ValueError("Task Splitter returned invalid JSON.")


def validate(self, data):

    return TaskSplitterResponse(**data)



def split_tasks(self, goal: str):

    system_prompt, user_prompt = self.build_prompt(goal)

    llm_response = self.call_llm(
        system_prompt,
        user_prompt
    )

    parsed = self.parse_response(llm_response)

    validated = self.validate(parsed)

    return validated