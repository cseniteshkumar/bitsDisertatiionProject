"""
`backend` package shim that exposes the implementation from `gpt_researcher`.

This makes `import backend` and `import backend.submodule` resolve to the
corresponding modules inside `gpt_researcher`. It keeps the existing
`backend/` package on disk but directs package imports to the
`gpt_researcher` package path so `backend` becomes the canonical name.

Note: this is a lightweight, reversible approach to consolidation.
"""
import importlib
import os

# Import the real implementation package
_gr = importlib.import_module("gpt_researcher")

# Ensure local `backend/` submodules (e.g. backend.utils) remain importable
# while directing package imports to the `gpt_researcher` implementation.
# Prepend the local package directory and then append the gpt_researcher paths.
local_path = os.path.dirname(__file__)
__path__ = [local_path] + list(_gr.__path__)

# Re-export top-level names from gpt_researcher for convenience
try:
	from gpt_researcher import *  # noqa: F401,F403
	__all__ = getattr(_gr, "__all__", [])
except Exception:  # pragma: no cover - defensive fallback
	__all__ = []
