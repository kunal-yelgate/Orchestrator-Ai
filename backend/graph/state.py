from langgraph.graph import StateGraph, START, END

from graph.state import WorkflowState

from agents.planner import planner_node
from agents.task_splitter import task_splitter_node
from agents.researcher import (
    researcher_node_1,
    researcher_node_2,
)
from agents.summarizer import summarizer_node
from agents.verifier import verifier_node


def build_workflow():

    workflow = StateGraph(WorkflowState)

    # Register Nodes
    workflow.add_node("Planner", planner_node)
    workflow.add_node("TaskSplitter", task_splitter_node)

    workflow.add_node("ResearchAgent1", researcher_node_1)
    workflow.add_node("ResearchAgent2", researcher_node_2)

    workflow.add_node("Summarizer", summarizer_node)
    workflow.add_node("Verifier", verifier_node)

    # Flow
    workflow.add_edge(START, "Planner")

    workflow.add_edge("Planner", "TaskSplitter")

    # NOTE:
    # For the MVP, execute research nodes one after another.
    # Later you can replace this with true parallel execution.

    workflow.add_edge("TaskSplitter", "ResearchAgent1")
    workflow.add_edge("ResearchAgent1", "ResearchAgent2")
    workflow.add_edge("ResearchAgent2", "Summarizer")

    workflow.add_edge("Summarizer", "Verifier")

    workflow.add_edge("Verifier", END)

    return workflow.compile()