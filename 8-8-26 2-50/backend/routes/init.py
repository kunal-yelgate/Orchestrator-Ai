"""
routes/init.py

API 1: Initialize Provider – accepts user input, tests provider connection,
and returns a provider_id for later use.
"""

from fastapi import APIRouter
import uuid

from models.requests import InitRequest
from models.responses import InitResponse, ProviderInfo
from utils.logger import logger
from utils.registry import register_provider
from llm.provider_factory import get_llm  # <-- UPDATED IMPORT

router = APIRouter()

# List of Gemini models with free‑tier quota – ordered by preference
FALLBACK_MODELS = [
    "gemini-3-flash-preview",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.1-flash-lite",
]

@router.post("/api/init", response_model=InitResponse)
async def initialize_provider(req: InitRequest):
    """
    Initialize a provider (Gemini or Ollama) and return a provider_id.
    """
    provider_id = f"prov_{uuid.uuid4().hex[:8]}"
    name = req.provider.capitalize()

    # -------- GEMINI (with fallback) --------
    if req.provider.lower() == "gemini":
        models_to_try = [req.model] + [m for m in FALLBACK_MODELS if m != req.model]
        last_error = None

        for model in models_to_try:
            try:
                logger.info(f"Attempting to connect with model: {model}")
                llm = get_llm("gemini", model, req.api_key)
                llm.generate(prompt="Test connection", max_tokens=100)
                register_provider(provider_id, llm)
                logger.info(f"✅ Connected with model: {model}")
                return InitResponse(
                    success=True,
                    provider_id=provider_id,
                    provider=ProviderInfo(
                        name=name,
                        type="commercial",
                        model=model,
                        status="connected"
                    )
                )
            except Exception as e:
                error_str = str(e)
                last_error = error_str
                if ("429" in error_str or "quota" in error_str.lower() or
                    "response.text" in error_str or "finish_reason" in error_str or
                    "cut off" in error_str.lower()):
                    logger.warning(f"Model {model} failed (retryable): {error_str}")
                    continue
                else:
                    logger.error(f"Model {model} failed (non‑retryable): {error_str}")
                    break

        return InitResponse(
            success=False,
            provider_id=provider_id,
            provider=ProviderInfo(
                name=name,
                type="commercial",
                model=req.model,
                status=f"failed: no working model. Last error: {last_error}"
            )
        )

    # -------- OLLAMA --------
    if req.provider.lower() == "ollama":
        try:
            llm = get_llm("ollama", req.model)
            llm.generate(prompt="Test connection", max_tokens=5)
            register_provider(provider_id, llm)
            logger.info(f"✅ Ollama connected: {req.model}")
            return InitResponse(
                success=True,
                provider_id=provider_id,
                provider=ProviderInfo(
                    name="Ollama",
                    type="local",
                    model=req.model,
                    status="connected"
                )
            )
        except Exception as e:
            status = f"failed: {str(e)}"
            logger.error(f"Ollama connection error: {e}")
            return InitResponse(
                success=False,
                provider_id=provider_id,
                provider=ProviderInfo(
                    name="Ollama",
                    type="local",
                    model=req.model,
                    status=status
                )
            )

    # -------- UNSUPPORTED PROVIDER --------
    return InitResponse(
        success=False,
        provider_id=provider_id,
        provider=ProviderInfo(
            name=name,
            type="unknown",
            model=req.model,
            status=f"failed: unsupported provider '{req.provider}'"
        )
    )