import json

from models.task_model import TaskSplitterResponse
from prompts.splitter_prompt import (
    TASK_SPLITTER_SYSTEM_PROMPT,
    build_task_splitter_prompt,
)


class TaskSplitter:
    """
    Task Splitter Agent
    """

    def __init__(self, llm_provider):
        self.llm = llm_provider

    def build_prompt(self, goal: str):

        system_prompt = TASK_SPLITTER_SYSTEM_PROMPT

        user_prompt = build_task_splitter_prompt(goal)

        return system_prompt, user_prompt

    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
    ):

        response = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )

        return response

    def parse_response(self, response: str):

        try:

            return json.loads(response)

        except json.JSONDecodeError:

            raise ValueError(
                "Task Splitter returned invalid JSON."
            )

    def validate(self, data):

        return TaskSplitterResponse(**data)


# ===========================================================
# LangGraph Node
# ===========================================================

def task_splitter_node(state):

    print("\n========== Task Splitter ==========\n")

    state["current_agent"] = "Task Splitter"

    if "execution_trace" not in state:
        state["execution_trace"] = []

    state["execution_trace"].append("Task Splitter")

    try:

        goal = state["goal"]

        llm = state["llm"]

        splitter = TaskSplitter(llm)

        system_prompt, user_prompt = splitter.build_prompt(goal)

        response = splitter.call_llm(
            system_prompt,
            user_prompt,
        )

        parsed = splitter.parse_response(response)

        validated = splitter.validate(parsed)

        state["tasks"] = validated.tasks

        state["status"] = "Task Splitter Completed"

        print("Task Splitter Completed Successfully")

    except Exception as e:

        state["status"] = "Task Splitter Failed"

        state["error"] = str(e)

        print(e)

    return state


# ===========================================================
# Local Testing
# ===========================================================

if __name__ == "__main__":

    class DummyLLM:

        def generate(
            self,
            system_prompt,
            user_prompt,
            temperature,
        ):

            return """
            {
                "success": true,
                "parallel": true,
                "tasks": [
                    {
                        "task_id":"1",
                        "title":"Research AI",
                        "agent":"Researcher",
                        "dependencies":[],
                        "status":"pending"
                    }
                ]
            }
            """

    state = {
        "goal": "Research AI",
        "llm": DummyLLM(),
        "execution_trace": [],
        "current_agent": "",
        "tasks": [],
        "status": "",
        "error": ""
    }

    result = task_splitter_node(state)

    print(result)