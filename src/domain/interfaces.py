"""
Domain Interfaces
Abstract base classes following Interface Segregation Principle
"""

from abc import ABC, abstractmethod
from typing import List, Any, Protocol
from src.domain.models import Document, DocumentChunk, Question, Answer


class IDocumentLoader(ABC):
    """Interface for document loaders (Interface Segregation Principle)"""
    
    @abstractmethod
    def load(self, file_path: str) -> List[Document]:
        """
        Load documents from a file path
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of Document objects
        """
        pass
    
    @abstractmethod
    def supports(self, file_extension: str) -> bool:
        """
        Check if loader supports a file type
        
        Args:
            file_extension: File extension (e.g., '.pdf')
            
        Returns:
            True if supported, False otherwise
        """
        pass


class ITextSplitter(ABC):
    """Interface for text splitters"""
    
    @abstractmethod
    def split_documents(self, documents: List[Document]) -> List[DocumentChunk]:
        """
        Split documents into chunks
        
        Args:
            documents: List of documents to split
            
        Returns:
            List of document chunks
        """
        pass


class IEmbeddingService(ABC):
    """Interface for embedding services (Dependency Inversion Principle)"""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        pass
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass


class IVectorStore(ABC):
    """Interface for vector stores (Dependency Inversion Principle)"""
    
    @abstractmethod
    def add_documents(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """
        Add documents to the vector store
        
        Args:
            chunks: Document chunks to add
            embeddings: Corresponding embeddings
        """
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], k: int) -> List[DocumentChunk]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of similar document chunks
        """
        pass


class ILLMService(ABC):
    """Interface for LLM services (Dependency Inversion Principle)"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the LLM
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        pass


class IDocumentService(ABC):
    """Interface for document processing service (Single Responsibility Principle)"""
    
    @abstractmethod
    def process_documents(self, files: List[Any]) -> IVectorStore:
        """
        Process uploaded documents and create vector store
        
        Args:
            files: List of uploaded file objects
            
        Returns:
            Vector store containing document embeddings
        """
        pass


class IQAService(ABC):
    """Interface for question-answering service (Single Responsibility Principle)"""
    
    @abstractmethod
    def ask_question(self, question: Question) -> Answer:
        """
        Answer a question based on documents
        
        Args:
            question: Question to answer
            
        Returns:
            Answer object
        """
        pass

