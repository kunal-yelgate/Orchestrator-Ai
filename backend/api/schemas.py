from typing import Any, Dict, List

from pydantic import BaseModel, Field


class OrchestrateRequest(BaseModel):
    goal: str
    provider: str
    documents: List[str] = Field(default_factory=list)


class OrchestrateResponse(BaseModel):
    workflow_id: str
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    execution_trace: List[str] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    verification: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float = 0.0
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost: float = 0.0
    provider: str = ""
    model: str = ""
    retry_count: int = 0
    budget: Dict[str, Any] = Field(default_factory=dict)

class UploadResponse(BaseModel):
    path: str
    filename: str
