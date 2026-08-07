"""
planner.py

Planner Agent for Agentic AI Orchestrator.

Input:
    User goal + provider + model + api_key (all via CLI prompt)

Output:
    Typed workflow graph JSON

Supported providers:
    - gemini      (Google Generative AI)
    - openai      (OpenAI-compatible chat completions)
    - huggingface (HF InferenceClient — routes to novita, together, etc.)

Only the SDK for the provider you actually pick needs to be installed:
    pip install google-generativeai   # for gemini
    pip install openai                # for openai
    pip install huggingface_hub       # for huggingface
"""


import os
import json
import re
from pathlib import Path

from dotenv import load_dotenv


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
# Supported top-level providers
# =======================================================

SUPPORTED_PROVIDERS = ["gemini", "openai", "huggingface"]

# Sub-providers only relevant when top-level provider == "huggingface"
HF_ROUTED_PROVIDERS = [
    "novita",
    "together",
    "fireworks-ai",
    "sambanova",
    "hyperbolic",
    "nebius",
    "cerebras",
    "hf-inference",
]


# =======================================================
# Provider call functions
# =======================================================

def call_gemini(goal: str, model: str, api_key: str) -> str:
    """Calls Google Gemini via google-generativeai SDK."""
    try:
        import google.generativeai as genai
    except ImportError:
        raise RuntimeError(
            "google-generativeai not installed. Run: pip install google-generativeai"
        )

    if not api_key:
        raise RuntimeError("Gemini requires an api_key")

    genai.configure(api_key=api_key)

    gemini_model = genai.GenerativeModel(
        model_name=model,
        system_instruction=PLANNER_SYSTEM_PROMPT
    )

    response = gemini_model.generate_content(
        goal,
        generation_config={"temperature": 0.2}
    )

    return response.text


def call_openai(goal: str, model: str, api_key: str) -> str:
    """Calls OpenAI (or any OpenAI-compatible) chat completions endpoint."""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError(
            "openai package not installed. Run: pip install openai"
        )

    if not api_key:
        raise RuntimeError("OpenAI requires an api_key")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": goal},
        ],
    )

    return response.choices[0].message.content


def call_huggingface(goal: str, model: str, api_key: str, hf_provider: str) -> str:
    """Calls a model via HuggingFace InferenceClient, routed through hf_provider
    (e.g. novita, together, fireworks-ai)."""
    try:
        from huggingface_hub import InferenceClient
    except ImportError:
        raise RuntimeError(
            "huggingface_hub not installed. Run: pip install huggingface_hub"
        )

    token = api_key or os.getenv("HF_TOKEN")

    if not token:
        raise RuntimeError(
            "No API key provided and HF_TOKEN missing in backend/.env"
        )

    client = InferenceClient(provider=hf_provider, api_key=token)

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": goal},
        ],
    )

    return response.choices[0].message.content


# =======================================================
# JSON Parser
# =======================================================

def extract_json(text):
    """
    Extract JSON from LLM response.
    Handles ```json blocks.
    """

    text = text.strip()

    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)
    text = text.strip()

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)

    if not match:
        raise ValueError(
            "No JSON found in model output:\n" + text
        )

    return json.loads(match.group())


# =======================================================
# Planner Execution — dispatches to the right provider
# =======================================================

def run_planner(goal: str, provider: str, model: str, api_key: str = None, hf_provider: str = None):
    """
    Runs the planner agent against the chosen provider + model.

    Args:
        goal: the user's natural-language objective
        provider: "gemini" | "openai" | "huggingface"
        model: model name/id specific to that provider
        api_key: API key for the provider (falls back to .env for huggingface only)
        hf_provider: required only when provider == "huggingface"
                     (e.g. "novita", "together")
    """

    provider = provider.lower().strip()

    if provider == "gemini":
        output = call_gemini(goal, model, api_key)

    elif provider == "openai":
        output = call_openai(goal, model, api_key)

    elif provider == "huggingface":
        if not hf_provider:
            raise RuntimeError(
                "huggingface provider requires hf_provider (e.g. 'novita', 'together')"
            )
        output = call_huggingface(goal, model, api_key, hf_provider)

    else:
        raise RuntimeError(
            f"Unsupported provider '{provider}'. Choose from: {', '.join(SUPPORTED_PROVIDERS)}"
        )

    workflow = extract_json(output)

    return workflow


# =======================================================
# Simple Validation
# =======================================================

def validate_workflow(workflow):

    agents = workflow.get("agents", [])

    ids = [agent["id"] for agent in agents]

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate agent IDs detected")

    required = [
        "planner",
        "task_splitter",
        "summarizer",
        "verifier"
    ]

    for r in required:
        if r not in ids:
            raise ValueError(f"Missing {r}")

    for agent in agents:
        for nxt in agent.get("next", []):
            if nxt not in ids:
                raise ValueError(f"Invalid next reference {nxt}")

    return True


# =======================================================
# CLI Testing
# =======================================================

if __name__ == "__main__":

    goal = input("Enter your goal: ").strip()

    if not goal:
        print("Goal cannot be empty")
        exit()

    print(f"\nSupported providers: {', '.join(SUPPORTED_PROVIDERS)}")
    provider = input("Enter provider (gemini / openai / huggingface): ").strip().lower()

    if provider not in SUPPORTED_PROVIDERS:
        print(f"Unsupported provider '{provider}'. Choose from: {', '.join(SUPPORTED_PROVIDERS)}")
        exit()

    hf_provider = None
    if provider == "huggingface":
        print(f"HF-routed providers: {', '.join(HF_ROUTED_PROVIDERS)}")
        hf_provider = input("Enter HF routed provider (e.g. novita): ").strip().lower()
        if not hf_provider:
            print("hf_provider cannot be empty for huggingface")
            exit()

    model = input("Enter model name (e.g. gemini-2.5-flash / gpt-4o / meta-llama/Llama-3.1-8B-Instruct): ").strip()

    if not model:
        print("Model cannot be empty")
        exit()

    api_key = input(
        "Enter API key (leave blank to use HF_TOKEN from .env — huggingface only): "
    ).strip()

    api_key = api_key or None

    try:
        workflow = run_planner(
            goal=goal,
            provider=provider,
            model=model,
            api_key=api_key,
            hf_provider=hf_provider
        )

        validate_workflow(workflow)

        print("\nGenerated Workflow\n")
        print(json.dumps(workflow, indent=4))

    except Exception as e:
        print("\nError:", e)

    # =======================================================
# LangGraph Node Wrapper
# =======================================================

from graph.state import WorkflowState


from graph.state import WorkflowState


def planner_node(state: WorkflowState):
    """
    LangGraph Planner Node
    """

    print("\n========== Planner ==========\n")

    state["current_agent"] = "Planner"

    if "execution_trace" not in state:
        state["execution_trace"] = []

    state["execution_trace"].append("Planner")

    try:

        workflow = run_planner(
            goal=state["goal"],
            provider=state["provider"],
            model=state["model"],
            api_key=state["api_key"],
            hf_provider=state.get("hf_provider")
        )

        validate_workflow(workflow)

        state["plan"] = workflow

        state["status"] = "Planner Completed"

        print("Planner Finished Successfully")

    except Exception as e:

        state["status"] = "Planner Failed"

        state["error"] = str(e)

        print(e)

    return state