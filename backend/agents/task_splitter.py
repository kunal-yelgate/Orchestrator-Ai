from graph.state import WorkflowState
from graph.compiler import WorkflowCompiler


# ==========================================================
# LangGraph Node
# ==========================================================

def task_splitter_node(state: WorkflowState):

    print("\n========== Task Splitter ==========\n")

    state["current_agent"] = "Task Splitter"

    if "execution_trace" not in state:
        state["execution_trace"] = []

    state["execution_trace"].append("Task Splitter")

    try:

        # ============================================
        # Read Planner Output
        # ============================================

        plan = state.get("plan", {})

        if not plan:
            raise ValueError(
                "Planner did not generate a workflow plan."
            )

        # ============================================
        # Compile Workflow into Executable Tasks
        # ============================================

        compiler = WorkflowCompiler(plan)

        compiled_tasks = compiler.compile()

        if not compiled_tasks:
            raise ValueError(
                "Workflow Compiler generated zero tasks."
            )

        # ============================================
        # Store Runtime Tasks
        # ============================================

        state["tasks"] = compiled_tasks

        state["status"] = "Task Splitter Completed"

        print(f"\nGenerated {len(compiled_tasks)} Executable Tasks\n")

        for index, task in enumerate(compiled_tasks, start=1):

            print(
                f"{index}. "
                f"{task['title']} "
                f"({task['specialization']}) "
                f"[{task['priority'].upper()}]"
            )

    except Exception as e:

        state["status"] = "Task Splitter Failed"

        state["error"] = str(e)

        print(f"Task Splitter Error : {e}")

    return state