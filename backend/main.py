import os
import uuid

from dotenv import load_dotenv

from graph.builder import build_workflow
from llm.provider_factory import get_provider

load_dotenv()


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

            "model": os.getenv(
                "GEMINI_MODEL",
                "gemini-2.0-flash"
            ),

            "api_key": os.getenv(
                "GEMINI_API_KEY"
            ),

            "base_url": None

        }

    elif choice == "2":

        return {

            "provider": "groq",

            "model": os.getenv(
                "GROQ_MODEL",
                "llama-3.3-70b-versatile"
            ),

            "api_key": os.getenv(
                "GROQ_API_KEY"
            ),

            "base_url": "https://api.groq.com/openai/v1"

        }

    elif choice == "3":

        return {

            "provider": "ollama",

            "model": os.getenv(
                "OLLAMA_MODEL",
                "llama3.1"
            ),

            "api_key": "ollama",

            "base_url": os.getenv(
                "OLLAMA_BASE_URL",
                "http://localhost:11434/v1"
            )

        }

    else:

        raise ValueError("Invalid Provider Selected")


# ==========================================================
# Initial Workflow State
# ==========================================================

def create_state(goal, config):

    llm = get_provider(

        provider=config["provider"],

        model=config["model"],

        api_key=config["api_key"],

        base_url=config["base_url"]

    )

    return {

        # =========================================
        # Workflow
        # =========================================

        "workflow_id": str(uuid.uuid4()),

        "goal": goal,

        "status": "Running",

        "error": "",

        # =========================================
        # LLM
        # =========================================

        "provider": config["provider"],

        "model": config["model"],

        "api_key": config["api_key"],

        "hf_provider": "",

        "llm": llm,

        # =========================================
        # Planner
        # =========================================

        "plan": {},

        # =========================================
        # Task Splitter
        # =========================================

        "tasks": [],

        # =========================================
        # Research
        # =========================================

        "research_agent_1": {},

        "research_agent_2": {},

        "research_results": [],

        # =========================================
        # Summarizer
        # =========================================

        "summary": {},

        # =========================================
        # Verifier
        # =========================================

        "verification": {},

        "final_output": {},

        # =========================================
        # Execution
        # =========================================

        "current_agent": "",

        "execution_trace": []

    }


# ==========================================================
# Main
# ==========================================================

def main():

    print("\n==============================================")
    print("      AGENTIC AI ORCHESTRATOR")
    print("==============================================")

    try:

        config = choose_provider()

        goal = input("\nEnter Goal:\n\n> ")

        state = create_state(
            goal,
            config
        )

        workflow = build_workflow()

        print("\n==============================================")
        print("Executing Workflow...")
        print("==============================================")

        result = workflow.invoke(state)

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

    except Exception as e:

        print("\nWorkflow Failed\n")

        print(e)


if __name__ == "__main__":
    main()