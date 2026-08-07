from pydantic import BaseModel, Field
from typing import List


class Task(BaseModel):
    task_id: str = Field(...)
    title: str
    agent: str
    dependencies: List[str] = Field(default_factory=list)
    status: str = "pending"


class TaskSplitterResponse(BaseModel):
    success: bool
    parallel: bool
    tasks: List[Task]
