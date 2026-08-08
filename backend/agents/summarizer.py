import json

from graph.state import WorkflowState


class Summarizer:
    """
    Summarizer Agent

    Combines all research outputs into one final report.
    """

    def __init__(self, llm_provider):
        self.llm = llm_provider

    def build_prompt(self, research_results, failed_tasks=None):

        system_prompt = """
You are the Summarizer Agent.

Your job is to combine multiple research reports into one final report.

<<<<<<< HEAD
Return ONLY valid JSON.
=======
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
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0

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
Combine all research reports into ONE comprehensive report.

{content}
<<<<<<< HEAD

Return ONLY JSON.
=======
{failed_block}
Return ONLY valid JSON.
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
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

<<<<<<< HEAD
        raise Exception(
            "No research results available."
=======
    try:

        research_results = state.get("research_results", [])

        if not research_results:
            raise Exception("No research results available.")

        failed_tasks = state.get("research_failures", [])

        summarizer = Summarizer(state["llm"])

        system_prompt, user_prompt = summarizer.build_prompt(
            research_results,
            failed_tasks,
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
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

<<<<<<< HEAD
    state["summary"] = summary
=======
        # Surface partial-failure info on the summary itself so it's
        # visible in the final output / API response without the client
        # needing to separately inspect state["research_failures"].
        summary["partial_failure"] = bool(failed_tasks)
        summary["failed_tasks"] = failed_tasks

        state["summary"] = summary
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0

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