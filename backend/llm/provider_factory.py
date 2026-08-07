"""
Universal LLM Provider Factory

Currently Supported:
- Gemini
- OpenAI Compatible APIs (Groq, Ollama, Together, DeepSeek, Mistral, etc.)

Anthropic can be added later by creating:
    llm/adapters/anthropic.py
"""

from llm.adapters.openai_compatible import OpenAICompatible
from llm.adapters.gemini import GeminiProvider


def get_provider(
    provider: str,
    model: str,
    api_key: str,
    base_url: str = None
):
    provider = provider.lower().strip()

    # Native Gemini API
    if provider == "gemini":
        return GeminiProvider(
            model=model,
            api_key=api_key
        )

    # OpenAI Compatible Providers
    # Examples:
    # - OpenAI
    # - Groq
    # - Ollama
    # - Together AI
    # - DeepSeek
    # - Fireworks
    # - Mistral

    return OpenAICompatible(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url
    )