import json

from graph.state import WorkflowState


class Researcher:
    """
    Generic Research Agent

    Executes exactly one research task.
    """

    def __init__(self, llm_provider):
        self.llm = llm_provider

    def build_prompt(self, task):

        system_prompt = """
You are an expert Research Agent.

Research ONLY the assigned task.

Return ONLY valid JSON.

{
    "summary":"",
    "key_points":[],
    "references":[]
}
"""

        user_prompt = f"""
Research the following task.

Task ID:
{task["id"]}

Title:
{task["title"]}

Description:
{task["description"]}

Specialization:
{task["specialization"]}

Priority:
{task["priority"]}
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

                    "summary": response,

                    "key_points": [],

                    "references": []

                }
    # ==========================================================
# LangGraph Research Node
# ==========================================================

def research_node(state: WorkflowState):

    task = state["current_task"]

    print("\n" + "=" * 60)
    print(f"🔍 Research Agent Started")
    print(f"Task : {task['title']}")
    print("=" * 60)

    # ----------------------------------------------
    # Runtime Tracking
    # ----------------------------------------------

    state.setdefault("active_nodes", [])
    state.setdefault("completed_nodes", [])
    state.setdefault("execution_trace", [])

    state["active_nodes"].append(task["title"])

    researcher = Researcher(
        state["llm"]
    )

    system_prompt, user_prompt = researcher.build_prompt(
        task
    )

    response = researcher.call_llm(
        system_prompt,
        user_prompt,
    )

    result = researcher.parse_response(
        response
    )

    state["completed_nodes"].append(
        task["title"]
    )

    print(f"✅ Completed : {task['title']}")

    print("=" * 60)

    return {

        "research_results": [

            {

                "task_id": task["id"],

                "title": task["title"],

                "specialization": task["specialization"],

                "result": result,

            }

        ],

<<<<<<< HEAD
        "execution_trace": [
=======
# ==========================================================
# Partial Failure Recovery helpers
#
# A research agent failing on its OWN task must never stop the rest of
# the workflow: other research agents still run, and the Summarizer
# still runs on whichever agents succeeded. Each research node therefore
# catches its own errors locally (never sets the workflow-halting
# state["error"]) and records what happened on state["research_failures"]
# instead. Only if EVERY research agent fails does downstream work stop
# -- and that happens naturally in summarizer_node, since it has nothing
# left to summarize.
# ==========================================================

def _record_research_failure(state, agent_name, task, error):

    state.setdefault("research_failures", [])

    state["research_failures"].append({
        "agent": agent_name,
        "task_id": task.get("task_id") if task else None,
        "title": task.get("title") if task else None,
        "error": str(error),
    })

    state["partial_failure"] = True

    print(f"\n{agent_name} failed on its task (continuing workflow): {error}\n")


# ==========================================================
# Research Agent 1
# ==========================================================
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0

            f"Research : {task['title']}"

        ],

        "completed_nodes": [

<<<<<<< HEAD
            task["title"]

        ]

    }
=======
    tasks = state.get("tasks", [])

    if len(tasks) == 0:

        state["research_agent_1"] = {}

        return state

    task = tasks[0]

    try:

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

            "result": result,

            "status": "success",

        }

    except Exception as e:

        # Local failure only -- does NOT set state["error"], so
        # ResearchAgent2, the Summarizer, and the Verifier still run.
        state["research_agent_1"] = {

            "task_id": task.get("task_id"),

            "title": task.get("title"),

            "error": str(e),

            "status": "failed",

        }

        _record_research_failure(state, "ResearchAgent1", task, e)

    return state


# ==========================================================
# Research Agent 2
# ==========================================================

def researcher_node_2(state: WorkflowState):

    print("\n========== Research Agent 2 ==========\n")

    state["current_agent"] = "ResearchAgent2"
    state["execution_trace"].append("ResearchAgent2")

    tasks = state.get("tasks", [])

    if len(tasks) >= 2:

        task = tasks[1]

        try:

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

                "result": result,

                "status": "success",

            }

        except Exception as e:

            # Local failure only -- ResearchAgent1's result (if it
            # succeeded) is still usable, so we don't halt the workflow.
            state["research_agent_2"] = {

                "task_id": task.get("task_id"),

                "title": task.get("title"),

                "error": str(e),

                "status": "failed",

            }

            _record_research_failure(state, "ResearchAgent2", task, e)

    else:

        state["research_agent_2"] = {}

    # ======================================================
    # Collect results from whichever research agents actually
    # succeeded. This is what makes Partial Failure Recovery work:
    # the Summarizer below only ever sees successful entries, and
    # simply has less to work with when some agents failed.
    # ======================================================

    state["research_results"] = [
        agent_result
        for agent_result in (
            state.get("research_agent_1"),
            state.get("research_agent_2"),
        )
        if agent_result and agent_result.get("status") == "success"
    ]

    if state["research_results"]:

        state["status"] = (
            "Research Completed"
            if not state.get("partial_failure")
            else "Research Partially Completed"
        )

        print(
            "Research Completed Successfully"
            if not state.get("partial_failure")
            else "Research Completed With Partial Failures"
        )

    else:

        # Every research agent failed -- nothing for the Summarizer to
        # work with. This IS a fatal error, unlike a single agent failing.
        state["status"] = "failed"

        state["error"] = "All research agents failed."

    return state
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
