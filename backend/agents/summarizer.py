import json

from graph.state import WorkflowState


class Summarizer:
    """
    Summarizer Agent
    """

    def __init__(self, llm_provider):
        self.llm = llm_provider

    def build_prompt(self, research_results):

        system_prompt = """
You are the Summarizer Agent.

Combine multiple research outputs into one final report.

Return ONLY JSON.

{
    "title":"",
    "summary":"",
    "key_points":[],
    "conclusion":""
}
"""

        content = ""

        for item in research_results:

            title = item.get("title", "")

            result = item.get("result", {})

            summary = result.get("summary", "")

            content += f"\nTask: {title}\n"
            content += f"Research:\n{summary}\n"

        user_prompt = f"""
Combine the following research into one final report.

{content}
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
                "title": "Summary",
                "summary": response,
                "key_points": [],
                "conclusion": ""
            }


# ===========================================================
# LangGraph Node
# ===========================================================

def summarizer_node(state: WorkflowState):

    print("\n========== Summarizer ==========\n")

    state["current_agent"] = "Summarizer"

    state["execution_trace"].append("Summarizer")

    try:

        research_results = state.get("research_results", [])

        if not research_results:

            raise Exception("No research results available.")

        llm = state["llm"]

        summarizer = Summarizer(llm)

        system_prompt, user_prompt = summarizer.build_prompt(
            research_results
        )

        response = summarizer.call_llm(
            system_prompt,
            user_prompt,
        )

        summary = summarizer.parse_response(response)

        state["summary"] = summary

        state["status"] = "Summarizer Completed"

        print("Summarizer Finished Successfully")

    except Exception as e:

        state["status"] = "Summarizer Failed"

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
                "title":"Artificial Intelligence",
                "summary":"AI is transforming multiple industries.",
                "key_points":[
                    "Healthcare",
                    "Finance",
                    "Education"
                ],
                "conclusion":"AI will continue to evolve."
            }
            """

    state = {

        "llm": DummyLLM(),

        "research_results": [

            {
                "title": "History",

                "result": {
                    "summary": "History of AI"
                }

            },

            {
                "title": "Applications",

                "result": {
                    "summary": "Applications of AI"
                }

            }

        ],

        "execution_trace": [],

        "current_agent": "",

        "summary": {},

        "status": "",

        "error": ""
    }

    result = summarizer_node(state)

    print(result)