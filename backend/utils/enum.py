"""Enums used across the backend package."""

from enum import Enum


class ReportType(Enum):
    ResearchReport = "research_report"
    ResourceReport = "resource_report"
    OutlineReport = "outline_report"
    CustomReport = "custom_report"
    DetailedReport = "detailed_report"
    SubtopicReport = "subtopic_report"
    DeepResearch = "deep"


class ReportSource(Enum):
    Web = "web"
    Local = "local"
    Azure = "azure"
    LangChainDocuments = "langchain_documents"
    LangChainVectorStore = "langchain_vectorstore"
    Static = "static"
    Hybrid = "hybrid"


class Tone(Enum):
    Objective = "Objective (impartial and unbiased presentation of facts and findings)"
    Formal = "Formal (adheres to academic standards with sophisticated language and structure)"
    Analytical = "Analytical"
    Persuasive = "Persuasive"
    Informative = "Informative"


class PromptFamily(Enum):
    Default = "default"
    Granite = "granite"
    Granite3 = "granite3"
    Granite31 = "granite3.1"
    Granite32 = "granite3.2"
    Granite33 = "granite3.3"


__all__ = ["ReportType", "ReportSource", "Tone", "PromptFamily"]
