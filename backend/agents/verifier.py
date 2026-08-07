from graph.state import WorkflowState


def verifier_node(state: WorkflowState):
    """
    Verifier Agent

    Checks whether:
    - All research tasks completed
    - Summary exists
    - Workflow can be marked completed
    """

    print("Verifier Running...")

    state["current_agent"] = "Verifier"
    state["execution_trace"].append("Verifier")

    research_results = state.get("research_results", [])
    summary = state.get("summary", {})

    issues = []

    # Check research results
    if not research_results:
        issues.append("No research results found.")

    # Check summary
    if not summary:
        issues.append("Summary not generated.")

    elif isinstance(summary, dict):
        if not summary.get("content"):
            issues.append("Summary content is empty.")

    # Verification Result
    verified = len(issues) == 0

    confidence = 1.0 if verified else 0.4

    state["verification"] = {
        "verified": verified,
        "confidence": confidence,
        "issues": issues
    }

    # Final Output
    state["final_output"] = {
        "workflow_id": state["workflow_id"],
        "goal": state["goal"],
        "summary": summary,
        "verification": state["verification"]
    }

    # Workflow Status
    state["status"] = "completed" if verified else "failed"

    return state