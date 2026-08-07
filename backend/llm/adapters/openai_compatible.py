"""
OpenAI Compatible LLM Adapter

Supports any provider exposing OpenAI-compatible
/chat/completions endpoint.

Examples:
- OpenAI
- Groq
- DeepSeek
- OpenRouter
- Together AI
- Fireworks
- Mistral API
- Ollama local models
- Any custom OpenAI-compatible endpoint
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


        if not api_key:
            raise ValueError(
                f"API key missing for provider: {provider}"
            )


        self.client = OpenAI(

            api_key=api_key,

            # Required for providers other than OpenAI
            base_url=base_url
        )


    def generate(
            self,
            prompt: str,
            temperature: float = 0.2
    ) -> str:
        """
        Generate response from any OpenAI-compatible provider.
        """


        try:

            response = self.client.chat.completions.create(

                model=self.model,

                temperature=temperature,

                messages=[

                    {
                        "role": "system",
                        "content":
                        "You are a helpful AI assistant."
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }

                ]
            )


            return response.choices[0].message.content



        except Exception as e:

            raise RuntimeError(

                f"{self.provider} generation failed: {str(e)}"

            )