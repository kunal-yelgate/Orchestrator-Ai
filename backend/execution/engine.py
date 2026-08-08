import asyncio
import time

from agents.researcher import research_node
from config.agent_config import AGENT_CONFIGS
from graph.state import WorkflowState


class ExecutionEngine:
    """
    Executes research tasks in parallel.
    """

    def __init__(self):
        self.max_parallel_agents = 10

    async def execute_task(
        self,
        state: WorkflowState,
        task,
        semaphore: asyncio.Semaphore,
    ):
        runtime_state = {
            **state,
            "current_task": task,
        }

        agent_config = AGENT_CONFIGS["Researcher"]
        retry_limit = agent_config.retry_limit

        for attempt in range(retry_limit + 1):
            try:
                async with semaphore:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(
                            research_node,
                            runtime_state,
                        ),
                        timeout=agent_config.timeout,
                    )

                    result["retry_count"] = attempt
                    return result

            except asyncio.TimeoutError:
                print(
                    f"Retry {attempt + 1}/{retry_limit + 1} : {task['title']}"
                )

            except Exception as error:
                print(
                    f"Retry {attempt + 1}/{retry_limit + 1} : {task['title']}"
                )
                print(error)

        print(f"Research Failed : {task['title']}")

        return {
            "research_results": [],
            "execution_trace": [f"Failed : {task['title']}"],
            "completed_nodes": [],
            "failed_nodes": [task["title"]],
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "retry_count": retry_limit,
        }

    async def execute_parallel(
        self,
        state: WorkflowState,
    ):
        start_time = time.perf_counter()

        tasks = state.get("tasks", [])
        agent_config = AGENT_CONFIGS["Researcher"]

        if state.get("total_tokens", 0) >= agent_config.max_tokens:
            print(f"Token budget exceeded for {agent_config.name}")

            return {
                "research_results": [],
                "execution_trace": ["Budget Exceeded : Researcher"],
                "completed_nodes": [],
                "failed_nodes": [],
                "execution_time": 0.0,
                "status": "Research Budget Exceeded",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "retry_count": 0,
            }

        semaphore = asyncio.Semaphore(self.max_parallel_agents)

        print("\n" + "=" * 70)
        print("EXECUTION ENGINE STARTED")
        print(f"Launching {len(tasks)} Parallel Research Agents")
        print("=" * 70)

        jobs = [
            self.execute_task(
                state,
                task,
                semaphore,
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
        failed_nodes = []
        retry_count = 0
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        for result in results:
            research_results.extend(
                result.get("research_results", [])
            )

            execution_trace.extend(
                result.get("execution_trace", [])
            )

            completed_nodes.extend(
                result.get("completed_nodes", [])
            )

            failed_nodes.extend(
                result.get("failed_nodes", [])
            )

            retry_count += result.get(
                "retry_count",
                0,
            )

            prompt_tokens += result.get(
                "prompt_tokens",
                0,
            )

            completion_tokens += result.get(
                "completion_tokens",
                0,
            )

            total_tokens += result.get(
                "total_tokens",
                0,
            )

        elapsed = round(
            time.perf_counter() - start_time,
            2,
        )

        print("=" * 70)
        print("PARALLEL EXECUTION COMPLETED")
        print(f"Completed Tasks : {len(research_results)}")
        print(f"Execution Time  : {elapsed} sec")
        print(f"Total Tokens    : {total_tokens}")
        print(f"Total Retries   : {retry_count}")
        print("=" * 70)

        return {
            "research_results": research_results,
            "execution_trace": execution_trace,
            "completed_nodes": completed_nodes,
            "failed_nodes": failed_nodes,
            "execution_time": elapsed,
            "status": "Research Completed",
            "retry_count": retry_count,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
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