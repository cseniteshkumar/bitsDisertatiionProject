"""Compatibility package for legacy `gpt_researcher` imports.

The implementation now lives under `backend/`. This package exposes the
same subpackage search path so older import sites keep working without
importing `backend` during package initialization.
"""

from __future__ import annotations

import os
from importlib import import_module

_backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))

# Make submodule imports like `gpt_researcher.utils.llm` resolve to backend/
# without duplicating code.
__path__ = [os.path.dirname(__file__), _backend_path]
__all__ = ["GPTResearcher"]


def __getattr__(name: str):
	if name == "GPTResearcher":
		return import_module("backend.agent").GPTResearcher
	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")