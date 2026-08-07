from graph.state import WorkflowState


def summarizer_node(state: WorkflowState):
    """
    Summarizer Agent

    Combines the outputs from all Research Agents
    into one structured summary.
    """

    print("Summarizer Running...")

    state["current_agent"] = "Summarizer"
    state["execution_trace"].append("Summarizer")

    research_results = state.get("research_results", [])

    if not research_results:
        state["summary"] = {
            "title": "No Research Available",
            "content": "No research results were found.",
            "status": "failed"
        }

        return state

    combined_text = ""

    for item in research_results:

        title = item.get("title", "Untitled")

        result = item.get("result", {})

        summary = result.get("summary", "")

        combined_text += f"\n### {title}\n"
        combined_text += summary + "\n"

    state["summary"] = {
        "title": "Final Summary",
        "content": combined_text.strip(),
        "research_count": len(research_results),
        "status": "completed"
    }

    return state