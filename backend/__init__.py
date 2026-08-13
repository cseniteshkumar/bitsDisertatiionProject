"""Backend package root.

`GPTResearcher` is exposed lazily so importing `backend` does not eagerly
load the full agent graph during package initialization.
"""

from importlib import import_module

__all__ = ["GPTResearcher"]


def __getattr__(name: str):
	if name == "GPTResearcher":
		return import_module(".agent", __name__).GPTResearcher
	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
