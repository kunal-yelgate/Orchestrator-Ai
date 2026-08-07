import json

from graph.state import WorkflowState


class Researcher:
    """
    Research Agent
    """

    def __init__(self, llm_provider):
        self.llm = llm_provider

    def build_prompt(self, task, retrieval=None):

        system_prompt = """
You are a Research Agent.

Your job is to research the assigned task.

You may be given context that was already retrieved from documents the
user uploaded. If that context answers (or partially answers) the task,
use and build on it. If it does not cover the task — or no document
context is provided at all — research the task yourself using your own
knowledge and reasoning instead of leaving it unanswered.

Return ONLY valid JSON.

{
    "summary":"",
    "key_points":[],
    "references":[]
}
"""

        retrieval = retrieval or {}

        document_context_block = ""

        if retrieval.get("ran") and retrieval.get("found"):

            document_context_block = f"""
Document Context (already retrieved from the user's uploaded documents):

{retrieval.get("answer", "")}

Use this as your primary source where relevant. Fill any gaps with your
own research.
"""

        elif retrieval.get("ran") and not retrieval.get("found"):

            document_context_block = """
The uploaded documents were checked but did not contain information
relevant to this task. Research this task yourself using your own
knowledge and reasoning.
"""

        user_prompt = f"""
Research the following task.

Task ID:
{task["task_id"]}

Task:
{task["title"]}
{document_context_block}
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

                if start != -1 and end != -1:
                    return json.loads(response[start:end + 1])

            except Exception:
                pass

            return {
                "summary": response,
                "key_points": [],
                "references": []
            }


# ==========================================================
# Research Agent 1
# ==========================================================

def researcher_node_1(state: WorkflowState):

    print("\n========== Research Agent 1 ==========\n")

    state["current_agent"] = "ResearchAgent1"
    state["execution_trace"].append("ResearchAgent1")

    if state.get("error"):
        return state

    tasks = state.get("tasks", [])

    if len(tasks) == 0:

        state["research_agent_1"] = {}

        return state

    try:

        task = tasks[0]

        researcher = Researcher(state["llm"])

        system_prompt, user_prompt = researcher.build_prompt(
            task,
            state.get("retrieval"),
        )

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

        state["status"] = "failed"

        state["research_agent_1"] = {}

    return state


# ==========================================================
# Research Agent 2
# ==========================================================

def researcher_node_2(state: WorkflowState):

    print("\n========== Research Agent 2 ==========\n")

    state["current_agent"] = "ResearchAgent2"
    state["execution_trace"].append("ResearchAgent2")

    if state.get("error"):
        return state

    tasks = state.get("tasks", [])

    if len(tasks) < 2:

        state["research_agent_2"] = {}

        state["research_results"] = []

        if state.get("research_agent_1"):
            state["research_results"].append(
                state["research_agent_1"]
            )

        return state

    try:

        task = tasks[1]

        researcher = Researcher(state["llm"])

        system_prompt, user_prompt = researcher.build_prompt(
            task,
            state.get("retrieval"),
        )

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

        state["research_results"] = []

        if state.get("research_agent_1"):
            state["research_results"].append(
                state["research_agent_1"]
            )

        if state.get("research_agent_2"):
            state["research_results"].append(
                state["research_agent_2"]
            )

        state["status"] = "Research Completed"

        print("Research Completed Successfully")

    except Exception as e:

        state["error"] = str(e)

        state["status"] = "failed"

    return state