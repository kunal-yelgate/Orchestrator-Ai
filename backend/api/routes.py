import os
import uuid

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

from api.schemas import OrchestrateRequest, OrchestrateResponse
from config.agent_config import AGENT_CONFIGS
from graph.builder import build_workflow
from llm.provider_factory import get_provider

load_dotenv()

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "Agentic AI Orchestrator API",
        "version": "2.0",
    }


@router.get("/health")
def health():
    return {
        "status": "healthy",
    }


@router.get("/providers")
def providers():
    return {
        "providers": [
            "gemini",
            "groq",
            "ollama",
        ]
    }


def create_state(goal: str, provider: str):
    provider = provider.lower()

    if provider == "gemini":
        llm = get_provider(
            provider="gemini",
            model="gemini-2.0-flash",
            api_key=os.getenv("GEMINI_API_KEY"),
        )
        model = "gemini-2.0-flash"

    elif provider == "groq":
        llm = get_provider(
            provider="groq",
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        model = "llama-3.3-70b-versatile"

    elif provider == "ollama":
        llm = get_provider(
            provider="ollama",
            model="llama3.1",
            api_key="ollama",
            base_url="http://localhost:11434/v1",
        )
        model = "llama3.1"

    else:
        raise ValueError("Unsupported provider")

    return {
        "workflow_id": str(uuid.uuid4()),
        "conversation_name": "",
        "created_at": "",
        "goal": goal,
        "status": "",
        "error": "",
        "provider": provider,
        "model": model,
        "api_key": "",
        "hf_provider": "",
        "llm": llm,
        "plan": {},
        "workflow_name": "",
        "execution_mode": "",
        "reasoning": "",
        "tasks": [],
        "current_task": {},
        "research_results": [],
        "summary": {},
        "verification": {},
        "final_output": {},
        "current_agent": "",
        "execution_trace": [],
        "execution_time": 0.0,
        "active_nodes": [],
        "completed_nodes": [],
        "failed_nodes": [],
        "total_tokens": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "estimated_cost": 0.0,
        "retry_count": 0,
        "approved": False,
        "workflow_version": "1.0",
    }


@router.post(
    "/orchestrate",
    response_model=OrchestrateResponse,
)
def orchestrate(request: OrchestrateRequest):
    try:
        workflow = build_workflow()

        state = create_state(
            goal=request.goal,
            provider=request.provider,
        )

        result = workflow.invoke(state)

        max_tokens = AGENT_CONFIGS["Researcher"].max_tokens
        used = result.get("total_tokens", 0)
        remaining = max(0, max_tokens - used)
        utilization = (
            round((used / max_tokens) * 100, 2)
            if max_tokens
            else 0.0
        )

        return OrchestrateResponse(
            workflow_id=result["workflow_id"],
            tasks=result.get("tasks", []),
            execution_trace=result.get("execution_trace", []),
            summary=result.get("summary", {}),
            verification=result.get("verification", {}),
            execution_time=result.get("execution_time", 0.0),
            total_tokens=result.get("total_tokens", 0),
            prompt_tokens=result.get("prompt_tokens", 0),
            completion_tokens=result.get("completion_tokens", 0),
            estimated_cost=result.get("estimated_cost", 0.0),
            provider=result.get("provider", ""),
            model=result.get("model", ""),
            retry_count=result.get("retry_count", 0),
            budget={
                "max_tokens": max_tokens,
                "used_tokens": used,
                "remaining_tokens": remaining,
                "utilization": utilization,
            },
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
