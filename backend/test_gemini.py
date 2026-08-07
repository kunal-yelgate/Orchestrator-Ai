from dotenv import load_dotenv
import os

from llm.provider_factory import get_provider

load_dotenv()


def test_provider():

    llm = get_provider(
        provider="gemini",
        model="gemini-2.0-flash-001",
        api_key=os.getenv("GEMINI_API_KEY")
    )

    response = llm.generate(
        "Explain AI agents in 3 lines"
    )

    print(response)


if __name__ == "__main__":
    test_provider()