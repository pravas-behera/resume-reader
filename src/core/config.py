"""
Configuration Management
Handles application configuration and environment variables
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ModelConfig:
    """Configuration for LLM model"""
    name: str
    temperature: float
    max_tokens: Optional[int] = None


@dataclass
class EmbeddingConfig:
    """Configuration for embeddings"""
    model: str = "text-embedding-ada-002"
    chunk_size: int = 1000
    chunk_overlap: int = 200


@dataclass
class RetrievalConfig:
    """Configuration for document retrieval"""
    k: int = 3  # Number of chunks to retrieve
    search_type: str = "similarity"


@dataclass
class AppConfig:
    """Main application configuration"""
    openai_api_key: str
    model_config: ModelConfig
    embedding_config: EmbeddingConfig
    retrieval_config: RetrievalConfig
    
    @classmethod
    def from_env(cls, api_key: Optional[str] = None) -> "AppConfig":
        """
        Create configuration from environment variables
        
        Args:
            api_key: Optional API key override
            
        Returns:
            AppConfig instance
        """
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OpenAI API key is required")
        
        return cls(
            openai_api_key=key,
            model_config=ModelConfig(
                name=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
                temperature=float(os.getenv("TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("MAX_TOKENS", "1000")) if os.getenv("MAX_TOKENS") else None
            ),
            embedding_config=EmbeddingConfig(
                model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002"),
                chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
                chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200"))
            ),
            retrieval_config=RetrievalConfig(
                k=int(os.getenv("RETRIEVAL_K", "3")),
                search_type=os.getenv("SEARCH_TYPE", "similarity")
            )
        )
    
    def update_model_config(self, name: str, temperature: float) -> None:
        """Update model configuration"""
        self.model_config.name = name
        self.model_config.temperature = temperature

