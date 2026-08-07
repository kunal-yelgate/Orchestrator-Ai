
"""
retrieval_agent.py

Single-file Retrieval Agent (V1)
Supports:
- PDF (.pdf)
- Text (.txt, .md)

Requirements:
pip install pypdf openai

Set:
GROQ_API_KEY=<your key>
"""

import os
from pathlib import Path
from difflib import SequenceMatcher

from openai import OpenAI
from pypdf import PdfReader


# -----------------------
# Hardcoded Groq settings
# -----------------------
MODEL = "llama-3.3-70b-versatile"
BASE_URL = "https://api.groq.com/openai/v1"


def load_text(path: str) -> str:
    ext = Path(path).suffix.lower()

    if ext in [".txt", ".md"]:
        return Path(path).read_text(encoding="utf-8", errors="ignore")

    if ext == ".pdf":
        reader = PdfReader(path)
        text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
        return "\n".join(text)

    raise ValueError("Only PDF, TXT and MD are supported.")


def chunk_text(text, size=1000, overlap=200):
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        start += size - overlap

    return chunks


def score(query, chunk):
    return SequenceMatcher(
        None,
        query.lower(),
        chunk.lower()
    ).ratio()


def retrieve(query, chunks, k=3):
    ranked = sorted(
        chunks,
        key=lambda c: score(query, c),
        reverse=True
    )

    return ranked[:k]


def ask_llm(query, context):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("Set GROQ_API_KEY environment variable.")

    client = OpenAI(
        api_key=api_key,
        base_url=BASE_URL
    )

    prompt = f"""
You are a Retrieval Agent.

Answer ONLY from the supplied context.

If the answer is not present,
reply exactly:

I couldn't find that information in the supplied source.

Context:

{context}

Question:
{query}
"""

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful retrieval assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def main():

    print("=" * 60)
    print("Retrieval Agent")
    print("=" * 60)

    query = input("\nQuery:\n> ")

    path = input("\nPDF/TXT Path:\n> ")

    if not os.path.exists(path):
        print("\nFile not found.")
        return

    print("\nLoading document...")

    text = load_text(path)

    chunks = chunk_text(text)

    best = retrieve(query, chunks)

    context = "\n\n".join(best)

    print("\nGenerating answer...\n")

    answer = ask_llm(query, context)

    print("=" * 60)
    print(answer)
    print("=" * 60)


if __name__ == "__main__":
    main()
