"""
Universal OpenAI-Compatible LLM Adapter

Supports:

- OpenAI
- Groq
- Ollama
- Together AI
- DeepSeek
- Fireworks
- OpenRouter
- Novita
- Mistral
- Any OpenAI-Compatible Endpoint
"""

from openai import OpenAI


class OpenAICompatible:

    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        base_url: str = None
    ):

        self.provider = provider
        self.model = model

        if provider != "ollama" and not api_key:
            raise ValueError(
                f"API key missing for provider: {provider}"
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> str:
        """
        Universal generate function for every
        OpenAI-compatible provider.
        """

        try:

            response = self.client.chat.completions.create(

                model=self.model,

                temperature=temperature,

                messages=[

                    {
                        "role": "system",
                        "content": system_prompt
                    },

                    {
                        "role": "user",
                        "content": user_prompt
                    }

                ]

            )

            return response.choices[0].message.content

        except Exception as e:

            raise RuntimeError(

                f"{self.provider} generation failed:\n{str(e)}"

            )