import json


class ResearchService:

    def __init__(self, llm):

        self.llm = llm

    def run(self, task):

        system_prompt = """
You are an expert Research Agent.

Return ONLY JSON.

{
    "summary":"",
    "key_points":[],
    "references":[]
}
"""

        user_prompt = f"""
Research this task.

Title:
{task['title']}

Description:
{task['description']}

Specialization:
{task['specialization']}
"""

        response = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )

        try:

            result = json.loads(response)

        except Exception:

            start = response.find("{")
            end = response.rfind("}")

            if start != -1 and end != -1:

                result = json.loads(
                    response[start:end+1]
                )

            else:

                result = {

                    "summary": response,

                    "key_points": [],

                    "references": []

                }

        return {

            "task_id": task["id"],

            "title": task["title"],

            "specialization": task["specialization"],

            "result": result

        }