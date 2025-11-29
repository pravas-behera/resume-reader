"""
Custom Exceptions
Application-specific exception classes
"""


class DocumentQAAException(Exception):
    """Base exception for Document Q&A system"""
    pass


class ConfigurationError(DocumentQAAException):
    """Raised when there's a configuration error"""
    pass


class DocumentProcessingError(DocumentQAAException):
    """Raised when document processing fails"""
    pass


class DocumentLoadError(DocumentQAAException):
    """Raised when document loading fails"""
    pass


class VectorStoreError(DocumentQAAException):
    """Raised when vector store operations fail"""
    pass


class QAChainError(DocumentQAAException):
    """Raised when QA chain operations fail"""
    pass


class APIKeyError(DocumentQAAException):
    """Raised when API key is missing or invalid"""
    pass

