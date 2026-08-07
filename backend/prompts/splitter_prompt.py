TASK_SPLITTER_SYSTEM_PROMPT = """
You are the Task Splitter Agent of an Agentic AI Orchestrator.

ROLE
Your responsibility is to convert a user's high-level goal into a structured, executable workflow.

...
"""
def build_task_splitter_prompt(goal: str) -> str:
    return f"""
User Goal:

{goal}

Generate an executable workflow.

Return JSON only.
"""


