from typing import TypedDict, List, Dict, Any


class WorkflowState(TypedDict):
    """
    Shared state passed between all LangGraph nodes.
    """

    # ===================================================
    # Workflow Information
    # ===================================================

    workflow_id: str

    goal: str

    status: str

    error: str

    # ===================================================
    # LLM Configuration
    # ===================================================

    provider: str

    model: str

    api_key: str

    hf_provider: str

    llm: Any

    # ===================================================
    # Planner
    # ===================================================

    plan: Dict[str, Any]

    # ===================================================
    # Task Splitter
    # ===================================================

    tasks: List[Dict[str, Any]]

    # ===================================================
    # Research Agents
    # ===================================================

    research_agent_1: Dict[str, Any]

    research_agent_2: Dict[str, Any]

    research_results: List[Dict[str, Any]]

    # ===================================================
    # Summarizer
    # ===================================================

    summary: Dict[str, Any]

    # ===================================================
    # Verifier
    # ===================================================

    verification: Dict[str, Any]

    final_output: Dict[str, Any]

    # ===================================================
    # Execution Tracking
    # ===================================================

    current_agent: str

    execution_trace: List[str]