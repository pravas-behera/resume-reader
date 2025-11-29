"""
PDF Document Loader
Implementation for PDF file loading
"""

from typing import List
from langchain_community.document_loaders import PyPDFLoader as LangChainPDFLoader
from src.domain.models import Document
from src.domain.interfaces import IDocumentLoader
from src.infrastructure.loaders.base_loader import BaseDocumentLoader
from src.core.exceptions import DocumentLoadError
from src.core.logger import logger


class PDFLoader(BaseDocumentLoader):
    """PDF document loader implementation"""
    
    def __init__(self):
        """Initialize PDF loader"""
        super().__init__(supported_extensions=[".pdf"])
    
    def load(self, file_path: str) -> List[Document]:
        """
        Load PDF documents
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of Document objects
            
        Raises:
            DocumentLoadError: If loading fails
        """
        try:
            logger.info(f"Loading PDF from: {file_path}")
            loader = LangChainPDFLoader(file_path)
            langchain_docs = loader.load()
            
            documents = []
            for i, doc in enumerate(langchain_docs):
                documents.append(
                    Document(
                        content=doc.page_content,
                        metadata={
                            **doc.metadata,
                            "page_number": doc.metadata.get("page", i + 1),
                            "source_file": file_path
                        },
                        source=file_path
                    )
                )
            
            logger.info(f"Successfully loaded {len(documents)} pages from PDF")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            raise DocumentLoadError(f"Failed to load PDF: {str(e)}") from e

