"""Embedding provider management for GPT Researcher.

This module provides the Memory class that handles embedding generation
across multiple providers (OpenAI, Cohere, Google, Ollama, etc.).

Supported providers:
    - openai: OpenAI embeddings
    - azure_openai: Azure OpenAI embeddings
    - cohere: Cohere embeddings
    - google_vertexai: Google Vertex AI embeddings
    - google_genai: Google Generative AI embeddings
    - fireworks: Fireworks AI embeddings
    - ollama: Local Ollama embeddings
    - together: Together AI embeddings
    - mistralai: Mistral AI embeddings
    - huggingface: HuggingFace embeddings
    - nomic: Nomic embeddings
    - voyageai: Voyage AI embeddings
    - dashscope: DashScope embeddings
    - bedrock: AWS Bedrock embeddings
    - aimlapi: AIML API embeddings
    - custom: Custom OpenAI-compatible API
"""

import os
from typing import Any

OPENAI_EMBEDDING_MODEL = os.environ.get(
    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
)

_SUPPORTED_PROVIDERS = {"ollama"}


class Memory:
    """Manages embedding generation for document similarity and retrieval.

    This class provides a unified interface for generating embeddings
    using various providers. It lazily loads provider-specific dependencies
    only when needed.

    Attributes:
        _embeddings: The underlying LangChain embeddings instance.

    Example:
        ```python
        memory = Memory("openai", "text-embedding-3-small")
        embeddings = memory.get_embeddings()
        ```
    """

    def __init__(self, embedding_provider: str, model: str, **embedding_kwargs: Any):
        """Initialize the Memory with a specific embedding provider.

        Args:
            embedding_provider: The name of the embedding provider to use.
                Must be one of the supported providers (openai, cohere, etc.).
            model: The model name/ID to use for embeddings.
            **embedding_kwargs: Additional keyword arguments passed to the
                embedding provider's constructor.

        Raises:
            Exception: If the embedding provider is not supported.
        """
        _embeddings = None
        if embedding_provider != "ollama":
            raise ValueError(
                f"Unsupported embedding provider '{embedding_provider}'. This project uses Ollama only."
            )

        from langchain_ollama import OllamaEmbeddings

        base_url = embedding_kwargs.pop("base_url", None) or os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )
        _embeddings = OllamaEmbeddings(
            model=model,
            base_url=base_url,
            **embedding_kwargs,
        )

        self._embeddings = _embeddings

    def get_embeddings(self):
        """Get the configured embeddings instance.

        Returns:
            The LangChain embeddings instance configured for this Memory.
        """
        return self._embeddings
