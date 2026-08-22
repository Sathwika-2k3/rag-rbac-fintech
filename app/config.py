import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _clean_env(name: str, default: str | None = None) -> str | None:
    # Secrets pasted into GitHub Actions (or .env) occasionally pick up a stray
    # trailing newline or whitespace, which HTTP clients reject outright as an
    # "illegal header value." Stripping here fixes that regardless of the source.
    value = os.getenv(name, default)
    return value.strip() if value else value


GROQ_API_KEY = _clean_env("GROQ_API_KEY")
LANGCHAIN_API_KEY = _clean_env("LANGCHAIN_API_KEY")
LANGCHAIN_TRACING_V2 = _clean_env("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_PROJECT = _clean_env("LANGCHAIN_PROJECT", "finsolve-rag-rbac")
QDRANT_URL = _clean_env("QDRANT_URL")
QDRANT_API_KEY = _clean_env("QDRANT_API_KEY")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "resources" / "data"
