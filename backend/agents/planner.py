import json

from graph.state import WorkflowState
from prompts.planner_prompt import PLANNER_SYSTEM_PROMPT


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
        system_prompt: str,
        user_prompt: str,
    ):
        return self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )

    def parse_response(self, response: str):
        try:
            return json.loads(response)

        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}")

            if start == -1 or end == -1:
                raise ValueError("Planner returned invalid JSON.")

            return json.loads(response[start : end + 1])


# ==========================================================
# LangGraph Node
# ==========================================================

def planner_node(state: WorkflowState):
    print("\n========== Planner ==========\n")

    state["current_agent"] = "Planner"
    state.setdefault("execution_trace", []).append("Planner")

    try:
        goal = state["goal"]
        llm = state["llm"]

        planner = Planner(llm)

        system_prompt, user_prompt = planner.build_prompt(goal)

        llm_response = planner.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        content = (
            llm_response.get("content", "")
            if isinstance(llm_response, dict)
            else llm_response
        )

        workflow = planner.parse_response(content)

        usage = (
            llm_response.get("usage", {})
            if isinstance(llm_response, dict)
            else {}
        )

        state["prompt_tokens"] = state.get("prompt_tokens", 0) + usage.get(
            "prompt_tokens",
            0,
        )

        state["completion_tokens"] = state.get(
            "completion_tokens",
            0,
        ) + usage.get(
            "completion_tokens",
            0,
        )

        state["total_tokens"] = state.get("total_tokens", 0) + usage.get(
            "total_tokens",
            0,
        )

        # Store the complete planner output
        state["plan"] = workflow

        # Extract planner metadata
        state["workflow_name"] = workflow.get(
            "workflow_name",
            "Untitled Workflow",
        )

        state["execution_mode"] = workflow.get(
            "execution",
            "parallel",
        )

        state["reasoning"] = workflow.get(
            "reasoning",
            "",
        )

        # Dynamic tasks
        state["tasks"] = workflow.get("tasks", [])
        state["research_results"] = []
        state["active_nodes"] = []
        state["completed_nodes"] = []
        state["failed_nodes"] = []
        state["status"] = "Planner Completed"

        print("\n========== Workflow Plan ==========\n")
        print(f"Workflow : {state['workflow_name']}")
        print(f"Execution: {state['execution_mode']}")
        print(f"Reason   : {state['reasoning']}")
        print(f"Tasks    : {len(state['tasks'])}\n")

        for index, task in enumerate(state["tasks"], start=1):
            print(
                f"{index}. "
                f"{task.get('title', 'Untitled Task')} "
                f"[{task.get('specialization', 'General')}] "
                f"Priority: {task.get('priority', 'medium')}"
            )

        print("\nPlanner Finished Successfully")

    except Exception as error:
        state["status"] = "Planner Failed"
        state["error"] = str(error)
        print(error)

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
            return {
                "content": """
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
                """,
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 150,
                    "total_tokens": 250,
                },
            }

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
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }

    result = planner_node(state)

    print("\n========== Planner Output ==========\n")
    print(json.dumps(result["plan"], indent=4))
    print("\n========== Token Usage ==========\n")
    print(f"Prompt tokens: {result['prompt_tokens']}")
    print(f"Completion tokens: {result['completion_tokens']}")
    print(f"Total tokens: {result['total_tokens']}")