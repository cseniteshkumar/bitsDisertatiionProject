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

# If the implementation has been merged into `backend/` (instead of
# living in a separate `gpt_researcher` package), prefer exporting
# local symbols such as `GPTResearcher` from the local module tree.
try:
	# Import local implementation if present and export into package namespace
	from .agent import GPTResearcher  # type: ignore
	globals()["GPTResearcher"] = GPTResearcher
	if "GPTResearcher" not in __all__:
		__all__.append("GPTResearcher")
except Exception as e:
	# Log the import error to a file for diagnostics and attempt fallback
	try:
		with open(os.path.join(local_path, "_import_errors.log"), "a", encoding="utf-8") as fh:
			fh.write(f"Failed to import GPTResearcher from backend.agent: {e}\n")
	except Exception:
		pass
	# Fallback: try to load from original gpt_researcher package if present
	try:
		_mod = importlib.import_module("gpt_researcher.agent")
		GPTResearcher = getattr(_mod, "GPTResearcher")
		globals()["GPTResearcher"] = GPTResearcher
		if "GPTResearcher" not in __all__:
			__all__.append("GPTResearcher")
	except Exception:
		# Give up silently — smoke test will report missing symbol
		pass

# If GPTResearcher is still unavailable, provide a lazy proxy class so that
# importing `backend` doesn't fail; the real implementation will be imported
# when the class is instantiated.
if "GPTResearcher" not in globals():
	class GPTResearcher:
		"""Lazy proxy for the real GPTResearcher implementation.

		Instantiating this proxy will import the real class from
		`backend.agent` or `gpt_researcher.agent` and delegate all calls.
		"""

		def __init__(self, *args, **kwargs):
			# Import the real class lazily
			try:
				mod = importlib.import_module("backend.agent")
			except Exception:
				mod = importlib.import_module("gpt_researcher.agent")
			Real = getattr(mod, "GPTResearcher")
			# create the real instance and copy it onto self
			self.__dict__['_real'] = Real(*args, **kwargs)

		def __getattr__(self, name):
			return getattr(self.__dict__['_real'], name)

		def __setattr__(self, name, value):
			if name == '_real':
				super().__setattr__(name, value)
			else:
				setattr(self.__dict__['_real'], name, value)

		def __repr__(self):
			return f"<Lazy GPTResearcher proxy for {self.__dict__['_real'].__class__.__name__}>"

	# export the proxy
	globals()['GPTResearcher'] = GPTResearcher
	if "GPTResearcher" not in __all__:
		__all__.append("GPTResearcher")
