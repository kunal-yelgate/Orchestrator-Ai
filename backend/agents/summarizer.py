import json

from graph.state import WorkflowState


class Summarizer:
    """
    Summarizer Agent
    """

    def __init__(self, llm_provider):
        self.llm = llm_provider

    def build_prompt(self, research_results, failed_tasks=None):

        system_prompt = """
You are the Summarizer Agent.

Combine multiple research outputs into one final report.

Some research tasks may be missing because that research agent failed --
if so you will be told which tasks were skipped. Write the report using
only the research you were given; do not invent content for the missing
tasks, but you may briefly note in the summary that those areas were not
covered.

IMPORTANT RULES

1. Return ONLY valid JSON.
2. Do NOT use markdown.
3. Do NOT wrap JSON inside ```json.
4. Do NOT explain anything.

Return EXACTLY:

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

        failed_block = ""

        if failed_tasks:

            failed_titles = ", ".join(
                task.get("title") or task.get("task_id") or "unknown task"
                for task in failed_tasks
            )

            failed_block = f"""
The following research tasks failed and are NOT included above:
{failed_titles}
"""

        user_prompt = f"""
Combine the following research into one final report.

{content}
{failed_block}
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
            temperature=0.2,
        )

    def parse_response(self, response):

        if not response:
            raise ValueError("Summarizer returned an empty response.")

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

                    "title": "Summary",

                    "summary": cleaned,

                    "key_points": [],

                    "conclusion": ""

                }


# ==========================================================
# LangGraph Node
# ==========================================================

def summarizer_node(state: WorkflowState):

    print("\n========== Summarizer ==========\n")

    state["current_agent"] = "Summarizer"

    state.setdefault("execution_trace", [])
    state["execution_trace"].append("Summarizer")

    if state.get("error"):
        return state

    try:

        research_results = state.get("research_results", [])

        if not research_results:
            raise Exception("No research results available.")

        failed_tasks = state.get("research_failures", [])

        summarizer = Summarizer(state["llm"])

        system_prompt, user_prompt = summarizer.build_prompt(
            research_results,
            failed_tasks,
        )

        response = summarizer.call_llm(
            system_prompt,
            user_prompt,
        )

        print("\n========== RAW SUMMARIZER OUTPUT ==========\n")
        print(response)

        summary = summarizer.parse_response(response)

        print("\n========== PARSED SUMMARY ==========\n")
        print(summary)

        # Surface partial-failure info on the summary itself so it's
        # visible in the final output / API response without the client
        # needing to separately inspect state["research_failures"].
        summary["partial_failure"] = bool(failed_tasks)
        summary["failed_tasks"] = failed_tasks

        state["summary"] = summary

        state["status"] = "Summarizer Completed"

        print("\nSummarizer Finished Successfully\n")

    except Exception as e:

        state["status"] = "failed"

        state["error"] = str(e)

        print("\nSummarizer Error:\n")
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

    print(result["summary"])