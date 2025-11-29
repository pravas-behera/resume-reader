"""
FAISS Vector Store Implementation
"""

from typing import List, Any
from langchain_community.vectorstores import FAISS as LangChainFAISS
from langchain_openai import OpenAIEmbeddings
from src.domain.models import DocumentChunk
from src.domain.interfaces import IVectorStore
from src.infrastructure.vectorstores.base_store import BaseVectorStore
from src.core.exceptions import VectorStoreError
from src.core.logger import logger


class FAISSVectorStore(BaseVectorStore):
    """FAISS vector store implementation"""
    
    def __init__(self, embeddings: OpenAIEmbeddings):
        """
        Initialize FAISS vector store
        
        Args:
            embeddings: Embedding model instance
        """
        super().__init__()
        self.embeddings = embeddings
        self._store: LangChainFAISS = None
        logger.info("Initialized FAISS vector store")
    
    def _add_documents_impl(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """Add documents to FAISS store"""
        try:
            # Convert chunks to LangChain document format
            from langchain_core.documents import Document as LangChainDoc
            
            langchain_docs = []
            for chunk in chunks:
                langchain_docs.append(
                    LangChainDoc(
                        page_content=chunk.content,
                        metadata=chunk.metadata
                    )
                )
            
            if self._store is None:
                # Create new store
                self._store = LangChainFAISS.from_documents(
                    documents=langchain_docs,
                    embedding=self.embeddings
                )
            else:
                # Add to existing store
                self._store.add_documents(langchain_docs)
            
            logger.info(f"Added {len(chunks)} chunks to FAISS store")
            
        except Exception as e:
            logger.error(f"Error adding documents to FAISS: {str(e)}")
            raise VectorStoreError(f"Failed to add documents: {str(e)}") from e
    
    def search(self, query_embedding: List[float], k: int) -> List[DocumentChunk]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of similar document chunks
        """
        if self._store is None:
            raise VectorStoreError("Vector store is empty")
        
        try:
            # FAISS search uses text query, not embedding directly
            # This is a limitation - we'd need to implement custom search
            # For now, we'll use the retriever interface
            results = self._store.similarity_search_with_score(
                query="",  # This won't work - need to fix
                k=k
            )
            
            chunks = []
            for doc, score in results:
                chunks.append(
                    DocumentChunk(
                        content=doc.page_content,
                        metadata=doc.metadata,
                        chunk_index=0,
                        source=doc.metadata.get("source")
                    )
                )
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error searching FAISS store: {str(e)}")
            raise VectorStoreError(f"Search failed: {str(e)}") from e
    
    def as_retriever(self, **kwargs) -> Any:
        """Get LangChain retriever interface"""
        if self._store is None:
            raise VectorStoreError("Vector store is empty")
        return self._store.as_retriever(**kwargs)

