"""Delegator module for enums used across the project.

Prefer the canonical definitions from `gpt_researcher.utils.enum`.
"""
try:
    from gpt_researcher.utils.enum import *  # noqa: F401,F403
except Exception:  # pragma: no cover - fallback
    # Minimal enum fallbacks to avoid import errors during smoke tests.
    class ReportType:
        ResearchReport = "research_report"
        DetailedReport = "detailed_report"
        ResourceReport = "resource_report"
        OutlineReport = "outline_report"
        CustomReport = "custom_report"
        SubtopicReport = "subtopic_report"
        DeepResearch = "deep_research"

    class ReportSource:
        Web = "web"
        Local = "local"
        Hybrid = "hybrid"

    class Tone:
        Objective = "objective"
        Formal = "formal"
