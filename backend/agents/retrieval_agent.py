
"""
retrieval_agent.py

Single-file Retrieval Agent (V1)
Supports loading text from:
- PDF (.pdf)
- Text (.txt, .md)
- CSV (.csv)
- SQLite database files (.db, .sqlite, .sqlite3)
- Any web URL (HTML pages, plain text, JSON, etc.)
- GitHub links — a single file ('blob') URL, or a repo root URL
  (walks the default branch and pulls in text/code files)

Requirements:
pip install pypdf openai requests

Set:
GROQ_API_KEY=<your key>
GITHUB_TOKEN=<optional, raises GitHub API rate limits>
"""

import os
import csv
import sqlite3
from pathlib import Path
from difflib import SequenceMatcher
from html.parser import HTMLParser
from urllib.parse import urlparse

import json
from datetime import datetime
import hashlib

from openai import OpenAI
from pypdf import PdfReader

try:
    import requests
except ImportError:
    requests = None


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

# Local file types load_text() knows how to open.
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".csv", ".db", ".sqlite", ".sqlite3"}

# File extensions worth pulling out of a GitHub repo (skip binaries/assets).
GITHUB_TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
    ".go", ".rs", ".rb", ".php", ".cs", ".sql", ".sh", ".yaml", ".yml",
    ".json", ".txt", ".md", ".rst", ".toml", ".ini", ".cfg",
}

MAX_GITHUB_FILES = 25          # cap how many repo files we pull in
MAX_DB_ROWS_PER_TABLE = 500    # cap rows dumped per SQLite table
MAX_REMOTE_BYTES = 2_000_000   # 2 MB safety cap per fetched URL/file


# ==========================================================
# Source-type detection
# ==========================================================

def is_url(source: str) -> bool:
    return source.lower().startswith(("http://", "https://"))


def is_github_url(source: str) -> bool:
    return is_url(source) and "github.com" in urlparse(source).netloc.lower()


def _require_requests():
    if requests is None:
        raise RuntimeError(
            "The 'requests' package is required for URL/GitHub retrieval. "
            "Install it with: pip install requests"
        )


def _github_headers():
    token = os.getenv("GITHUB_TOKEN")
    return {"Authorization": f"token {token}"} if token else {}


def _fetch(url: str, headers=None):
    _require_requests()
    resp = requests.get(url, headers=headers or {}, timeout=20)
    resp.raise_for_status()
    return resp


class _HTMLTextExtractor(HTMLParser):
    """Minimal HTML-to-text stripper — avoids adding a bs4 dependency."""

    _SKIP_TAGS = {"script", "style", "noscript"}

    def __init__(self):
        super().__init__()
        self._skip = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP_TAGS:
            self._skip = True

    def handle_endtag(self, tag):
        if tag in self._SKIP_TAGS:
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self.parts.append(text)

    def get_text(self) -> str:
        return "\n".join(self.parts)


def html_to_text(html: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(html)
    return parser.get_text()


def load_url(url: str) -> str:
    """
    Fetches a web page and returns its visible text. HTML is stripped of
    tags/scripts/styles; anything else (plain text, JSON, etc.) is
    returned as-is.
    """

    resp = _fetch(url)

    content_type = resp.headers.get("Content-Type", "").lower()
    raw = resp.content[:MAX_REMOTE_BYTES]

    looks_like_html = "html" in content_type or raw.lstrip()[:15].lower().startswith(b"<!doctype html") or raw.lstrip()[:5].lower() == b"<html"

    decoded = raw.decode(resp.encoding or "utf-8", errors="ignore")

    return html_to_text(decoded) if looks_like_html else decoded


def _github_blob_to_raw(url: str):
    """
    Converts a GitHub 'blob' file URL into its raw.githubusercontent.com
    equivalent. Returns None if the URL isn't a single-file blob link.

    https://github.com/{owner}/{repo}/blob/{branch}/{path}
      -> https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
    """

    parts = urlparse(url).path.strip("/").split("/")

    if len(parts) < 5 or parts[2] != "blob":
        return None

    owner, repo, _, branch, *path_parts = parts

    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{'/'.join(path_parts)}"


def load_github(url: str) -> str:
    """
    Supports two kinds of GitHub links:

    1. A single file ('blob') URL — fetched directly as raw text.
    2. A repo root URL (https://github.com/{owner}/{repo}) — walks the
       default branch via the GitHub API and concatenates the text/code
       files it finds, capped at MAX_GITHUB_FILES so this stays bounded.
    """

    raw_url = _github_blob_to_raw(url)

    if raw_url:
        resp = _fetch(raw_url, headers=_github_headers())
        return resp.content[:MAX_REMOTE_BYTES].decode("utf-8", errors="ignore")

    parts = urlparse(url).path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError(f"Unrecognized GitHub URL: {url}")

    owner, repo = parts[0], parts[1]

    tree_resp = _fetch(
        f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1",
        headers=_github_headers(),
    )

    tree = tree_resp.json().get("tree", [])

    text_files = [
        item for item in tree
        if item.get("type") == "blob"
        and Path(item["path"]).suffix.lower() in GITHUB_TEXT_EXTENSIONS
    ][:MAX_GITHUB_FILES]

    combined = []

    for item in text_files:
        raw = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{item['path']}"
        try:
            file_resp = _fetch(raw, headers=_github_headers())
            content = file_resp.content[:MAX_REMOTE_BYTES].decode("utf-8", errors="ignore")
            combined.append(f"### {item['path']} ###\n{content}")
        except Exception:
            continue

    if not combined:
        raise ValueError(
            f"No readable text/code files found in {owner}/{repo} "
            f"(scanned {len(tree)} entries)."
        )

    return "\n\n".join(combined)


def load_csv(path: str) -> str:
    """
    Converts CSV rows into readable 'field: value' sentences so the
    similarity scorer can match on column values instead of raw commas.
    """

    lines = []

    with open(path, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader):
            sentence = " | ".join(f"{k}: {v}" for k, v in row.items() if k)
            lines.append(f"Row {i + 1}: {sentence}")

    return "\n".join(lines)


def load_sqlite(path: str) -> str:
    """
    Dumps every table in a SQLite database file into readable
    'table row: col=val' sentences (capped per table so large databases
    don't blow up the retrieval context).
    """

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row

    lines = []

    try:
        tables = [
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        ]

        for table in tables:
            cursor = conn.execute(f"SELECT * FROM {table} LIMIT {MAX_DB_ROWS_PER_TABLE}")

            for row in cursor:
                sentence = " | ".join(f"{key}: {row[key]}" for key in row.keys())
                lines.append(f"{table} row: {sentence}")

    finally:
        conn.close()

    return "\n".join(lines)


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
    """
    Loads and returns plain text from any supported source:
    - Local files: .pdf, .txt, .md, .csv, .db/.sqlite/.sqlite3
    - Any web URL (HTML pages, plain text, JSON, etc.)
    - GitHub file ('blob') or repo root links

    This is the single entry point gather_context() (and the standalone
    CLI) calls — everything downstream (chunk_text, retrieve, ask_llm)
    doesn't need to know or care what kind of source it came from.
    """

    if is_github_url(path):
        return load_github(path)

    if is_url(path):
        return load_url(path)

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

    if ext == ".csv":
        return load_csv(path)

    if ext in [".db", ".sqlite", ".sqlite3"]:
        return load_sqlite(path)

    raise ValueError(
        "Unsupported source. Supported: PDF, TXT, MD, CSV, SQLite DB "
        "files, web URLs, and GitHub file/repo links."
    )


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
            if is_url(doc_path):
                # URL or GitHub link — load_text() fetches it directly;
                # no local extension/existence check applies.
                text = load_text(doc_path)

            else:
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

    path = input(
        "\nSource (PDF/TXT/MD/CSV/SQLite path, web URL, or GitHub link):\n> "
    )

    if not is_url(path) and not os.path.exists(path):
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
