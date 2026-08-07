from google import genai
import time


class GeminiProvider:


    def __init__(
            self,
            model,
            api_key
    ):

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model



    def generate(
            self,
            prompt,
            temperature=0.2,
            retries=3
    ):


        for attempt in range(retries):

            try:

                response = self.client.models.generate_content(

                    model=self.model,

                    contents=prompt

                )

                return response.text


            except Exception as e:

                if "503" in str(e):

                    wait = 2 ** attempt

                    print(
                        f"Gemini busy. Retrying after {wait}s..."
                    )

                    time.sleep(wait)

                else:
                    raise e



        raise Exception(
            "Gemini unavailable after retries"
        )