import importlib
import os
from typing import Any, Optional

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    def load_dotenv() -> None:
        return None

# Load environment variables
load_dotenv()


class GeminiProvider:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")

        self.model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")
        self.client = None
        self.model = None

        self._initialize_client(api_key)

    def _initialize_client(self, api_key: str) -> None:
        """Initialize the Gemini client using the installed package API."""
        try:
            google_genai = importlib.import_module("google.genai")
            client_cls = getattr(google_genai, "Client", None)
            if callable(client_cls):
                self.client = client_cls(api_key=api_key)
                self.model = self.model_name
                return
        except Exception:
            pass

        try:
            genai = importlib.import_module("google.generativeai")
            configure = getattr(genai, "configure", None)
            if callable(configure):
                configure(api_key=api_key)

            model_class = getattr(genai, "GenerativeModel", None)
            if callable(model_class):
                self.model = model_class(self.model_name)
                return
        except Exception as exc:
            raise RuntimeError(f"Unable to initialize Gemini client: {exc}") from exc

        raise RuntimeError("No supported Gemini client API was found in the installed packages")

    def invoke(self, prompt: str) -> str:
        """Send a prompt to Gemini and return the generated text."""
        try:
            if self.client is not None:
                models = getattr(self.client, "models", None)
                if models is not None:
                    generate_content = getattr(models, "generate_content", None)
                    if callable(generate_content):
                        response = generate_content(model=self.model_name, contents=prompt)
                        text = getattr(response, "text", None)
                        if text:
                            return text
                return "No response generated."

            model_obj = self.model
            if isinstance(model_obj, str):
                return "Gemini model was not initialized correctly"

            if model_obj is not None:
                response = getattr(model_obj, "generate_content", None)
                if callable(response):
                    generated = response(prompt)
                    text = getattr(generated, "text", None)
                    if text:
                        return text
                return "No response generated."

            return "No response generated."

        except Exception as exc:
            return f"Gemini Error: {str(exc)}"