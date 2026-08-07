import json

from graph.state import WorkflowState


class Verifier:
    """
    Verifier Agent
    """

    def __init__(self, llm_provider):
        self.llm = llm_provider

    def build_prompt(self, summary):

        system_prompt = """
You are the Verifier Agent.

Your job is to verify the quality of the generated summary.

Return ONLY JSON.

{
    "verified": true,
    "confidence": 0.95,
    "issues": [],
    "feedback": ""
}
"""

        user_prompt = f"""
Verify the following summary.

{summary}
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
            temperature=0.1,
        )

    def parse_response(self, response):

        try:
            return json.loads(response)

        except Exception:

            return {
                "verified": False,
                "confidence": 0.0,
                "issues": [
                    "Verifier returned invalid JSON."
                ],
                "feedback": response
            }


# ===========================================================
# LangGraph Node
# ===========================================================

def verifier_node(state: WorkflowState):

    print("\n========== Verifier ==========\n")

    state["current_agent"] = "Verifier"

    state["execution_trace"].append("Verifier")

    try:

        summary = state.get("summary", {})

        if not summary:

            raise Exception("Summary not found.")

        llm = state["llm"]

        verifier = Verifier(llm)

        system_prompt, user_prompt = verifier.build_prompt(
            summary
        )

        response = verifier.call_llm(
            system_prompt,
            user_prompt,
        )

        verification = verifier.parse_response(response)

        state["verification"] = verification

        state["final_output"] = {
            "workflow_id": state["workflow_id"],
            "goal": state["goal"],
            "summary": summary,
            "verification": verification
        }

        if verification["verified"]:

            state["status"] = "Completed"

        else:

            state["status"] = "Verification Failed"

        print("Verifier Finished Successfully")

    except Exception as e:

        state["status"] = "Verifier Failed"

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
                "verified": true,
                "confidence": 0.98,
                "issues": [],
                "feedback": "Summary is complete and accurate."
            }
            """

    state = {

        "workflow_id": "WF-001",

        "goal": "Research Artificial Intelligence",

        "summary": {
            "title": "Artificial Intelligence",
            "summary": "AI is transforming industries.",
            "key_points": [
                "Healthcare",
                "Finance"
            ],
            "conclusion": "AI has a promising future."
        },

        "llm": DummyLLM(),

        "execution_trace": [],

        "current_agent": "",

        "verification": {},

        "final_output": {},

        "status": "",

        "error": ""
    }

    result = verifier_node(state)

    print(result)