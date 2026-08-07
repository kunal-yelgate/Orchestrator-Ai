import json

from graph.state import WorkflowState


class Summarizer:
    """
    Summarizer Agent

    Combines all research outputs into one final report.
    """

    def __init__(self, llm_provider):
        self.llm = llm_provider

    def build_prompt(self, research_results):

        system_prompt = """
You are the Summarizer Agent.

Your job is to combine multiple research reports into one final report.

Return ONLY valid JSON.

{
    "title":"",
    "summary":"",
    "key_points":[],
    "conclusion":""
}
"""

        content = ""

        for item in research_results:

            content += f"""
Task:
{item["title"]}

Specialization:
{item["specialization"]}

Research:
{item["result"]["summary"]}

-----------------------
"""

        user_prompt = f"""
Combine all research reports into ONE comprehensive report.

{content}

Return ONLY JSON.
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

                    "title": "Summary",

                    "summary": response,

                    "key_points": [],

                    "conclusion": ""

                }


# ==========================================================
# LangGraph Node
# ==========================================================

def summarizer_node(state: WorkflowState):

    print("\n========== Summarizer ==========\n")

    state["current_agent"] = "Summarizer"

    research_results = state.get(
        "research_results",
        [],
    )

    if not research_results:

        raise Exception(
            "No research results available."
        )

    summarizer = Summarizer(
        state["llm"]
    )

    system_prompt, user_prompt = summarizer.build_prompt(
        research_results
    )

    response = summarizer.call_llm(
        system_prompt,
        user_prompt,
    )

    summary = summarizer.parse_response(
        response
    )

    state["summary"] = summary

    state["status"] = "Summarizer Completed"

    state.setdefault(
        "execution_trace",
        []
    )

    state["execution_trace"].append(
        "Summarizer"
    )

    print("Summary Generated Successfully")

    return state