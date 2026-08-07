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

IMPORTANT RULES

1. Return ONLY valid JSON.
2. Do NOT use markdown.
3. Do NOT wrap JSON inside ```json.
4. Do NOT explain anything.

Return EXACTLY:

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

Return ONLY valid JSON.
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

        if not response:
            raise ValueError("Verifier returned an empty response.")

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

                if start != -1 and end != -1:

                    return json.loads(
                        cleaned[start:end + 1]
                    )

                return {
                    "verified": False,
                    "confidence": 0.0,
                    "issues": [
                        "Verifier returned invalid JSON."
                    ],
                    "feedback": cleaned
                }


# ==========================================================
# LangGraph Node
# ==========================================================

def verifier_node(state: WorkflowState):

    print("\n========== Verifier ==========\n")

    state["current_agent"] = "Verifier"

    state.setdefault("execution_trace", [])
    state["execution_trace"].append("Verifier")

    if state.get("error"):
        return state

    try:

        summary = state.get("summary", {})

        if not summary:
            raise Exception("Summary not found.")

        verifier = Verifier(state["llm"])

        system_prompt, user_prompt = verifier.build_prompt(
            summary
        )

        response = verifier.call_llm(
            system_prompt,
            user_prompt,
        )

        print("\n========== RAW VERIFIER OUTPUT ==========\n")
        print(response)

        verification = verifier.parse_response(response)

        print("\n========== PARSED VERIFIER ==========\n")
        print(verification)

        state["verification"] = verification

        state["final_output"] = {

            "workflow_id": state["workflow_id"],

            "goal": state["goal"],

            "summary": summary,

            "verification": verification

        }

        state["status"] = (
            "Completed"
            if verification.get("verified")
            else "Verification Failed"
        )

        print("\nVerifier Finished Successfully\n")

    except Exception as e:

        state["status"] = "Verifier Failed"

        state["error"] = str(e)

        print("\nVerifier Error:\n")
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
            temperature=0.1,
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

    print(result["final_output"])