"""
OpenAI Embedding Service Implementation
"""

from typing import List
from langchain_openai import OpenAIEmbeddings
from src.domain.interfaces import IEmbeddingService
from src.core.exceptions import DocumentProcessingError
from src.core.logger import logger


class OpenAIEmbeddingService(IEmbeddingService):
    """OpenAI embedding service implementation"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        """
        Initialize OpenAI embedding service
        
        Args:
            api_key: OpenAI API key
            model: Embedding model name
        """
        self.api_key = api_key
        self.model = model
        self.embeddings = OpenAIEmbeddings(
            model=model,
            openai_api_key=api_key
        )
        logger.info(f"Initialized OpenAI embedding service with model: {model}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            result = self.embeddings.embed_query(text)
            return result
        except Exception as e:
            logger.error(f"Error embedding text: {str(e)}")
            raise DocumentProcessingError(f"Failed to embed text: {str(e)}") from e
    
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
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return results
        except Exception as e:
            logger.error(f"Error embedding documents: {str(e)}")
            raise DocumentProcessingError(f"Failed to embed documents: {str(e)}") from e

