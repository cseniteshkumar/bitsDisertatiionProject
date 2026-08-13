"""Compatibility shim: expose `backend` as `gpt_researcher`.

This lightweight package re-exports the `backend` implementation so that
remaining imports of `gpt_researcher` in the codebase continue to work
after consolidation. It delegates package lookups to the `backend` package
by adopting its `__path__` and re-exporting top-level names.
"""
import importlib
import os

# Import the canonical backend package
_bk = importlib.import_module("backend")

# Make package imports resolve into the backend package directory
try:
    __path__ = list(_bk.__path__)
except Exception:
    # fallback: single-file backend may not have __path__
    __path__ = []

# Re-export symbols from backend for convenience
try:
    from backend import *  # noqa: F401,F403
    __all__ = getattr(_bk, "__all__", [])
except Exception:
    __all__ = []
