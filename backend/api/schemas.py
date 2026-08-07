from pydantic import BaseModel
from typing import List, Dict, Any


class OrchestrateRequest(BaseModel):
    goal: str
    provider: str


class OrchestrateResponse(BaseModel):
    workflow_id: str
    execution_trace: List[str]
    summary: Dict[str, Any]
    verification: Dict[str, Any]