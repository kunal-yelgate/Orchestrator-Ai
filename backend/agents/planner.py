"""
planner.py

Planner Agent for Agentic AI Orchestrator.

Input:
    User goal

Output:
    Typed workflow graph JSON

Model:
    meta-llama/Llama-3.1-8B-Instruct

Provider:
    HuggingFace InferenceClient + Novita
"""


import os
import json
import re
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


# =======================================================
# Load Environment Variables
# =======================================================


env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(env_path)



# =======================================================
# Planner System Prompt
# =======================================================


PLANNER_SYSTEM_PROMPT = """

You are the Planner Agent of an Agentic AI Orchestrator.

Your responsibility is to convert a user goal into a
typed executable multi-agent workflow graph.


Return ONLY valid JSON.

Do not add markdown.
Do not add explanations.


==================================================
OUTPUT SCHEMA
==================================================


{
  "workflow_name": "",
  "execution": "sequential | parallel | hybrid",

  "agents": [

    {
      "id": "",
      "role": "",
      "description": "",

      "input": "",
      "output": "",

      "depends_on": [],

      "next": [],

      "parallel": false
    }

  ]
}



==================================================
AVAILABLE AGENT TYPES
==================================================


Only use these roles:


1. Planner

2. Task Splitter

3. Researcher

4. Summarizer

5. Verifier



==================================================
WORKFLOW DESIGN RULES
==================================================


1.
Planner must always be the first node.


2.
Planner creates a high-level execution strategy.


3.
Planner must connect to Task Splitter.


4.
Task Splitter decomposes the goal into smaller tasks.


5.
For research or analysis tasks:

Create multiple specialized Researcher agents.


Example:


researcher_1
- Research history


researcher_2
- Research technical details


researcher_3
- Research applications



6.
Researcher agents must execute in parallel.


7.
All Researcher outputs must go to Summarizer.


8.
Summarizer combines all outputs.


9.
Verifier must always be the final node.



==================================================
GRAPH CONSTRAINTS
==================================================


1.
Every agent must appear EXACTLY ONCE.


2.
IDs must be unique.


3.
"next" contains ONLY agent IDs.


Correct:

"next":[
 "researcher_1",
 "researcher_2"
]


Incorrect:

"next":[
 {
   "id":"researcher_1"
 }
]



4.
The graph must be acyclic.


5.
Every dependency must reference an existing agent.


6.
No disconnected nodes.


7.
Every workflow must have:

Planner

Task Splitter

At least one Researcher

Summarizer

Verifier



8.
For complex research tasks create at least THREE Researcher agents.



9.
Researcher nodes:

parallel=true



All other nodes:

parallel=false



10.
Return ONLY JSON.

"""



# =======================================================
# Model Configuration
# =======================================================


HF_MODEL = "meta-llama/Llama-3.1-8B-Instruct"

HF_PROVIDER = "novita"



# =======================================================
# HuggingFace Client
# =======================================================


def get_client():

    token = os.getenv("HF_TOKEN")


    if not token:

        raise RuntimeError(
            "HF_TOKEN missing in backend/.env"
        )


    client = InferenceClient(

        provider=HF_PROVIDER,

        api_key=token

    )


    return client



# =======================================================
# JSON Parser
# =======================================================


def extract_json(text):

    """
    Extract JSON from LLM response.
    Handles ```json blocks.
    """


    text = text.strip()


    # Remove markdown fences

    text = re.sub(

        r"```json",

        "",

        text,

        flags=re.IGNORECASE

    )


    text = re.sub(

        r"```",

        "",

        text

    )


    text = text.strip()



    match = re.search(

        r"\{.*\}",

        text,

        flags=re.DOTALL

    )


    if not match:

        raise ValueError(

            "No JSON found in model output:\n"
            + text

        )



    return json.loads(
        match.group()
    )



# =======================================================
# Planner Execution
# =======================================================


def run_planner(goal):


    client = get_client()



    response = client.chat.completions.create(


        model=HF_MODEL,


        temperature=0.2,


        messages=[


            {

                "role":"system",

                "content":PLANNER_SYSTEM_PROMPT

            },


            {

                "role":"user",

                "content":goal

            }


        ]

    )



    output = response.choices[0].message.content



    workflow = extract_json(output)



    return workflow




# =======================================================
# Simple Validation
# =======================================================


def validate_workflow(workflow):


    agents = workflow.get(
        "agents",
        []
    )


    ids = [
        agent["id"]
        for agent in agents
    ]



    # duplicate check

    if len(ids) != len(set(ids)):

        raise ValueError(
            "Duplicate agent IDs detected"
        )



    required = [

        "planner",

        "task_splitter",

        "summarizer",

        "verifier"

    ]


    for r in required:

        if r not in ids:

            raise ValueError(
                f"Missing {r}"
            )



    # check next references


    for agent in agents:


        for nxt in agent.get(
            "next",
            []
        ):


            if nxt not in ids:

                raise ValueError(
                    f"Invalid next reference {nxt}"
                )



    return True




# =======================================================
# CLI Testing
# =======================================================


if __name__ == "__main__":



    goal = input(
        "Enter your goal: "
    ).strip()



    if not goal:

        print(
            "Goal cannot be empty"
        )

        exit()



    try:


        workflow = run_planner(goal)



        validate_workflow(
            workflow
        )



        print(
            "\nGenerated Workflow\n"
        )


        print(

            json.dumps(

                workflow,

                indent=4

            )

        )



    except Exception as e:


        print(

            "\nError:",

            e

        )