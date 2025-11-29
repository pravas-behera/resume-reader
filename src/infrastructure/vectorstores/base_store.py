"""
Base Vector Store
Abstract base class for vector stores
"""

from abc import ABC, abstractmethod
from typing import List
from src.domain.interfaces import IVectorStore
from src.domain.models import DocumentChunk


class BaseVectorStore(IVectorStore, ABC):
    """Base class for vector store implementations"""
    
    def __init__(self):
        """Initialize base vector store"""
        self._document_count = 0
    
    @property
    def document_count(self) -> int:
        """Get number of documents in store"""
        return self._document_count
    
    def add_documents(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """
        Add documents to the vector store
        
        Args:
            chunks: Document chunks to add
            embeddings: Corresponding embeddings
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        self._add_documents_impl(chunks, embeddings)
        self._document_count += len(chunks)
    
    @abstractmethod
    def _add_documents_impl(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """Implementation-specific document addition"""
        pass

