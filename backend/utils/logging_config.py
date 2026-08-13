"""Logging helpers for backend research runs.

This module keeps the old `backend.utils.logging_config` import path alive
while delegating to the concrete implementation in `backend.server`.
"""

from backend.server.logging_config import (  # noqa: F401
    JSONResearchHandler,
    get_json_handler,
    get_research_logger,
    setup_research_logging,
)

__all__ = [
    "JSONResearchHandler",
    "get_json_handler",
    "get_research_logger",
    "setup_research_logging",
]
