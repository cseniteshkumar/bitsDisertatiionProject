"""
Compatibility shim: keep `backend.utils` importable while providing
subpackage modules under `backend.utils.*` that delegate to local
implementations or the `gpt_researcher.utils` package.

Prefer using submodules like `backend.utils.llm` or `backend.utils.enum`.
This file re-exports a small set of common helpers for backwards
compatibility (e.g. `write_md_to_pdf`).
"""
from ._local import write_md_to_pdf, write_md_to_word, write_text_to_md

__all__ = [
    "write_md_to_pdf",
    "write_md_to_word",
    "write_text_to_md",
]