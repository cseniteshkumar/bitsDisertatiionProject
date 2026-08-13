"""Memory package for backend.

Provide backwards-compatible exports expected by code that used
``gpt_researcher.memory``. The canonical implementation lives in
``backend/memory/embeddings.py`` which defines `Memory`.
"""
try:
	from .embeddings import Memory  # type: ignore
	__all__ = ["Memory"]
except Exception:
	# best-effort fallback — import may fail during partial merges
	__all__ = []

