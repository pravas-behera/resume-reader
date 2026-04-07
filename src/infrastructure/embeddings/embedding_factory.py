"""
Embedding Service Factory
"""

from src.core.config import AppConfig
from src.core.exceptions import APIKeyError, DocumentProcessingError


class EmbeddingFactory:
    """Factory for creating configured embedding services"""

    @staticmethod
    def create(config: AppConfig):
        provider = config.embedding_config.provider.lower()

        if provider == "openai":
            if not config.openai_api_key:
                raise APIKeyError("OpenAI API key is required for OpenAI embedding provider")
            from src.infrastructure.embeddings.openai_embeddings import OpenAIEmbeddingService

            return OpenAIEmbeddingService(
                api_key=config.openai_api_key,
                model=config.embedding_config.model
            )

        if provider == "ollama":
            from src.infrastructure.embeddings.ollama_embeddings import OllamaEmbeddingService

            return OllamaEmbeddingService(
                model=config.embedding_config.model or config.ollama_config.embedding_model,
                base_url=config.ollama_config.base_url
            )

        raise DocumentProcessingError(f"Unsupported embedding provider: {provider}")
