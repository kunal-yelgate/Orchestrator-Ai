from langgraph.graph import StateGraph, START, END

from graph.state import WorkflowState

from agents.planner import planner_node
from agents.retrieval_agent import retriever_node
from agents.task_splitter import task_splitter_node
from agents.researcher import (
    researcher_node_1,
    researcher_node_2,
)
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
        "Retriever",
        retriever_node,
    )

    workflow.add_node(
        "TaskSplitter",
        task_splitter_node,
    )

    workflow.add_node(
        "ResearchAgent1",
        researcher_node_1,
    )

    workflow.add_node(
        "ResearchAgent2",
        researcher_node_2,
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

    # Retriever always sits in the sequence, but it's a cheap no-op
    # whenever the Planner decided retrieval wasn't needed
    # (state["needs_retrieval"] is False) — see retriever_node().
    workflow.add_edge(
        "Planner",
        "Retriever",
    )

    workflow.add_edge(
        "Retriever",
        "TaskSplitter",
    )

    workflow.add_edge(
        "TaskSplitter",
        "ResearchAgent1",
    )

    workflow.add_edge(
        "ResearchAgent1",
        "ResearchAgent2",
    )

    workflow.add_edge(
        "ResearchAgent2",
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