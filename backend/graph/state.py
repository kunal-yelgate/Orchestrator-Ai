from typing import TypedDict, List, Dict, Any


class WorkflowState(TypedDict):
    """
    Shared state passed between all LangGraph nodes.
    """

    # ===================================================
    # Workflow Information
    # ===================================================

    workflow_id: str

    conversation_name: str

    created_at: str

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

    plan: Dict[str, Any]

    # Set by the Planner: True when the goal mentions a document/knowledge
    # source or files were uploaded with the request. Consumed by the
    # Retriever node to decide whether to actually run retrieval.
    needs_retrieval: bool

    # ===================================================
    # Retriever
    # ===================================================

    # Paths to uploaded/attached documents (pdf, txt, md).
    documents: List[str]

    # Output of the Retriever node:
    # {
    #   "ran": bool,
    #   "found": bool,
    #   "answer": str,
    #   "documents_used": List[str],
    #   "chunks_used": List[str],
    # }
    retrieval: Dict[str, Any]

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
