import os
import uuid
import re
from datetime import datetime

from dotenv import load_dotenv

from graph.runner import run_workflow, node_names
from llm.provider_factory import get_provider
from utils.checkpoint import list_workflows, list_checkpoints, load_checkpoint
from utils.tee_logger import start_logging

load_dotenv()

def slugify(text: str, max_words: int = 5):

    text = text.lower()

    text = re.sub(r'[^a-z0-9\s]', '', text)

    words = text.split()

    return "_".join(words[:max_words])


def generate_conversation_name(goal: str):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    topic = slugify(goal)

    return f"{timestamp}_{topic}"


def current_time():

    return datetime.now().strftime("%d %b %Y %I:%M:%S %p")


# ==========================================================
# Provider Selection
# ==========================================================

def choose_provider():

    print("\n======================================")
    print("      SELECT LLM PROVIDER")
    print("======================================")

    print("1. Gemini")
    print("2. Groq")
    print("3. Ollama")

    choice = input("\nEnter Choice : ").strip()

    if choice == "1":
        return {
            "provider": "gemini",
            "model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            "api_key": os.getenv("GEMINI_API_KEY"),
            "base_url": None,
        }

    elif choice == "2":
        return {
            "provider": "groq",
            "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            "api_key": os.getenv("GROQ_API_KEY"),
            "base_url": "https://api.groq.com/openai/v1",
        }

    elif choice == "3":
        return {
            "provider": "ollama",
            "model": os.getenv("OLLAMA_MODEL", "llama3.1"),
            "api_key": "ollama",
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        }

    else:
        raise ValueError("Invalid Provider Selected")


def api_key_env_var(provider: str) -> str:
    return {
        "gemini": "GEMINI_API_KEY",
        "groq": "GROQ_API_KEY",
    }.get(provider, "")


# ==========================================================
# Initial Workflow State
# ==========================================================
'''
def create_state(goal, config):

    conversation_name = generate_conversation_name(goal)

    created_at = current_time()

    "workflow_id": workflow_id,

    "conversation_name": conversation_name,

    "created_at": created_at,

    llm = get_provider(
        provider=config["provider"],
        model=config["model"],
        api_key=config["api_key"],
        base_url=config["base_url"],
    )

    return {
        "workflow_id": str(uuid.uuid4()),
        "goal": goal,
        "status": "Running",
        "error": "",

        "provider": config["provider"],
        "model": config["model"],
        "api_key": config["api_key"],
        "hf_provider": "",
        "base_url": config["base_url"],
        "llm": llm,

        "plan": {},
        "tasks": [],

        "research_agent_1": {},
        "research_agent_2": {},
        "research_results": [],

        "summary": {},

        "verification": {},
        "final_output": {},

        "current_agent": "",
        "execution_trace": [],
    }
'''
def create_state(goal, config):

    workflow_id = str(uuid.uuid4())

    conversation_name = generate_conversation_name(goal)

    created_at = current_time()

    llm = get_provider(
        provider=config["provider"],
        model=config["model"],
        api_key=config["api_key"],
        base_url=config["base_url"],
    )

    return {
        "workflow_id": workflow_id,
        "conversation_name": conversation_name,
        "created_at": created_at,

        "goal": goal,
        "status": "Running",
        "error": "",

        "provider": config["provider"],
        "model": config["model"],
        "api_key": config["api_key"],
        "hf_provider": "",
        "base_url": config["base_url"],
        "llm": llm,

        "plan": {},
        "tasks": [],

        "research_agent_1": {},
        "research_agent_2": {},
        "research_results": [],

        "summary": {},

        "verification": {},
        "final_output": {},

        "current_agent": "",
        "execution_trace": [],
    }

# ==========================================================
# Rollback: rehydrate a loaded checkpoint into a runnable state
# ==========================================================

def rehydrate_state(state: dict) -> dict:
    """
    A loaded checkpoint has api_key redacted and no llm object
    (both were stripped before saving — see utils/checkpoint.py).
    This restores both so the workflow can resume execution.
    """

    provider = state["provider"]
    env_var = api_key_env_var(provider)

    api_key = os.getenv(env_var) if env_var else None

    if not api_key:
        if provider == "ollama":
            api_key = "ollama"
        else:
            api_key = input(
                f"\nAPI key for '{provider}' not found in .env — enter it now: "
            ).strip()

    state["api_key"] = api_key

    state["llm"] = get_provider(
        provider=provider,
        model=state["model"],
        api_key=api_key,
        base_url=state.get("base_url"),
    )

    return state


# ==========================================================
# Print final results (shared by new + resumed runs)
# ==========================================================

def print_results(result: dict):

    print("\n==============================================")
    print("WORKFLOW COMPLETED")
    print("==============================================")

    print("\nExecution Trace\n")
    for agent in result["execution_trace"]:
        print(f"✓ {agent}")

    print("\n==============================================")
    print("FINAL OUTPUT")
    print("==============================================")
    print(result["final_output"])

    if result["error"]:
        print("\n==============================================")
        print("ERROR")
        print("==============================================")
        print(result["error"])


# ==========================================================
# Flow: start a brand-new workflow
# ==========================================================

def run_new_workflow():

    config = choose_provider()
    goal = input("\nEnter Goal:\n\n> ")

    state = create_state(goal, config)

    start_logging(state["workflow_id"])

    print("\n==============================================")
    print(f"Conversation : {state['conversation_name']}")
    print(f"Created At   : {state['created_at']}")
    print(f"Workflow ID  : {state['workflow_id']}")
    print("==============================================")

    print("\n==============================================")
    print("Executing Workflow...")
    print("==============================================")

    result = run_workflow(state, start_index=0)

    print_results(result)


# ==========================================================
# Flow: roll back to a checkpoint and continue from there
# ==========================================================

def run_from_checkpoint():

    workflows = list_workflows()

    if not workflows:
        print("\nNo saved workflows found.")
        return

    print("\n======================================")
    print("      SAVED WORKFLOWS")
    print("======================================")

    for i, wf in enumerate(workflows, start=1):
        print(f"\n{i}. {wf['conversation_name']}")

        print(f"   Created : {wf['created_at']}")

    choice = input("\nSelect a workflow number: ").strip()

    try:
        workflow_id = workflows[int(choice)-1]["workflow_id"]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    checkpoints = list_checkpoints(workflow_id)

    if not checkpoints:
        print("\nNo checkpoints found for this workflow.")
        return

    print(f"\n======================================")
    print(f"      CHECKPOINTS — {workflow_id}")
    print("======================================")

    for i, cp in enumerate(checkpoints, start=1):
        print(
            f"{i}. [{cp['timestamp']}] Step {cp['step_index']} — "
            f"{cp['agent_name']} ({cp['status']})"
        )

    choice = input("\nRoll back to which checkpoint number: ").strip()

    try:
        selected = checkpoints[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    state, step_index, agent_name = load_checkpoint(workflow_id, selected["file"])

    state = rehydrate_state(state)

    start_logging(workflow_id)  # appends to the same workflow's log file

    print("\n==============================================")
    print(f"ROLLED BACK TO: {agent_name} (step {step_index})")
    print(f"RESUMING FROM: {node_names()[step_index + 1] if step_index + 1 < len(node_names()) else 'nothing — this was the last node'}")
    print("==============================================")

    result = run_workflow(state, start_index=step_index + 1)

    print_results(result)


# ==========================================================
# Main
# ==========================================================

def main():

    print("\n==============================================")
    print("      AGENTIC AI ORCHESTRATOR")
    print("==============================================")

    print("\n1. Start a new workflow")
    print("2. Roll back to a checkpoint and continue")

    choice = input("\nEnter Choice : ").strip()

    try:
        if choice == "1":
            run_new_workflow()
        elif choice == "2":
            run_from_checkpoint()
        else:
            print("Invalid choice.")

    except Exception as e:
        print("\nWorkflow Failed\n")
        print(e)


if __name__ == "__main__":
    main()