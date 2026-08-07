import asyncio
import time

from graph.state import WorkflowState
from agents.researcher import research_node


class ExecutionEngine:
    """
    Executes research tasks in parallel.
    """

    def __init__(self):
        self.max_parallel_agents = 10
        self.timeout = 120

    async def execute_task(
        self,
        state: WorkflowState,
        task,
    ):

        runtime_state = {
            **state,
            "current_task": task,
        }

        try:

            result = await asyncio.wait_for(

                asyncio.to_thread(
                    research_node,
                    runtime_state,
                ),

                timeout=self.timeout,

            )

            return result

        except asyncio.TimeoutError:

            print(f"❌ Task Timed Out : {task['title']}")

            return {

                "research_results": [],

                "execution_trace": [

                    f"Timeout : {task['title']}"

                ],

                "completed_nodes": []

            }

        except Exception as e:

            print(f"Research Error : {e}")

            return {

                "research_results": [],

                "execution_trace": [

                    f"Failed : {task['title']}"

                ],

                "completed_nodes": []

            }

    async def execute_parallel(
        self,
        state: WorkflowState,
    ):

        start_time = time.perf_counter()

        tasks = state.get(
            "tasks",
            [],
        )

        print("\n" + "=" * 70)
        print("🚀 EXECUTION ENGINE STARTED")
        print(f"Launching {len(tasks)} Parallel Research Agents")
        print("=" * 70)

        jobs = [

            self.execute_task(
                state,
                task,
            )

            for task in tasks

        ]

        results = await asyncio.gather(
            *jobs,
            return_exceptions=False,
        )

        research_results = []

        execution_trace = []

        completed_nodes = []

        for result in results:

            research_results.extend(
                result.get(
                    "research_results",
                    [],
                )
            )

            execution_trace.extend(
                result.get(
                    "execution_trace",
                    [],
                )
            )

            completed_nodes.extend(
                result.get(
                    "completed_nodes",
                    [],
                )
            )

        elapsed = round(
            time.perf_counter() - start_time,
            2,
        )

        print("=" * 70)
        print("✅ PARALLEL EXECUTION COMPLETED")
        print(f"Completed Tasks : {len(research_results)}")
        print(f"Execution Time  : {elapsed} sec")
        print("=" * 70)

        return {

            "research_results": research_results,

            "execution_trace": execution_trace,

            "completed_nodes": completed_nodes,

            "execution_time": elapsed,

            "status": "Research Completed",

        }


# ==========================================================
# LangGraph Node (Synchronous Wrapper)
# ==========================================================

def execution_node(state: WorkflowState):

    state["current_agent"] = "Executor"

    engine = ExecutionEngine()

    return asyncio.run(
        engine.execute_parallel(state)
    )