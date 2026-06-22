"""
backend/services/_openai_client.py

Centralized OpenAI client + model name configuration.

WHY: previously every service file instantiated its own OpenAI() client
and hardcoded model names ("gpt-4o-mini" / "gpt-4o") in ~22 places.
Changing the model required editing 22 files, and a new HTTP client
was created on every call (no connection pooling).

This module:
  - Caches a single OpenAI client (lru_cache) — reused across all calls
  - Centralizes the two model names in env-overridable constants
  - Same model defaults as before — behavior is unchanged

To change a model project-wide, add to your .env:
    OPENAI_MODEL_CHEAP=gpt-4o-mini   (or whatever replaces it later)
    OPENAI_MODEL_SMART=gpt-4o
"""

import os
from functools import lru_cache
from openai import OpenAI


# Model names — exact same defaults as the hardcoded strings they replace
MODEL_CHEAP = os.getenv("OPENAI_MODEL_CHEAP", "gpt-4o-mini")
MODEL_SMART = os.getenv("OPENAI_MODEL_SMART", "gpt-4o")


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    """
    Returns a singleton OpenAI client. Cached, so the underlying HTTP
    connection pool is reused across all calls in the process.
    """
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to your .env file or "
            "your deployment environment variables."
        )
    return OpenAI(api_key=key)