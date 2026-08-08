import operator
from typing import Annotated, Any, Dict, List, TypedDict


class WorkflowState(TypedDict):
    """
    Shared LangGraph Workflow State
    """

    # =====================================================
    # Workflow Information
    # =====================================================

    workflow_id: str
    conversation_name: str
    created_at: str

    goal: str

    status: str
    error: str

    # =====================================================
    # LLM Configuration
    # =====================================================

    provider: str
    model: str
    api_key: str
    hf_provider: str

    llm: Any

    # =====================================================
    # Planner Output
    # =====================================================

    plan: Dict[str, Any]

    workflow_name: str
    execution_mode: str
    reasoning: str

    # =====================================================
    # Task Management
    # =====================================================

    tasks: List[Dict[str, Any]]

    # Current task executed by one Research Agent
    current_task: Dict[str, Any]

    # =====================================================
    # Parallel Research Results
    # =====================================================

    research_results: Annotated[
        List[Dict[str, Any]],
        operator.add,
    ]

    # =====================================================
    # Final Outputs
    # =====================================================

    summary: Dict[str, Any]
    verification: Dict[str, Any]
    final_output: Dict[str, Any]

    # =====================================================
    # Execution Tracking
    # =====================================================

    current_agent: str

    execution_trace: Annotated[
        List[str],
        operator.add,
    ]

    execution_time: float

    active_nodes: List[str]

    completed_nodes: Annotated[
        List[str],
        operator.add,
    ]

    failed_nodes: Annotated[
        List[str],
        operator.add,
    ]
    retry_count: int
    # =====================================================
    # Token & Cost Tracking
    # =====================================================

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float

    # =====================================================
    # Approval / Version
    # =====================================================

    approved: bool
    workflow_version: str