"""
Domain Models
Data models and DTOs for the application
"""

from dataclasses import dataclass
from typing import List, Optional, Any
from datetime import datetime


@dataclass
class Document:
    """Represents a processed document"""
    content: str
    metadata: dict
    source: Optional[str] = None
    
    def __post_init__(self):
        """Validate document after initialization"""
        if not self.content or not self.content.strip():
            raise ValueError("Document content cannot be empty")


@dataclass
class DocumentChunk:
    """Represents a chunk of a document"""
    content: str
    metadata: dict
    chunk_index: int
    source: Optional[str] = None


@dataclass
class Question:
    """Represents a user question"""
    text: str
    timestamp: datetime
    session_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate question after initialization"""
        if not self.text or not self.text.strip():
            raise ValueError("Question text cannot be empty")


@dataclass
class Answer:
    """Represents an answer to a question"""
    text: str
    question: str
    source_documents: List[DocumentChunk]
    timestamp: datetime
    confidence: Optional[float] = None


@dataclass
class ChatMessage:
    """Represents a chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Streamlit"""
        return {
            "role": self.role,
            "content": self.content
        }

