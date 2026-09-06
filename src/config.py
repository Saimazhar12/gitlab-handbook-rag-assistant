"""
config.py
---------
Central configuration for the pipeline. Reads settings from environment
variables (loaded from a .env file via python-dotenv) so no API keys or
machine-specific paths are hardcoded anywhere else in the project.

Supports either OpenAI or Google Gemini as the LLM/embeddings provider —
switch by setting LLM_PROVIDER in your .env file, without duplicating
the rest of the pipeline.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# --- Paths -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "gitlab_handbook"

# --- Chunking ------------------------------------------------------------
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# --- Retrieval -----------------------------------------------------------
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "4"))
# Chroma similarity scores here are distances (lower = more similar).
# Chunks with a distance above this are treated as "not relevant enough" --
# tune this if your embedding model reports scores on a different scale.
MAX_RELEVANT_DISTANCE = float(os.getenv("MAX_RELEVANT_DISTANCE", "0.8"))

# --- Provider selection ---------------------------------------------------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()  # "openai" or "gemini"


def _require_env(var_name: str, provider_label: str):
    value = os.getenv(var_name)
    if not value:
        print(f"[error] {var_name} is not set, but LLM_PROVIDER='{provider_label}'.")
        print(f"        Add {var_name}=... to your .env file (see .env.example).")
        sys.exit(1)
    return value


# Network calls to the LLM/embedding provider get this many seconds before
# giving up. Without a timeout, a slow or dropped connection leaves the
# request hanging indefinitely instead of failing with a message.
REQUEST_TIMEOUT_SECONDS = 30


def get_embedding_function():
    """Return a LangChain embeddings object for the configured provider."""
    if LLM_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings

        _require_env("OPENAI_API_KEY", "openai")
        return OpenAIEmbeddings(model="text-embedding-3-small", timeout=REQUEST_TIMEOUT_SECONDS)

    elif LLM_PROVIDER == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        _require_env("GOOGLE_API_KEY", "gemini")
        return GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            request_options={"timeout": REQUEST_TIMEOUT_SECONDS},
        )

    else:
        print(f"[error] Unknown LLM_PROVIDER='{LLM_PROVIDER}'. Use 'openai' or 'gemini'.")
        sys.exit(1)


def get_chat_model():
    """Return a LangChain chat model for the configured provider."""
    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        _require_env("OPENAI_API_KEY", "openai")
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.2, timeout=REQUEST_TIMEOUT_SECONDS)

    elif LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        _require_env("GOOGLE_API_KEY", "gemini")
        return ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite",
            temperature=0.2,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    else:
        print(f"[error] Unknown LLM_PROVIDER='{LLM_PROVIDER}'. Use 'openai' or 'gemini'.")
        sys.exit(1)
