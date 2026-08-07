import json

from graph.state import WorkflowState

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
        system_prompt,
        user_prompt,
    ):

        return self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )

    def parse_response(self, response):

        if not response:
            raise ValueError("Task Splitter returned an empty response.")

        try:
            return json.loads(response)

        except json.JSONDecodeError:

            cleaned = response.strip()

            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]

            if cleaned.startswith("```"):
                cleaned = cleaned[3:]

            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

            try:
                return json.loads(cleaned)

            except Exception:

                start = cleaned.find("{")
                end = cleaned.rfind("}")

                if start == -1 or end == -1:
                    raise ValueError(
                        f"Task Splitter returned invalid JSON:\n\n{response}"
                    )

                return json.loads(
                    cleaned[start:end + 1]
                )

    def validate(self, data):

        return TaskSplitterResponse(**data)


# ==========================================================
# LangGraph Node
# ==========================================================

def task_splitter_node(state: WorkflowState):

    print("\n========== Task Splitter ==========\n")

    state["current_agent"] = "TaskSplitter"

    state.setdefault("execution_trace", [])
    state["execution_trace"].append("TaskSplitter")

    if state.get("error"):
        return state

    try:

        goal = state["goal"]

        splitter = TaskSplitter(state["llm"])

        system_prompt, user_prompt = splitter.build_prompt(goal)

        response = splitter.call_llm(
            system_prompt,
            user_prompt,
        )

        print("\n========== RAW TASK SPLITTER OUTPUT ==========\n")
        print(response)

        parsed = splitter.parse_response(response)

        print("\n========== PARSED JSON ==========\n")
        print(parsed)

        # ====================================================
        # Normalize Groq Output
        # ====================================================

        if "workflow" in parsed:

            workflow = parsed["workflow"]

            normalized_tasks = []

            for task in workflow.get("tasks", []):

                normalized_tasks.append({

                    "task_id": str(task.get("task_id")),

                    "title": task.get(
                        "task_name",
                        task.get("title", "")
                    ),

                    "agent": "Researcher",

                    "dependencies": [],

                    "status": "pending"

                })

            parsed = {

                "success": True,

                "parallel": True,

                "tasks": normalized_tasks

            }

            print("\n========== NORMALIZED JSON ==========\n")
            print(parsed)

        validated = splitter.validate(parsed)

        state["tasks"] = [
            task.model_dump()
            for task in validated.tasks
        ]

        state["status"] = "Task Splitter Completed"

        print("\nTask Splitter Completed Successfully\n")

    except Exception as e:

        state["status"] = "failed"

        state["tasks"] = []

        state["error"] = str(e)

        print("\nTask Splitter Error:\n")
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
    "success": true,
    "parallel": true,
    "tasks": [
        {
            "task_id":"1",
            "title":"Research Artificial Intelligence",
            "agent":"Researcher",
            "dependencies":[],
            "status":"pending"
        },
        {
            "task_id":"2",
            "title":"Applications of Artificial Intelligence",
            "agent":"Researcher",
            "dependencies":[],
            "status":"pending"
        }
    ]
}
"""

    state = {

        "goal": "Research Artificial Intelligence",

        "llm": DummyLLM(),

        "tasks": [],

        "execution_trace": [],

        "current_agent": "",

        "status": "",

        "error": ""
    }

    result = task_splitter_node(state)

    print("\n========== TASKS ==========\n")

    print(json.dumps(result["tasks"], indent=4))