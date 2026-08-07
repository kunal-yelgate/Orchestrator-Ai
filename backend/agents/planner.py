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

        state["plan"] = workflow

        state["status"] = "Planner Completed"

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
                "workflow_name":"Research Workflow",
                "execution":"parallel",
                "agents":[
                    {
                        "id":"planner",
                        "role":"Planner",
                        "description":"Create workflow",
                        "input":"User Goal",
                        "output":"Workflow Plan",
                        "depends_on":[],
                        "next":["task_splitter"],
                        "parallel":false
                    },
                    {
                        "id":"task_splitter",
                        "role":"Task Splitter",
                        "description":"Split work",
                        "input":"Workflow",
                        "output":"Tasks",
                        "depends_on":["planner"],
                        "next":["researcher_1","researcher_2"],
                        "parallel":false
                    },
                    {
                        "id":"researcher_1",
                        "role":"Researcher",
                        "description":"Research Topic 1",
                        "input":"Task",
                        "output":"Research",
                        "depends_on":["task_splitter"],
                        "next":["summarizer"],
                        "parallel":true
                    },
                    {
                        "id":"researcher_2",
                        "role":"Researcher",
                        "description":"Research Topic 2",
                        "input":"Task",
                        "output":"Research",
                        "depends_on":["task_splitter"],
                        "next":["summarizer"],
                        "parallel":true
                    },
                    {
                        "id":"summarizer",
                        "role":"Summarizer",
                        "description":"Combine Results",
                        "input":"Research",
                        "output":"Summary",
                        "depends_on":["researcher_1","researcher_2"],
                        "next":["verifier"],
                        "parallel":false
                    },
                    {
                        "id":"verifier",
                        "role":"Verifier",
                        "description":"Validate Output",
                        "input":"Summary",
                        "output":"Verified Report",
                        "depends_on":["summarizer"],
                        "next":[],
                        "parallel":false
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

        "error": ""
    }

    result = planner_node(state)

    print("\n========== Planner Output ==========\n")

    print(json.dumps(result["plan"], indent=4))