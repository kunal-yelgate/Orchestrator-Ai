import time

from google import genai


class GeminiProvider:
    def __init__(self, model, api_key):
        if not api_key:
            raise ValueError("Gemini API key is required.")

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(
        self,
        system_prompt,
        user_prompt,
        temperature=0.2,
        retries=3,
    ):
        prompt = f"""
{system_prompt}

---

{user_prompt}
"""

        for attempt in range(retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "temperature": temperature,
                    },
                )

                usage = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                }

                if hasattr(response, "usage_metadata"):
                    metadata = response.usage_metadata

                    usage["prompt_tokens"] = getattr(
                        metadata,
                        "prompt_token_count",
                        0,
                    )

                    usage["completion_tokens"] = getattr(
                        metadata,
                        "candidates_token_count",
                        0,
                    )

                    usage["total_tokens"] = getattr(
                        metadata,
                        "total_token_count",
                        usage["prompt_tokens"] + usage["completion_tokens"],
                    )

                return {
                    "content": response.text,
                    "usage": usage,
                }

            except Exception as error:
                if "503" in str(error) and attempt < retries - 1:
                    wait = 2**attempt
                    print(f"Gemini busy. Retrying in {wait} seconds...")
                    time.sleep(wait)
                else:
                    raise

        raise RuntimeError("Gemini unavailable after retries.")