"""
Universal LLM Provider Factory

Supports:
- Gemini native API
- OpenAI-compatible APIs:
    - Groq
    - OpenAI
    - DeepSeek
    - Together
    - Fireworks
    - Novita
    - OpenRouter
    - etc.
- Local models through OpenAI-compatible endpoints
"""

from llm.adapters.openai_compatible import OpenAICompatible
from llm.adapters.gemini import GeminiProvider


def get_provider(
        provider: str,
        model: str,
        api_key: str = None,
        base_url: str = None
):

    provider = provider.lower().strip()


    # --------------------------------
    # Validate API key
    # --------------------------------

    if provider != "ollama" and not api_key:
        raise ValueError(
            f"API key required for provider: {provider}"
        )


    # --------------------------------
    # Gemini Native API
    # --------------------------------

    if provider == "gemini":

        return GeminiProvider(
            model=model,
            api_key=api_key
        )


    # --------------------------------
    # Groq / OpenAI Compatible
    # --------------------------------

    return OpenAICompatible(

        provider=provider,

        model=model,

        api_key=api_key,

        base_url=base_url
    )