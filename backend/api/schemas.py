from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


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
    final_output: Dict[str, Any] = Field(default_factory=dict)
    status: str = ""
    error: str = ""
    # step_index / agent_name of the last node that ran — lets the frontend
    # know exactly where on the graph execution currently sits, so it can
    # highlight the right node and fetch checkpoints from there.
    last_step_index: Optional[int] = None
    last_agent_name: Optional[str] = None


class UploadResponse(BaseModel):
    path: str
    filename: str


class WorkflowSummary(BaseModel):
    workflow_id: str
    conversation_name: str
    created_at: str


class CheckpointSummary(BaseModel):
    step_index: int
    agent_name: str
    timestamp: str
    status: str
    file: str


class RollbackRequest(BaseModel):
    # The checkpoint "file" value returned by GET /workflows/{id}/checkpoints.
    # Execution resumes at the node immediately AFTER this checkpoint.
    checkpoint_file: str
