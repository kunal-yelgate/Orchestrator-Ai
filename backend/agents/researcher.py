from graph.state import WorkflowState


def researcher_node_1(state: WorkflowState):
    """
    Research Agent 1
    Performs research for the first assigned task.
    """

    print("Research Agent 1 Running...")

    state["current_agent"] = "ResearchAgent1"
    state["execution_trace"].append("ResearchAgent1")

    # Read first task (if available)
    task = state["tasks"][0] if state["tasks"] else {}

    state["research_agent_1"] = {
        "task_id": task.get("task_id", "task_001"),
        "title": task.get("title", "Research Task 1"),
        "result": {
            "summary": "Dummy research result for Research Agent 1.",
            "source": "LLM",
            "status": "completed"
        }
    }

    return state


def researcher_node_2(state: WorkflowState):
    """
    Research Agent 2
    Performs research for the second assigned task.
    """

    print("Research Agent 2 Running...")

    state["current_agent"] = "ResearchAgent2"
    state["execution_trace"].append("ResearchAgent2")

    task = state["tasks"][1] if len(state["tasks"]) > 1 else {}

    state["research_agent_2"] = {
        "task_id": task.get("task_id", "task_002"),
        "title": task.get("title", "Research Task 2"),
        "result": {
            "summary": "Dummy research result for Research Agent 2.",
            "source": "LLM",
            "status": "completed"
        }
    }

    # Merge research outputs for Summarizer
    state["research_results"] = [
        state["research_agent_1"],
        state["research_agent_2"]
    ]

    return state