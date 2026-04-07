"""
Ollama Embedding Service Implementation
"""

from typing import List
from langchain_community.embeddings import OllamaEmbeddings
from src.domain.interfaces import IEmbeddingService
from src.core.exceptions import DocumentProcessingError
from src.core.logger import logger


class OllamaEmbeddingService(IEmbeddingService):
    """Local Ollama embedding service implementation"""

    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama embedding service

        Args:
            model: Ollama embedding model name
            base_url: Ollama server base URL
        """
        self.model = model
        self.base_url = base_url
        self.embeddings = OllamaEmbeddings(
            model=model,
            base_url=base_url
        )
        logger.info(f"Initialized Ollama embedding service with model: {model}")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a text

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Error embedding text with Ollama: {str(e)}")
            raise DocumentProcessingError(f"Failed to embed text with Ollama: {str(e)}") from e

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            results = self.embeddings.embed_documents(texts)
            logger.info(f"Generated Ollama embeddings for {len(texts)} texts")
            return results
        except Exception as e:
            logger.error(f"Error embedding documents with Ollama: {str(e)}")
            raise DocumentProcessingError(f"Failed to embed documents with Ollama: {str(e)}") from e
