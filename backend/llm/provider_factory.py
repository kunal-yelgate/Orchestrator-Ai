"""
Universal LLM Provider Factory

Supports:
- Gemini (Native API)
- Groq
- OpenAI
- Ollama
- Together AI
- DeepSeek
- Fireworks
- OpenRouter
- Novita
- Mistral
- Any OpenAI-Compatible Provider
"""

from llm.adapters.gemini import GeminiProvider
from llm.adapters.openai_compatible import OpenAICompatible


def get_provider(
    provider: str,
    model: str,
    api_key: str = "",
    base_url: str = None,
):
    """
    Returns the appropriate LLM provider instance.
    """

    provider = provider.lower().strip()

    # ==========================================
    # Native Gemini
    # ==========================================
    if provider == "gemini":
        return GeminiProvider(
            model=model,
            api_key=api_key,
        )

    # ==========================================
    # OpenAI-Compatible Providers
    # ==========================================
    return OpenAICompatible(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
    )