import json

from graph.state import WorkflowState


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
    "summary":"",
    "key_points":[],
    "references":[]
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

        except Exception:

            try:

                start = response.find("{")
                end = response.rfind("}")

                return json.loads(
                    response[start:end + 1]
                )

            except Exception:

                return {

                    "summary": response,

                    "key_points": [],

                    "references": []

                }
    # ==========================================================
# LangGraph Research Node
# ==========================================================

def research_node(state: WorkflowState):

    task = state["current_task"]

    print("\n" + "=" * 60)
    print(f"🔍 Research Agent Started")
    print(f"Task : {task['title']}")
    print("=" * 60)

    # ----------------------------------------------
    # Runtime Tracking
    # ----------------------------------------------

    state.setdefault("active_nodes", [])
    state.setdefault("completed_nodes", [])
    state.setdefault("execution_trace", [])

    state["active_nodes"].append(task["title"])

    researcher = Researcher(
        state["llm"]
    )

    system_prompt, user_prompt = researcher.build_prompt(
        task
    )

    response = researcher.call_llm(
        system_prompt,
        user_prompt,
    )

    result = researcher.parse_response(
        response
    )

    state["completed_nodes"].append(
        task["title"]
    )

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

        ]

    }