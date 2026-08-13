"""Delegator module for tools utilities.

Delegates to `gpt_researcher.utils.tools` when available.
"""
try:
    from gpt_researcher.utils.tools import *  # noqa: F401,F403
except Exception:  # pragma: no cover - fallback
    def __getattr__(name):
        raise ImportError("backend.utils.tools is unavailable; ensure gpt_researcher is installed and importable")
