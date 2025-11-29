"""
Text Splitter Utility
"""

from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.domain.models import Document, DocumentChunk
from src.domain.interfaces import ITextSplitter
from src.core.logger import logger


class RecursiveTextSplitter(ITextSplitter):
    """Recursive character text splitter implementation"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize text splitter
        
        Args:
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        logger.info(f"Initialized text splitter: chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def split_documents(self, documents: List[Document]) -> List[DocumentChunk]:
        """
        Split documents into chunks
        
        Args:
            documents: List of documents to split
            
        Returns:
            List of document chunks
        """
        # Convert to LangChain format
        from langchain_core.documents import Document as LangChainDoc
        
        langchain_docs = []
        for doc in documents:
            langchain_docs.append(
                LangChainDoc(
                    page_content=doc.content,
                    metadata=doc.metadata
                )
            )
        
        # Split documents
        split_docs = self.splitter.split_documents(langchain_docs)
        
        # Convert back to domain models
        chunks = []
        for i, split_doc in enumerate(split_docs):
            chunks.append(
                DocumentChunk(
                    content=split_doc.page_content,
                    metadata=split_doc.metadata,
                    chunk_index=i,
                    source=split_doc.metadata.get("source")
                )
            )
        
        logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks

