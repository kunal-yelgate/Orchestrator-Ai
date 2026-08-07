from provider_factory import get_provider


def main():

    print("\n========== Universal LLM Test ==========\n")

    provider = input(
        "Provider (gemini/groq/openai/ollama/huggingface/openrouter/custom): "
    ).strip()

    model = input(
        "Model: "
    ).strip()

    api_key = input(
        "API Key (Press Enter if not required): "
    ).strip()

    if api_key == "":
        api_key = None

    base_url = input(
        "Base URL (Press Enter for default): "
    ).strip()

    if base_url == "":
        base_url = None

    prompt = input(
        "\nPrompt: "
    ).strip()

    print("\nInitializing provider...\n")

    llm = get_provider(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url
    )

    print("\nGenerating response...\n")

    response = llm.generate(prompt)

    print("=" * 80)
    print(response)
    print("=" * 80)


if __name__ == "__main__":
    main()