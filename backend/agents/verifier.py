import os
from typing import Any, Dict, Optional


class Verifier:
    """Simple orchestrator-style router for selecting an LLM provider."""

    def __init__(self) -> None:
        self.provider_keys = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
            "groq": "GROQ_API_KEY",
        }

        self.default_models = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-haiku",
            "gemini": "gemini-1.5-flash",
            "groq": "llama-3.1-8b-instant",
        }

    def _has_provider_key(self, provider: str, env: Optional[Dict[str, str]] = None) -> bool:
        keys = self.provider_keys.get(provider, [])
        if isinstance(keys, str):
            keys = [keys]

        source = env or os.environ
        return any(bool(source.get(key)) for key in keys)

    def select_llm(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Choose the best provider for a task based on keywords and available credentials."""
        task_text = (task or "").lower()
        context = context or {}

        preferred_provider = str(context.get("preferred_provider", "")).strip().lower()
        if preferred_provider and self._has_provider_key(preferred_provider):
            return {
                "provider": preferred_provider,
                "model": self.default_models.get(preferred_provider, "default-model"),
                "reason": "Preferred provider is available",
            }

        if any(word in task_text for word in ["code", "debug", "implement", "refactor", "script"]):
            if self._has_provider_key("openai"):
                return self._build_result("openai", "Strong coding and reasoning support")
            if self._has_provider_key("anthropic"):
                return self._build_result("anthropic", "Good fallback for coding tasks")

        if any(word in task_text for word in ["research", "summarize", "long", "document", "analysis"]):
            if self._has_provider_key("anthropic"):
                return self._build_result("anthropic", "Good for long-context reasoning")
            if self._has_provider_key("openai"):
                return self._build_result("openai", "Balanced long-context performance")

        if any(word in task_text for word in ["image", "vision", "ocr", "video"]):
            if self._has_provider_key("gemini"):
                return self._build_result("gemini", "Good multimodal support")
            if self._has_provider_key("openai"):
                return self._build_result("openai", "Fallback multimodal option")

        if any(word in task_text for word in ["fast", "cheap", "simple", "quick"]):
            if self._has_provider_key("groq"):
                return self._build_result("groq", "Fast and low-latency choice")

        for provider in ["openai", "anthropic", "gemini", "groq"]:
            if self._has_provider_key(provider):
                return self._build_result(provider, "Fallback provider selected")

        return {
            "provider": "local",
            "model": "local-model",
            "reason": "No supported API key detected; use a local or hosted fallback",
        }

    def _build_result(self, provider: str, reason: str) -> Dict[str, Any]:
        return {
            "provider": provider,
            "model": self.default_models.get(provider, "default-model"),
            "reason": reason,
        }


def route_task(task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience wrapper for the verifier router."""
    return Verifier().select_llm(task, context)


__all__ = ["Verifier", "route_task"]
