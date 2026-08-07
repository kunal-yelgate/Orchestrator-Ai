from fastapi import APIRouter, HTTPException
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

from api.schemas import (
    OrchestrateRequest,
    OrchestrateResponse,
)

from graph.builder import build_workflow
from llm.provider_factory import get_provider


router = APIRouter()


# ==========================================================
# Health Check
# ==========================================================

@router.get("/")
def home():

    return {
        "message": "Agentic AI Orchestrator API",
        "version": "1.0"
    }


# ==========================================================
# Health Endpoint
# ==========================================================

@router.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ==========================================================
# Available Providers
# ==========================================================

@router.get("/providers")
def providers():

    return {
        "providers": [
            "gemini",
            "groq",
            "ollama"
        ]
    }


# ==========================================================
# Create Workflow State
# ==========================================================

def create_state(goal: str, provider: str):

    provider = provider.lower()

    if provider == "gemini":

        llm = get_provider(
            provider="gemini",
            model="gemini-2.0-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
        )

    elif provider == "groq":

        llm = get_provider(
            provider="groq",
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )

    elif provider == "ollama":

        llm = get_provider(
            provider="ollama",
            model="llama3.1",
            api_key="ollama",
            base_url="http://localhost:11434/v1",
        )

    else:

        raise ValueError("Unsupported provider")

    return {

        "workflow_id": str(uuid.uuid4()),

        "goal": goal,

        "status": "",

        "error": "",

        "provider": provider,

        "llm": llm,

        "plan": {},

        "tasks": [],

        "research_agent_1": {},

        "research_agent_2": {},

        "research_results": [],

        "summary": {},

        "verification": {},

        "final_output": {},

        "execution_trace": [],

        "current_agent": ""
    }


# ==========================================================
# Main Orchestration Endpoint
# ==========================================================

@router.post(
    "/orchestrate",
    response_model=OrchestrateResponse
)
def orchestrate(request: OrchestrateRequest):

    try:

        workflow = build_workflow()

        state = create_state(
            request.goal,
            request.provider
        )

        result = workflow.invoke(state)

        return OrchestrateResponse(

            workflow_id=result["workflow_id"],

            execution_trace=result["execution_trace"],

            summary=result["summary"],

            verification=result["verification"]

        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )