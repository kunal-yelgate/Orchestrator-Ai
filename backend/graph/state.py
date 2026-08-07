from typing import TypedDict, List, Dict, Any, Annotated
import operator


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
        operator.add
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

##(Implement dynamic workflow execution engine)
