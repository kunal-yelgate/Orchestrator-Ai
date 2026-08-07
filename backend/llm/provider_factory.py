"""
Universal Provider Factory

Supports:

Native Providers
----------------
- Gemini

OpenAI-Compatible Providers
---------------------------
- OpenAI
- Groq
- Ollama
- Together AI
- OpenRouter
- DeepSeek
- Fireworks
- Mistral
- HuggingFace Router
- SambaNova
- NVIDIA NIM
- Cerebras
- xAI
- Any custom OpenAI-compatible endpoint
"""

from llm.adapters.gemini import GeminiProvider
from llm.adapters.openai_compatible import OpenAICompatible


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


def get_provider(
    provider: str,
    model: str,
    api_key: str = None,
    base_url: str = None
):
    """
    Returns the correct LLM adapter.

    Parameters
    ----------
    provider : str
    model : str
    api_key : str
    base_url : Optional[str]

    Examples
    --------
    get_provider("gemini", ...)
    get_provider("groq", ...)
    get_provider("ollama", ...)
    get_provider("openai", ...)
    """

    if not provider:
        raise ValueError("Provider cannot be empty.")

    provider = provider.lower().strip()

    # -----------------------------
    # Native Provider
    # -----------------------------

    if provider == "gemini":

        return GeminiProvider(
            model=model,
            api_key=api_key
        )

    # -----------------------------
    # OpenAI Compatible
    # -----------------------------

    if base_url is None:

        base_url = DEFAULT_BASE_URLS.get(provider)

    # Ollama generally doesn't require an API key
    if provider == "ollama" and not api_key:
        api_key = "ollama"

    return OpenAICompatible(

        provider=provider,

        model=model,

        api_key=api_key,

        base_url=base_url
    )