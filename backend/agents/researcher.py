import json

from graph.state import WorkflowState
from utils.permission_manager import PermissionManager


class Researcher:
    """
    Generic Research Agent

    Executes exactly one research task.
    """

    def __init__(self, llm_provider):
        self.llm = llm_provider

    def build_prompt(self, task):
        system_prompt = """
You are an expert Research Agent.

Research ONLY the assigned task.

Return ONLY valid JSON.

{
    "summary": "",
    "key_points": [],
    "references": []
}
"""

        user_prompt = f"""
Research the following task.

Task ID:
{task["id"]}

Title:
{task["title"]}

Description:
{task["description"]}

Specialization:
{task["specialization"]}

Priority:
{task["priority"]}
"""

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
        try:
            return json.loads(response)

        except json.JSONDecodeError:
            try:
                start = response.find("{")
                end = response.rfind("}")

                if start == -1 or end == -1:
                    raise ValueError("No JSON object found.")

                return json.loads(response[start : end + 1])

            except (json.JSONDecodeError, ValueError):
                return {
                    "summary": response,
                    "key_points": [],
                    "references": [],
                }


# ==========================================================
# LangGraph Research Node
# ==========================================================

def research_node(state: WorkflowState):
    task = state["current_task"]

    print("\n" + "=" * 60)
    print("🔍 Research Agent Started")
    print(f"Task : {task['title']}")
    print("=" * 60)

    state.setdefault("active_nodes", [])
    state.setdefault("completed_nodes", [])
    state.setdefault("execution_trace", [])
    state.setdefault("failed_nodes", [])

    state["active_nodes"].append(task["title"])

    PermissionManager.require_tool(
        "Researcher",
        "llm",
    )

    PermissionManager.require_network(
        "Researcher",
    )

    try:
        researcher = Researcher(state["llm"])

        system_prompt, user_prompt = researcher.build_prompt(task)

        llm_response = researcher.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        content = (
            llm_response.get("content", "")
            if isinstance(llm_response, dict)
            else llm_response
        )

        result = researcher.parse_response(content)

        usage = (
            llm_response.get("usage", {})
            if isinstance(llm_response, dict)
            else {}
        )

        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        if task["title"] in state["active_nodes"]:
            state["active_nodes"].remove(task["title"])

        state["completed_nodes"].append(task["title"])

        print(f"✅ Completed : {task['title']}")
        print("=" * 60)

        return {
            "research_results": [
                {
                    "task_id": task["id"],
                    "title": task["title"],
                    "specialization": task["specialization"],
                    "result": result,
                }
            ],
            "execution_trace": [
                f"Research : {task['title']}"
            ],
            "completed_nodes": [
                task["title"]
            ],
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }

    except Exception as error:
        if task["title"] in state["active_nodes"]:
            state["active_nodes"].remove(task["title"])

        state["failed_nodes"].append(task["title"])

        print(f"❌ Research failed for {task['title']}: {error}")

        return {
            "research_results": [],
            "execution_trace": [
                f"Research Failed : {task['title']}"
            ],
            "failed_nodes": [
                task["title"]
            ],
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
