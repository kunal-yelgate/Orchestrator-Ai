"""
checkpoint.py

Saves workflow state to a JSON file after every agent node completes.
Each checkpoint is timestamped and indexed so a workflow can be listed,
inspected, and rolled back to any prior step.

Checkpoints are stored at:
    backend/checkpoints/<workflow_id>/<step>_<agent>_<timestamp>.json
    backend/checkpoints/<workflow_id>/_index.json   (ordered manifest)

SECURITY: api_key is never written to disk. It is redacted before
serialization and must be re-supplied (from .env or prompt) on rollback.
"""

import json
import os
from datetime import datetime, timezone

CHECKPOINT_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "checkpoints"
)

# Keys that must never be persisted to disk
NON_SERIALIZABLE_KEYS = {"llm"}
REDACTED_KEYS = {"api_key"}


def _checkpoint_dir(workflow_id: str) -> str:
    path = os.path.join(CHECKPOINT_ROOT, workflow_id)
    os.makedirs(path, exist_ok=True)
    return path


def _index_path(workflow_id: str) -> str:
    return os.path.join(_checkpoint_dir(workflow_id), "_index.json")


def _sanitize_state(state: dict) -> dict:
    """Strip non-serializable objects and redact secrets before saving."""
    clean = {}
    for key, value in state.items():
        if key in NON_SERIALIZABLE_KEYS:
            continue
        if key in REDACTED_KEYS:
            clean[key] = "***REDACTED***"
            continue
        clean[key] = value
    return clean


def _update_index(workflow_id: str, entry: dict):
    path = _index_path(workflow_id)
    entries = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)
    entries.append(entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def save_checkpoint(state: dict, agent_name: str, step_index: int) -> str:
    """Persist the current state after `agent_name` finishes. Returns filepath."""
    workflow_id = state["workflow_id"]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    filename = f"{step_index:02d}_{agent_name}_{timestamp}.json"
    filepath = os.path.join(_checkpoint_dir(workflow_id), filename)

    payload = {
        "workflow_id": workflow_id,
        "step_index": step_index,
        "agent_name": agent_name,
        "timestamp": timestamp,
        "status": state.get("status", ""),
        "state": _sanitize_state(state),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    _update_index(workflow_id, {
        "step_index": step_index,
        "agent_name": agent_name,
        "timestamp": timestamp,
        "status": state.get("status", ""),
        "file": filename,
    })

    return filepath


def list_workflows() -> list:
    """Return all workflow_ids that have at least one checkpoint."""
    if not os.path.isdir(CHECKPOINT_ROOT):
        return []
    return sorted(
        d for d in os.listdir(CHECKPOINT_ROOT)
        if os.path.isdir(os.path.join(CHECKPOINT_ROOT, d))
    )


def list_checkpoints(workflow_id: str) -> list:
    """Return the ordered manifest of checkpoints for a workflow."""
    path = _index_path(workflow_id)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_checkpoint(workflow_id: str, filename: str):
    """Load a specific checkpoint file. Returns (state, step_index, agent_name)."""
    filepath = os.path.join(_checkpoint_dir(workflow_id), filename)
    with open(filepath, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload["state"], payload["step_index"], payload["agent_name"]