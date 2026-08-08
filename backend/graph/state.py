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

<<<<<<< HEAD
    # =====================================================
    # Planner Output
    # =====================================================
=======
    # Name of the provider that automatic fallback will switch to if
    # `provider` fails (e.g. "gemini" when provider == "groq"). Set by
    # create_state(); "" when no fallback is configured/available.
    fallback_provider: str

    # Appended to by llm/fallback_provider.py:FallbackProvider whenever
    # the primary provider fails and the fallback is used instead.
    # Each entry: {"node": str, "from_provider": str, "to_provider": str, "reason": str}
    provider_events: List[Dict[str, Any]]

    # ===================================================
    # Planner
    # ===================================================
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0

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

<<<<<<< HEAD
    # =====================================================
    # Final Outputs
    # =====================================================
=======
    research_results: List[Dict[str, Any]]

    # Entries for any research agent that failed on its own task. The
    # workflow does NOT halt because of these -- see agents/researcher.py.
    # Each entry: {"agent": str, "task_id": str, "title": str, "error": str}
    research_failures: List[Dict[str, Any]]

    # True whenever at least one research agent failed but at least one
    # other succeeded, so the Summarizer proceeded on partial results.
    partial_failure: bool

    # ===================================================
    # Summarizer
    # ===================================================
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0

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