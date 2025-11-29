"""
Base Document Loader
Abstract base class for document loaders
"""

from abc import ABC, abstractmethod
from typing import List
from src.domain.interfaces import IDocumentLoader
from src.domain.models import Document
from src.core.logger import logger


class BaseDocumentLoader(IDocumentLoader, ABC):
    """Base class for document loaders"""
    
    def __init__(self, supported_extensions: List[str]):
        """
        Initialize base loader
        
        Args:
            supported_extensions: List of supported file extensions
        """
        self.supported_extensions = [ext.lower() for ext in supported_extensions]
        logger.info(f"Initialized {self.__class__.__name__} with support for: {self.supported_extensions}")
    
    def supports(self, file_extension: str) -> bool:
        """Check if loader supports a file type"""
        return file_extension.lower() in self.supported_extensions
    
    @abstractmethod
    def load(self, file_path: str) -> List[Document]:
        """Load documents - must be implemented by subclasses"""
        pass

