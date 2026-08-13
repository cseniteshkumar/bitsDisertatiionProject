"""Compatibility bridge: top-level backend._local

This module re-exports helpers defined in `backend.utils._local` so that
legacy relative imports like ``from ._local import ...`` in
``backend/utils.py`` continue to work while the real implementations live
in ``backend/utils/_local.py`` (the package-local implementation).
"""
from .utils._local import write_md_to_pdf, write_md_to_word, write_text_to_md

__all__ = [
    "write_md_to_pdf",
    "write_md_to_word",
    "write_text_to_md",
]
