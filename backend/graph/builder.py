from typing import TypedDict, List, Dict, Any


class WorkflowState(TypedDict):
    """
    Shared state passed between all LangGraph nodes.
    Every node reads from this state and updates it.
    """

    # Workflow Info
    workflow_id: str
    goal: str
    status: str

    # Planner
    plan: str

    # Task Splitter
    tasks: List[Dict[str, Any]]

    # Parallel Research Results
    research_agent_1: Dict[str, Any]
    research_agent_2: Dict[str, Any]

    # Combined Results
    research_results: List[Dict[str, Any]]

    # Summarizer
    summary: Dict[str, Any]

    # Verifier
    verification: Dict[str, Any]

    # Final Output
    final_output: Dict[str, Any]

    # Execution Tracking
    current_agent: str
    execution_trace: List[str]

    # Error Handling
    error: str