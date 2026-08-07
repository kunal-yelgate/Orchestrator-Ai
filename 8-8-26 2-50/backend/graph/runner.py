"""
runner.py

Manual sequential runner for the workflow's node functions.
Used instead of workflow.invoke() so execution can start at
any node (needed for rollback/resume) and so a checkpoint can
be saved after every single node — not just at graph completion.

Mirrors the exact node order defined in graph/builder.py.
If you add/reorder nodes there, update NODE_SEQUENCE here too.
"""

from agents.planner import planner_node
from agents.retrieval_agent import retriever_node
from agents.task_splitter import task_splitter_node
from agents.researcher import researcher_node_1, researcher_node_2
from agents.summarizer import summarizer_node
from agents.verifier import verifier_node

from utils.checkpoint import save_checkpoint

# Retriever always stays in the sequence (so checkpoint step indices never
# shift). It's a cheap no-op whenever the Planner decided retrieval wasn't
# needed for this goal — see agents/retrieval_agent.py:retriever_node().
NODE_SEQUENCE = [
    ("Planner", planner_node),
    ("Retriever", retriever_node),
    ("TaskSplitter", task_splitter_node),
    ("ResearchAgent1", researcher_node_1),
    ("ResearchAgent2", researcher_node_2),
    ("Summarizer", summarizer_node),
    ("Verifier", verifier_node),
]


def node_names() -> list:
    return [name for name, _ in NODE_SEQUENCE]


def run_workflow(state: dict, start_index: int = 0) -> dict:
    """
    Runs NODE_SEQUENCE starting at start_index (0 = from the beginning).
    Saves a checkpoint to disk after every node completes.
    """
    for index in range(start_index, len(NODE_SEQUENCE)):
        name, node_fn = NODE_SEQUENCE[index]
        state = node_fn(state)
        save_checkpoint(state, name, index)

    return state