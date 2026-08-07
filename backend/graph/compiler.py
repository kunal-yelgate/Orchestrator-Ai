from typing import Dict, Any, List


class WorkflowCompiler:
    """
    Converts Planner output into executable runtime tasks.
    """

    def __init__(self, plan: Dict[str, Any]):

        self.plan = plan

    def compile(self) -> List[Dict[str, Any]]:

        runtime_tasks = []

        planner_tasks = self.plan.get(
            "tasks",
            [],
        )

        for index, task in enumerate(planner_tasks, start=1):

            runtime_tasks.append(

                {

                    "id": task["id"],

                    "title": task["title"],

                    "description": task["description"],

                    "specialization": task["specialization"],

                    "priority": task["priority"],

                    "status": "Pending",

                    "assigned_agent": f"ResearchAgent-{index}",

                    "result": None,

                }

            )

        return runtime_tasks