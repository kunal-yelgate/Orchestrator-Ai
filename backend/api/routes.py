<<<<<<< HEAD
import os
import uuid

=======
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import uuid
import os
import re
from datetime import datetime
from pathlib import Path
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

<<<<<<< HEAD
from api.schemas import OrchestrateRequest, OrchestrateResponse
from graph.builder import build_workflow
=======
load_dotenv()

from api.schemas import (
    OrchestrateRequest,
    OrchestrateResponse,
    UploadResponse,
    WorkflowSummary,
    CheckpointSummary,
    RollbackRequest,
)

from agents.retrieval_agent import SUPPORTED_EXTENSIONS
from graph.runner import run_workflow, node_names
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
from llm.provider_factory import get_provider
from llm.fallback_provider import FallbackProvider
from utils.checkpoint import list_workflows, list_checkpoints, load_checkpoint

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


<<<<<<< HEAD
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
=======
# ==========================================================
# Upload a document for later retrieval
#
# Frontend flow for "upload file + prompt together": the file is POSTed
# here first (independently of the prompt), and the returned server-side
# `path` is then included in the `documents` list of the /orchestrate
# call that carries the user's prompt. Multiple files just means multiple
# /upload calls before the single /orchestrate call.
# ==========================================================

@router.post("/upload", response_model=UploadResponse)
def upload_document(file: UploadFile = File(...)):

    ext = Path(file.filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    safe_name = f"{uuid.uuid4().hex[:10]}_{file.filename}"

    path = os.path.join(UPLOAD_DIR, safe_name)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return UploadResponse(
        path=path,
        filename=file.filename,
    )


# ==========================================================
# Small helpers (conversation naming / provider config)
# ==========================================================

def _slugify(text: str, max_words: int = 5) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    words = text.split()
    return "_".join(words[:max_words])


def _generate_conversation_name(goal: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic = _slugify(goal)
    return f"{timestamp}_{topic}"


def _current_time() -> str:
    return datetime.now().strftime("%d %b %Y %I:%M:%S %p")


def _provider_config(provider: str):
    provider = provider.lower()

    if provider == "gemini":
        return {
            "model": "gemini-2.0-flash",
            "api_key": os.getenv("GEMINI_API_KEY"),
            "base_url": None,
        }

    if provider == "groq":
        return {
            "model": "llama-3.3-70b-versatile",
            "api_key": os.getenv("GROQ_API_KEY"),
            "base_url": "https://api.groq.com/openai/v1",
        }

    if provider == "ollama":
        return {
            "model": "llama3.1",
            "api_key": "ollama",
            "base_url": "http://localhost:11434/v1",
        }

    raise ValueError("Unsupported provider")


# ==========================================================
# Automatic Provider Fallback
#
# If the requested provider fails at generation time, the LLM
# transparently retries the same call on a fallback provider so the
# workflow can continue instead of halting the whole run. See
# llm/fallback_provider.py for the actual failover logic.
# ==========================================================

def _default_fallback_provider(provider: str) -> str:
    # Gemini is the default safety net for everything except itself,
    # in which case Groq is used instead.
    return "groq" if provider == "gemini" else "gemini"


def _try_build_provider(provider: str):
    """
    Best-effort provider construction. Returns None instead of raising
    when the provider can't be built (e.g. its API key isn't configured
    in this environment) -- a missing fallback should never prevent the
    primary provider from being used.
    """

    try:
        cfg = _provider_config(provider)

        return get_provider(
            provider=provider,
            model=cfg["model"],
            api_key=cfg["api_key"],
            base_url=cfg["base_url"],
        ), cfg

    except Exception as e:
        print(f"[Provider Fallback] Could not prepare '{provider}' as a fallback: {e}")
        return None, None


def _build_llm_with_fallback(provider: str, provider_events: list):
    """
    Builds the primary provider (must succeed -- this is the provider the
    user actually asked for) and wraps it with a best-effort fallback
    provider. Returns (llm, primary_cfg, fallback_provider_name).
    """

    primary_cfg = _provider_config(provider)

    primary_llm = get_provider(
        provider=provider,
        model=primary_cfg["model"],
        api_key=primary_cfg["api_key"],
        base_url=primary_cfg["base_url"],
    )

    fallback_name = _default_fallback_provider(provider)
    fallback_llm, _ = _try_build_provider(fallback_name)

    if fallback_llm is None:
        fallback_name = ""

    llm = FallbackProvider(
        primary=primary_llm,
        primary_name=provider,
        fallback=fallback_llm,
        fallback_name=fallback_name,
        on_fallback=provider_events.append,
    )

    return llm, primary_cfg, fallback_name


# ==========================================================
# Create Workflow State
# ==========================================================

def create_state(goal: str, provider: str, documents=None):

    provider = provider.lower()

    # `provider_events` is mutated in place by FallbackProvider (via the
    # on_fallback callback above) every time a fallback happens, so the
    # same list object is stored on state and returned to the client.
    provider_events: list = []

    llm, cfg, fallback_provider = _build_llm_with_fallback(
        provider,
        provider_events,
    )
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0

    return {
        "workflow_id": str(uuid.uuid4()),
<<<<<<< HEAD
        "conversation_name": "",
        "created_at": "",
        "goal": goal,
        "status": "",
=======

        "conversation_name": _generate_conversation_name(goal),

        "created_at": _current_time(),

        "goal": goal,

        "status": "Running",

>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
        "error": "",
        "provider": provider,
<<<<<<< HEAD
        "model": model,
        "api_key": "",
        "hf_provider": "",
        "llm": llm,
=======

        "model": cfg["model"],

        # Stored so a rollback can rehydrate the LLM later. Never returned
        # to the client — utils/checkpoint.py redacts it before writing
        # any checkpoint to disk.
        "api_key": cfg["api_key"],

        "hf_provider": "",

        "base_url": cfg["base_url"],

        "llm": llm,

        "fallback_provider": fallback_provider,

        "provider_events": provider_events,

>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
        "plan": {},
        "workflow_name": "",
        "execution_mode": "",
        "reasoning": "",
        "tasks": [],
        "current_task": {},
        "research_results": [],
<<<<<<< HEAD
=======

        "research_failures": [],

        "partial_failure": False,

>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
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
        "approved": False,
        "workflow_version": "1.0",
    }


<<<<<<< HEAD
=======
# ==========================================================
# Rehydrate a loaded checkpoint (API-safe: no interactive input())
# ==========================================================

def _api_key_env_var(provider: str) -> str:
    return {
        "gemini": "GEMINI_API_KEY",
        "groq": "GROQ_API_KEY",
    }.get(provider, "")


def rehydrate_state(state: dict) -> dict:
    """
    A loaded checkpoint has api_key redacted and no llm object (both are
    stripped before saving — see utils/checkpoint.py). This restores both
    so the workflow can resume execution from the server environment.
    """

    provider = state.get("provider", "").lower()
    env_var = _api_key_env_var(provider)

    api_key = os.getenv(env_var) if env_var else None

    if not api_key:
        api_key = "ollama" if provider == "ollama" else None

    if not api_key:
        raise HTTPException(
            status_code=400,
            detail=f"API key for provider '{provider}' not found in server environment.",
        )

    state["api_key"] = api_key

    primary_llm = get_provider(
        provider=provider,
        model=state.get("model", ""),
        api_key=api_key,
        base_url=state.get("base_url"),
    )

    # Preserve provider_events across rollback/resume instead of resetting
    # it, so the full fallback history for this workflow_id survives.
    provider_events = state.get("provider_events") or []
    state["provider_events"] = provider_events

    fallback_name = _default_fallback_provider(provider)
    fallback_llm, _ = _try_build_provider(fallback_name)

    state["fallback_provider"] = fallback_name if fallback_llm else ""

    state["llm"] = FallbackProvider(
        primary=primary_llm,
        primary_name=provider,
        fallback=fallback_llm,
        fallback_name=state["fallback_provider"],
        on_fallback=provider_events.append,
    )

    # Older checkpoints (saved before Feature 5) won't have these keys.
    state.setdefault("research_failures", [])
    state.setdefault("partial_failure", False)

    return state


def _to_orchestrate_response(result: dict) -> OrchestrateResponse:
    trace = result.get("execution_trace", [])
    names = node_names()

    last_agent_name = trace[-1] if trace else None
    last_step_index = names.index(last_agent_name) if last_agent_name in names else None

    return OrchestrateResponse(
        workflow_id=result["workflow_id"],
        execution_trace=trace,
        retrieval=result.get("retrieval", {}),
        summary=result.get("summary", {}),
        verification=result.get("verification", {}),
        final_output=result.get("final_output", {}),
        status=result.get("status", ""),
        error=result.get("error", ""),
        last_step_index=last_step_index,
        last_agent_name=last_agent_name,
        provider_events=result.get("provider_events", []),
        research_failures=result.get("research_failures", []),
        partial_failure=result.get("partial_failure", False),
    )


# ==========================================================
# Main Orchestration Endpoint
#
# Uses graph/runner.py's run_workflow() (not the compiled LangGraph's
# .invoke()) so that a checkpoint is written to disk after every single
# node — this is what makes GET /workflows/{id}/checkpoints and
# POST /workflows/{id}/rollback below possible.
# ==========================================================

>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
@router.post(
    "/orchestrate",
    response_model=OrchestrateResponse,
)
def orchestrate(request: OrchestrateRequest):
    try:
<<<<<<< HEAD
        workflow = build_workflow()
=======
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0

        state = create_state(
            goal=request.goal,
            provider=request.provider,
        )

        result = run_workflow(state, start_index=0)

<<<<<<< HEAD
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
        )
=======
        return _to_orchestrate_response(result)

    except HTTPException:
        raise
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0

    except Exception as error:
        raise HTTPException(
            status_code=500,
<<<<<<< HEAD
            detail=str(error),
        )
=======
            detail=str(e)
        )


# ==========================================================
# List saved workflows (for a checkpoint picker)
# ==========================================================

@router.get("/workflows", response_model=List[WorkflowSummary])
def get_workflows():
    return list_workflows()


# ==========================================================
# List checkpoints for a workflow — one entry per graph node that
# completed. The frontend uses `agent_name` to match a checkpoint back
# to the node the user clicked in the graph.
# ==========================================================

@router.get("/workflows/{workflow_id}/checkpoints", response_model=List[CheckpointSummary])
def get_checkpoints(workflow_id: str):

    checkpoints = list_checkpoints(workflow_id)

    if not checkpoints:
        raise HTTPException(status_code=404, detail="No checkpoints found for this workflow")

    return checkpoints


# ==========================================================
# Roll back to a checkpoint and resume execution from the next node.
#
# This is what powers "click a node on the graph, revert to that state,
# and continue execution from there" in the UI.
# ==========================================================

@router.post("/workflows/{workflow_id}/rollback", response_model=OrchestrateResponse)
def rollback_workflow(workflow_id: str, request: RollbackRequest):

    try:
        state, step_index, agent_name = load_checkpoint(workflow_id, request.checkpoint_file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    state = rehydrate_state(state)

    try:
        result = run_workflow(state, start_index=step_index + 1)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return _to_orchestrate_response(result)
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
