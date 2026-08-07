from google import genai
import time


class GeminiProvider:

    def __init__(
        self,
        model,
        api_key
    ):

        if not api_key:
            raise ValueError("Gemini API key is required.")

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

    def generate(
        self,
        system_prompt,
        user_prompt,
        temperature=0.2,
        retries=3
    ):

        prompt = f"""
{system_prompt}

----------------------------------------

{user_prompt}
"""

        for attempt in range(retries):

            try:

                response = self.client.models.generate_content(

                    model=self.model,

                    contents=prompt,

                    config={
                        "temperature": temperature
                    }

                )

                return response.text

            except Exception as e:

                if "503" in str(e):

                    wait = 2 ** attempt

                    print(
                        f"Gemini busy. Retrying in {wait} seconds..."
                    )

                    time.sleep(wait)

                else:
                    raise e

        raise Exception(
            "Gemini unavailable after retries."
        )