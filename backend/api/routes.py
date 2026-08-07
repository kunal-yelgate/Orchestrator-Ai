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
        "version": "2.0"
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
# Providers
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

        # ==================================================
        # Workflow Info
        # ==================================================

        "workflow_id": str(uuid.uuid4()),
        "conversation_name": "",
        "created_at": "",

        "goal": goal,

        "status": "",
        "error": "",

        # ==================================================
        # LLM
        # ==================================================

        "provider": provider,
        "model": "",
        "api_key": "",
        "hf_provider": "",

        "llm": llm,

        # ==================================================
        # Planner
        # ==================================================

        "plan": {},

        "workflow_name": "",
        "execution_mode": "",
        "reasoning": "",

        "tasks": [],

        "current_task": {},

        # ==================================================
        # Research
        # ==================================================

        "research_results": [],

        # ==================================================
        # Final Output
        # ==================================================

        "summary": {},

        "verification": {},

        "final_output": {},

        # ==================================================
        # Execution
        # ==================================================

        "current_agent": "",

        "execution_trace": [],

        "execution_time": 0.0,

        "active_nodes": [],

        "completed_nodes": [],

        "failed_nodes": [],

        # ==================================================
        # Cost Tracking
        # ==================================================

        "total_tokens": 0,

        "prompt_tokens": 0,

        "completion_tokens": 0,

        "estimated_cost": 0.0,

        # ==================================================
        # Approval
        # ==================================================

        "approved": False,

        "workflow_version": "1.0"

    }


# ==========================================================
# Main Endpoint
# ==========================================================

@router.post(
    "/orchestrate",
    response_model=OrchestrateResponse,
)
def orchestrate(request: OrchestrateRequest):

    try:

        workflow = build_workflow()

        state = create_state(
            request.goal,
            request.provider,
        )

        result = workflow.invoke(state)

        return OrchestrateResponse(

            workflow_id=result["workflow_id"],

            execution_trace=result.get(
                "execution_trace",
                [],
            ),

            summary=result.get(
                "summary",
                {},
            ),

            verification=result.get(
                "verification",
                {},
            ),

        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )