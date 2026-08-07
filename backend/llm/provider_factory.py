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
<<<<<<< HEAD


# Default endpoints for OpenAI-compatible APIs
DEFAULT_BASE_URLS = {

    "openai":
        "https://api.openai.com/v1",

    "groq":
        "https://api.groq.com/openai/v1",

    "ollama":
        "http://localhost:11434/v1",

    "together":
        "https://api.together.xyz/v1",

    "deepseek":
        "https://api.deepseek.com/v1",

    "fireworks":
        "https://api.fireworks.ai/inference/v1",

    "openrouter":
        "https://openrouter.ai/api/v1",

    "mistral":
        "https://api.mistral.ai/v1",

    "huggingface":
        "https://router.huggingface.co/v1",

    "sambanova":
        "https://api.sambanova.ai/v1",

    "nvidia":
        "https://integrate.api.nvidia.com/v1",

    "cerebras":
        "https://api.cerebras.ai/v1",

    "xai":
        "https://api.x.ai/v1",
}
=======
>>>>>>> 7bf1b97b8889fe18300f2a7c84644d4371ac4eeb


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