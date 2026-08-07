import json

from graph.state import WorkflowState
from prompts.planner_prompt import (
    PLANNER_SYSTEM_PROMPT,
)


class Planner:
    """
    Planner Agent

    Converts a user goal into a workflow graph.
    """

    def __init__(self, llm_provider):

        self.llm = llm_provider

    def build_prompt(self, goal: str):

        system_prompt = PLANNER_SYSTEM_PROMPT

        user_prompt = f"""
Create an execution workflow for the following goal.

Goal:

{goal}

Return ONLY valid JSON.
"""

        return system_prompt, user_prompt

    def call_llm(

        self,

        system_prompt,

        user_prompt,

    ):

        response = self.llm.generate(

            system_prompt=system_prompt,

            user_prompt=user_prompt,

            temperature=0.2,

        )

        return response

    def parse_response(self, response):

        try:

            return json.loads(response)

        except Exception:

            start = response.find("{")

            end = response.rfind("}")

            if start == -1 or end == -1:

                raise ValueError("Planner returned invalid JSON.")

            return json.loads(response[start:end + 1])


# ==========================================================
# LangGraph Node
# ==========================================================

def planner_node(state: WorkflowState):

    print("\n========== Planner ==========\n")

    state["current_agent"] = "Planner"

    if "execution_trace" not in state:
        state["execution_trace"] = []

    state["execution_trace"].append("Planner")

    try:

        goal = state["goal"]

        llm = state["llm"]

        planner = Planner(llm)

        system_prompt, user_prompt = planner.build_prompt(goal)

        response = planner.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        workflow = planner.parse_response(response)

        # Store the complete planner output
        state["plan"] = workflow

        # =====================================================
        # Extract Planner Metadata
        # =====================================================

        state["workflow_name"] = workflow.get(
            "workflow_name",
            "Untitled Workflow"
        )

        state["execution_mode"] = workflow.get(
            "execution",
            "parallel"
        )

        state["reasoning"] = workflow.get(
            "reasoning",
            ""
        )

        # =====================================================
        # Dynamic Tasks
        # =====================================================

        state["tasks"] = workflow.get(
            "tasks",
            []
        )

        state["research_results"] = []

        state["active_nodes"] = []

        state["completed_nodes"] = []

        state["failed_nodes"] = []

        state["status"] = "Planner Completed"

        print("\n========== Workflow Plan ==========\n")

        print(f"Workflow : {state['workflow_name']}")
        print(f"Execution: {state['execution_mode']}")
        print(f"Reason   : {state['reasoning']}")
        print(f"Tasks    : {len(state['tasks'])}")

        print()

        for index, task in enumerate(state["tasks"], start=1):

            print(
                f"{index}. "
                f"{task['title']} "
                f"[{task['specialization']}] "
                f"Priority: {task['priority']}"
            )

        print("Planner Finished Successfully")

    except Exception as e:

        state["status"] = "Planner Failed"

        state["error"] = str(e)

        print(e)

    return state


# ==========================================================
# Local Testing
# ==========================================================

if __name__ == "__main__":

    class DummyLLM:

        def generate(
            self,
            system_prompt,
            user_prompt,
            temperature=0.2,
        ):

            return """
            {
                "workflow_name": "Research Workflow",
                "execution": "parallel",
                "reasoning": "The goal can be divided into independent research tasks.",
                "tasks": [
                    {
                        "id": "task_1",
                        "title": "History",
                        "description": "Research historical background.",
                        "specialization": "History",
                        "priority": "high"
                    },
                    {
                        "id": "task_2",
                        "title": "Architecture",
                        "description": "Study system architecture.",
                        "specialization": "Architecture",
                        "priority": "high"
                    },
                    {
                        "id": "task_3",
                        "title": "Applications",
                        "description": "Research real-world applications.",
                        "specialization": "Applications",
                        "priority": "medium"
                    }
                ]
            }
            """

    state = {

        "goal": "Research Artificial Intelligence",

        "llm": DummyLLM(),

        "plan": {},

        "current_agent": "",

        "execution_trace": [],

        "status": "",

        "error": "",

        "workflow_name": "",

        "execution_mode": "",

        "reasoning": "",

        "tasks": [],

        "research_results": [],

        "active_nodes": [],

        "completed_nodes": [],

        "failed_nodes": [],
    }

    result = planner_node(state)

    print("\n========== Planner Output ==========\n")

    print(json.dumps(result["plan"], indent=4))
