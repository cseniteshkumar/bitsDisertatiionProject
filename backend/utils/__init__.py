"""Backend utils package.

Re-export a small set of legacy helpers and expose delegator submodules.
Prefer importing submodules like `backend.utils.llm` or `backend.utils.enum`.
"""
from ._local import write_md_to_pdf, write_md_to_word, write_text_to_md  # type: ignore

__all__ = [
	"write_md_to_pdf",
	"write_md_to_word",
	"write_text_to_md",
]

# Import delegator submodules if available so that `from backend.utils import enum`
# and similar work as before.
try:
	from . import enum as enum  # noqa: F401
except Exception:
	pass
try:
	from . import llm as llm  # noqa: F401
except Exception:
	pass
try:
	from . import tools as tools  # noqa: F401
except Exception:
	pass
try:
	from . import logging_config as logging_config  # noqa: F401
except Exception:
	pass
