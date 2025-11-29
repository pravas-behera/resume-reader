"""
Document Loader Factory
Factory pattern for creating appropriate loaders
"""

from typing import List, Optional
from pathlib import Path
from src.domain.interfaces import IDocumentLoader
from src.infrastructure.loaders.pdf_loader import PDFLoader
from src.core.exceptions import DocumentLoadError
from src.core.logger import logger


class DocumentLoaderFactory:
    """Factory for creating document loaders"""
    
    _loaders: List[IDocumentLoader] = []
    _initialized = False
    
    @classmethod
    def _initialize_loaders(cls) -> None:
        """Initialize available loaders"""
        if not cls._initialized:
            cls._loaders = [
                PDFLoader(),
                # Add more loaders here as needed
            ]
            cls._initialized = True
            logger.info(f"Initialized {len(cls._loaders)} document loaders")
    
    @classmethod
    def get_loader(cls, file_path: str) -> IDocumentLoader:
        """
        Get appropriate loader for a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Appropriate document loader
            
        Raises:
            DocumentLoadError: If no loader supports the file type
        """
        cls._initialize_loaders()
        
        file_extension = Path(file_path).suffix
        
        for loader in cls._loaders:
            if loader.supports(file_extension):
                logger.info(f"Selected {loader.__class__.__name__} for {file_extension}")
                return loader
        
        raise DocumentLoadError(f"No loader available for file type: {file_extension}")
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of supported file extensions"""
        cls._initialize_loaders()
        extensions = []
        for loader in cls._loaders:
            if hasattr(loader, 'supported_extensions'):
                extensions.extend(loader.supported_extensions)
        return list(set(extensions))

