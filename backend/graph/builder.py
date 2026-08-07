from langgraph.graph import StateGraph, START, END

from graph.state import WorkflowState

from agents.planner import planner_node
from agents.task_splitter import task_splitter_node
from execution.engine import execution_node
from agents.summarizer import summarizer_node
from agents.verifier import verifier_node


def build_workflow():
    """
    Builds the complete Agentic AI Workflow.
    """

    workflow = StateGraph(WorkflowState)

    # ==================================================
    # Register Nodes
    # ==================================================

    workflow.add_node(
        "Planner",
        planner_node,
    )

    workflow.add_node(
        "TaskSplitter",
        task_splitter_node,
    )

    workflow.add_node(
        "Executor",
        execution_node,
    )

    workflow.add_node(
        "Summarizer",
        summarizer_node,
    )

    workflow.add_node(
        "Verifier",
        verifier_node,
    )

    # ==================================================
    # Workflow
    # ==================================================

    workflow.add_edge(
        START,
        "Planner",
    )

    workflow.add_edge(
        "Planner",
        "TaskSplitter",
    )

    workflow.add_edge(
        "TaskSplitter",
        "Executor",
    )

    workflow.add_edge(
        "Executor",
        "Summarizer",
    )

    workflow.add_edge(
        "Summarizer",
        "Verifier",
    )

    workflow.add_edge(
        "Verifier",
        END,
    )

    return workflow.compile()