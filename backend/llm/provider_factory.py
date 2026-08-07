"""
Universal LLM Provider Factory

User can provide:
- Any provider name
- Any model name
- Any API key
- Optional base_url

No provider restriction.
"""

from llm.adapters.openai_compatible import OpenAICompatible
from llm.adapters.gemini import GeminiProvider
from llm.adapters.anthropic import AnthropicProvider



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


    # Native Anthropic API
    if provider in [
        "anthropic",
        "claude"
    ]:

        return AnthropicProvider(
            model=model,
            api_key=api_key
        )


    # Everything else
    # Groq, DeepSeek, Together, Fireworks,
    # Mistral, Ollama, etc.

    return OpenAICompatible(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url
    )