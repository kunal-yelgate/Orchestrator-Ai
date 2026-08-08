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
    "title": "",
    "summary": "",
    "key_points": [],
    "conclusion": ""
}
"""

        content = ""

        for item in research_results:
            result = item.get("result", {})

            content += f"""
Task:
{item.get("title", "Untitled Task")}

Specialization:
{item.get("specialization", "General")}

Research:
{result.get("summary", "No summary available.")}

-----------------------
"""

        user_prompt = f"""
Combine all research reports into ONE comprehensive report.

{content}

Return ONLY JSON.
"""

        return system_prompt, user_prompt

    def call_llm(self, system_prompt, user_prompt):
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
                    "title": "Summary",
                    "summary": response,
                    "key_points": [],
                    "conclusion": "",
                }


# ==========================================================
# LangGraph Node
# ==========================================================

def summarizer_node(state: WorkflowState):
    print("\n========== Summarizer ==========\n")

    state["current_agent"] = "Summarizer"

    research_results = state.get("research_results", [])

    if not research_results:
        state["summary"] = {
            "title": "No Results",
            "summary": "All research agents failed to produce results.",
            "key_points": [],
            "conclusion": "",
        }

        state["status"] = "Summarizer Skipped"
        state.setdefault("execution_trace", []).append("Summarizer")

        return state

    summarizer = Summarizer(state["llm"])

    system_prompt, user_prompt = summarizer.build_prompt(research_results)

    llm_response = summarizer.call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    content = (
        llm_response.get("content", "")
        if isinstance(llm_response, dict)
        else llm_response
    )

    summary = summarizer.parse_response(content)

    usage = (
        llm_response.get("usage", {})
        if isinstance(llm_response, dict)
        else {}
    )

    state["prompt_tokens"] = state.get("prompt_tokens", 0) + usage.get(
        "prompt_tokens",
        0,
    )

    state["completion_tokens"] = state.get(
        "completion_tokens",
        0,
    ) + usage.get(
        "completion_tokens",
        0,
    )

    state["total_tokens"] = state.get("total_tokens", 0) + usage.get(
        "total_tokens",
        0,
    )

    state["summary"] = summary
    state["status"] = "Summarizer Completed"
    state.setdefault("execution_trace", []).append("Summarizer")

    print("Summary Generated Successfully")

    return state
