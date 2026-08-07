from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import uuid
import os
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

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
from llm.provider_factory import get_provider
from utils.checkpoint import list_workflows, list_checkpoints, load_checkpoint


router = APIRouter()

UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "uploads",
)


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
# Create Workflow State
# ==========================================================

def create_state(goal: str, provider: str, documents=None):

    provider = provider.lower()
    cfg = _provider_config(provider)

    llm = get_provider(
        provider=provider,
        model=cfg["model"],
        api_key=cfg["api_key"],
        base_url=cfg["base_url"],
    )

    return {

        "workflow_id": str(uuid.uuid4()),

        "conversation_name": _generate_conversation_name(goal),

        "created_at": _current_time(),

        "goal": goal,

        "status": "Running",

        "error": "",

        "provider": provider,

        "model": cfg["model"],

        # Stored so a rollback can rehydrate the LLM later. Never returned
        # to the client — utils/checkpoint.py redacts it before writing
        # any checkpoint to disk.
        "api_key": cfg["api_key"],

        "hf_provider": "",

        "base_url": cfg["base_url"],

        "llm": llm,

        "plan": {},

        "needs_retrieval": False,

        "documents": documents or [],

        "retrieval": {},

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

    state["llm"] = get_provider(
        provider=provider,
        model=state.get("model", ""),
        api_key=api_key,
        base_url=state.get("base_url"),
    )

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
    )


# ==========================================================
# Main Orchestration Endpoint
#
# Uses graph/runner.py's run_workflow() (not the compiled LangGraph's
# .invoke()) so that a checkpoint is written to disk after every single
# node — this is what makes GET /workflows/{id}/checkpoints and
# POST /workflows/{id}/rollback below possible.
# ==========================================================

@router.post(
    "/orchestrate",
    response_model=OrchestrateResponse
)
def orchestrate(request: OrchestrateRequest):

    try:

        state = create_state(
            request.goal,
            request.provider,
            request.documents,
        )

        result = run_workflow(state, start_index=0)

        return _to_orchestrate_response(result)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
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
