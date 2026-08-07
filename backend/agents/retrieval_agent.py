
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

import json
from datetime import datetime
import hashlib

from openai import OpenAI
from pypdf import PdfReader


# -----------------------
# Hardcoded Groq settings (used only by the standalone CLI in main())
# -----------------------
MODEL = "llama-3.3-70b-versatile"
BASE_URL = "https://api.groq.com/openai/v1"

# Sentinel the LLM is instructed to return verbatim when the supplied
# document context doesn't contain the answer. The Retriever node checks
# for this string to decide whether the Researcher needs to fall back to
# open-ended LLM research.
NOT_FOUND_MESSAGE = "I couldn't find that information in the supplied source."

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def build_retrieval_prompt(query: str, context: str) -> str:
    """
    Shared prompt template used both by the standalone CLI (ask_llm, via a
    hardcoded Groq client) and by the retriever_node (via the app's own
    llm provider). Keeping this in one place means both paths always agree
    on what "not found" looks like.
    """

    return f"""
You are a Retrieval Agent.

Answer ONLY from the supplied context.

If the answer is not present,
reply exactly:

{NOT_FOUND_MESSAGE}

Context:

{context}

Question:
{query}
"""


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

def save_chunks(chunks, source_path):
    """
    Save chunks to disk with metadata.
    """

    storage_dir = Path("chunk_store")
    storage_dir.mkdir(exist_ok=True)

    file_name = Path(source_path).stem

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    document_id = hashlib.md5(
        f"{file_name}_{timestamp}".encode()
    ).hexdigest()[:10]

    output_file = storage_dir / f"{file_name}_{timestamp}.json"

    data = {
        "document_id": document_id,
        "source_file": str(source_path),
        "document_name": file_name,
        "created_at": datetime.now().isoformat(),
        "total_chunks": len(chunks),
        "chunks": []
    }

    for i, chunk in enumerate(chunks):

        data["chunks"].append({
            "chunk_id": f"{document_id}_{i}",
            "chunk_number": i,
            "text": chunk
        })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return output_file

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

    prompt = build_retrieval_prompt(query, context)

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


def answer_from_context(llm, query: str, context: str) -> str:
    """
    Same behaviour as ask_llm(), but goes through the app's own LLM
    provider abstraction (state["llm"].generate) instead of a hardcoded
    Groq client, so the Retriever uses whichever provider the workflow
    was configured with.
    """

    prompt = build_retrieval_prompt(query, context)

    return llm.generate(
        system_prompt="You are a helpful retrieval assistant.",
        user_prompt=prompt,
        temperature=0.2,
    )


def gather_context(documents, query: str, k: int = 3):
    """
    Loads every document, chunks it, retrieves the best-matching chunks
    per document, and returns (context_text, chunks_used, documents_used,
    load_errors).
    """

    all_best_chunks = []
    documents_used = []
    load_errors = []

    for doc_path in documents:

        try:
            ext = Path(doc_path).suffix.lower()

            if ext not in SUPPORTED_EXTENSIONS:
                load_errors.append(
                    f"{doc_path}: unsupported file type '{ext}'"
                )
                continue

            if not os.path.exists(doc_path):
                load_errors.append(f"{doc_path}: file not found")
                continue

            text = load_text(doc_path)

            chunks = chunk_text(text)

            save_chunks(chunks, doc_path)

            best = retrieve(query, chunks, k=k)

            all_best_chunks.extend(best)

            documents_used.append(doc_path)

        except Exception as e:
            load_errors.append(f"{doc_path}: {e}")

    context = "\n\n".join(all_best_chunks)

    return context, all_best_chunks, documents_used, load_errors


# ==========================================================
# LangGraph / runner Node
# ==========================================================

def retriever_node(state):
    """
    Retriever node.

    Only performs retrieval when the Planner has flagged the workflow as
    needing it (state["needs_retrieval"]), which happens whenever the goal
    mentions a document/knowledge source, the goal explicitly asked for
    document retrieval, or documents were attached to the request
    (state["documents"]). Otherwise this is a cheap no-op so it can stay
    unconditionally wired into the graph/runner sequence.

    Uses the exact same load/chunk/score/retrieve pipeline as the
    standalone CLI agent above. If the retrieved context doesn't contain
    the answer (the LLM returns NOT_FOUND_MESSAGE), state["retrieval"]
    is marked found=False so the Researcher agents know to fall back to
    open-ended LLM research instead of trusting an empty/irrelevant
    context.
    """

    print("\n========== Retriever ==========\n")

    state["current_agent"] = "Retriever"

    state.setdefault("execution_trace", [])
    state["execution_trace"].append("Retriever")

    if state.get("error"):
        return state

    if not state.get("needs_retrieval"):

        state["retrieval"] = {
            "ran": False,
            "found": False,
            "answer": "",
            "documents_used": [],
            "chunks_used": [],
            "note": "Skipped — Planner determined no document retrieval was needed.",
        }

        print("Skipping retrieval — not required for this goal.")

        return state

    documents = state.get("documents") or []

    if not documents:

        state["retrieval"] = {
            "ran": False,
            "found": False,
            "answer": "",
            "documents_used": [],
            "chunks_used": [],
            "note": "Retrieval was needed but no documents were attached to the request.",
        }

        print("Retrieval needed but no documents were uploaded.")

        return state

    try:

        query = state["goal"]

        context, chunks_used, documents_used, load_errors = gather_context(
            documents,
            query,
        )

        if not context:

            state["retrieval"] = {
                "ran": True,
                "found": False,
                "answer": "",
                "documents_used": documents_used,
                "chunks_used": [],
                "note": "; ".join(load_errors) or "No usable content extracted from the supplied documents.",
            }

            print("Retriever found no usable content in the supplied documents.")

            return state

        answer = answer_from_context(state["llm"], query, context)

        found = NOT_FOUND_MESSAGE.lower() not in (answer or "").lower()

        state["retrieval"] = {
            "ran": True,
            "found": found,
            "answer": answer,
            "documents_used": documents_used,
            "chunks_used": chunks_used,
            "note": "; ".join(load_errors) if load_errors else "",
        }

        state["status"] = (
            "Retriever Completed"
            if found
            else "Retriever Completed — not found in documents, research will fall back to the LLM"
        )

        print("Retriever Finished Successfully" if found else "Retriever found no answer in documents — deferring to Researcher.")

    except Exception as e:

        # Retrieval failing should not kill the whole workflow — fall back
        # to letting the Researcher agents handle the task from scratch.
        state["retrieval"] = {
            "ran": True,
            "found": False,
            "answer": "",
            "documents_used": [],
            "chunks_used": [],
            "note": f"Retriever error: {e}",
        }

        print(f"Retriever Error (continuing without document context): {e}")

    return state


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
