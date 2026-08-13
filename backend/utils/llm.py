"""Delegator module for LLM utilities.

This module attempts to import the equivalent helpers from
`gpt_researcher.utils.llm` (the canonical implementation). If not
available, it provides minimal fallbacks that raise informative errors.
"""
try:
    from gpt_researcher.utils.llm import *  # noqa: F401,F403
except Exception:  # pragma: no cover - fallback
    def __getattr__(name):
        raise ImportError("backend.utils.llm is unavailable; ensure gpt_researcher is installed and importable")
