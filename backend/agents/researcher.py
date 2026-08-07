import json

from graph.state import WorkflowState


class Researcher:
    """
    Research Agent
    """

    def __init__(self, llm_provider):
        self.llm = llm_provider

    def build_prompt(self, task):

        system_prompt = """
You are a Research Agent.

Your job is to research the assigned task.

Return only JSON.

{
    "summary":"",
    "key_points":[],
    "references":[]
}
"""

        user_prompt = f"""
Research the following task.

Task ID:
{task["task_id"]}

Task:
{task["title"]}
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
            return {
                "summary": response,
                "key_points": [],
                "references": []
            }


# ==========================================================
# Research Agent 1
# ==========================================================

def researcher_node_1(state):

    print("\n========== Research Agent 1 ==========\n")

    state["current_agent"] = "ResearchAgent1"
    state["execution_trace"].append("ResearchAgent1")

    try:

        task = state["tasks"][0]

        llm = state["llm"]

        researcher = Researcher(llm)

        system_prompt, user_prompt = researcher.build_prompt(task)

        response = researcher.call_llm(
            system_prompt,
            user_prompt
        )

        result = researcher.parse_response(response)

        state["research_agent_1"] = {
            "task_id": task["task_id"],
            "title": task["title"],
            "result": result
        }

    except Exception as e:

        state["error"] = str(e)

        state["research_agent_1"] = {}

    return state


# ==========================================================
# Research Agent 2
# ==========================================================

def researcher_node_2(state):

    print("\n========== Research Agent 2 ==========\n")

    state["current_agent"] = "ResearchAgent2"
    state["execution_trace"].append("ResearchAgent2")

    try:

        if len(state["tasks"]) > 1:

            task = state["tasks"][1]

            llm = state["llm"]

            researcher = Researcher(llm)

            system_prompt, user_prompt = researcher.build_prompt(task)

            response = researcher.call_llm(
                system_prompt,
                user_prompt
            )

            result = researcher.parse_response(response)

            state["research_agent_2"] = {
                "task_id": task["task_id"],
                "title": task["title"],
                "result": result
            }

        else:

            state["research_agent_2"] = {}

        state["research_results"] = [
            state["research_agent_1"],
            state["research_agent_2"],
        ]

    except Exception as e:

        state["error"] = str(e)

    return state