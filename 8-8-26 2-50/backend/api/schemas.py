from pydantic import BaseModel, Field
from typing import List, Dict, Any


class OrchestrateRequest(BaseModel):
    goal: str
    provider: str
    # Server-side paths of previously uploaded documents (see POST /upload).
    # When non-empty, the Retriever always runs regardless of what the
    # Planner's own plan says.
    documents: List[str] = Field(default_factory=list)


class OrchestrateResponse(BaseModel):
    workflow_id: str
    execution_trace: List[str]
    retrieval: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any]
    verification: Dict[str, Any]


class UploadResponse(BaseModel):
    path: str
    filename: str