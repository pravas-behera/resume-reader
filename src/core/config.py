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
    provider: str = "openai"
    max_tokens: Optional[int] = None


@dataclass
class EmbeddingConfig:
    """Configuration for embeddings"""
    model: str = "text-embedding-ada-002"
    provider: str = "openai"
    chunk_size: int = 1000
    chunk_overlap: int = 200


@dataclass
class OllamaConfig:
    """Configuration for local Ollama models"""
    base_url: str = "http://localhost:11434"
    llm_model: str = "phi3"
    embedding_model: str = "nomic-embed-text"


@dataclass
class RetrievalConfig:
    """Configuration for document retrieval"""
    k: int = 3  # Number of chunks to retrieve
    search_type: str = "similarity"


@dataclass
class AppConfig:
    """Main application configuration"""
    openai_api_key: Optional[str]
    model_config: ModelConfig
    embedding_config: EmbeddingConfig
    ollama_config: OllamaConfig
    retrieval_config: RetrievalConfig
    
    @classmethod
    def from_env(
        cls,
        api_key: Optional[str] = None,
        llm_provider: Optional[str] = None,
        embedding_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
        temperature: Optional[float] = None,
        ollama_base_url: Optional[str] = None,
        ollama_llm_model: Optional[str] = None,
        ollama_embedding_model: Optional[str] = None
    ) -> "AppConfig":
        """
        Create configuration from environment variables
        
        Args:
            api_key: Optional API key override
            
        Returns:
            AppConfig instance
        """
        llm_provider_value = (llm_provider or os.getenv("LLM_PROVIDER", "openai")).lower()
        embedding_provider_value = (embedding_provider or os.getenv("EMBEDDING_PROVIDER", "openai")).lower()
        key = api_key or os.getenv("OPENAI_API_KEY")
        ollama_base_url_value = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_llm_model_value = ollama_llm_model or os.getenv("OLLAMA_LLM_MODEL", "phi3")
        ollama_embedding_model_value = ollama_embedding_model or os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        if model_name:
            model_name_value = model_name
        elif llm_provider_value == "ollama":
            model_name_value = ollama_llm_model_value
        else:
            model_name_value = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

        if embedding_model:
            embedding_model_value = embedding_model
        elif embedding_provider_value == "ollama":
            embedding_model_value = ollama_embedding_model_value
        else:
            embedding_model_value = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        temperature_value = temperature if temperature is not None else float(os.getenv("TEMPERATURE", "0.7"))

        if (llm_provider_value == "openai" or embedding_provider_value == "openai") and not key:
            raise ValueError("OpenAI API key is required when using OpenAI models")
        
        return cls(
            openai_api_key=key,
            model_config=ModelConfig(
                name=model_name_value,
                temperature=temperature_value,
                provider=llm_provider_value,
                max_tokens=int(os.getenv("MAX_TOKENS", "1000")) if os.getenv("MAX_TOKENS") else None
            ),
            embedding_config=EmbeddingConfig(
                model=embedding_model_value,
                provider=embedding_provider_value,
                chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
                chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200"))
            ),
            ollama_config=OllamaConfig(
                base_url=ollama_base_url_value,
                llm_model=ollama_llm_model_value,
                embedding_model=ollama_embedding_model_value
            ),
            retrieval_config=RetrievalConfig(
                k=int(os.getenv("RETRIEVAL_K", "3")),
                search_type=os.getenv("SEARCH_TYPE", "similarity")
            )
        )
    
    def update_model_config(self, name: str, temperature: float, provider: Optional[str] = None) -> None:
        """Update model configuration"""
        self.model_config.name = name
        self.model_config.temperature = temperature
        if provider:
            self.model_config.provider = provider.lower()

    def update_embedding_config(self, model: str, provider: Optional[str] = None) -> None:
        """Update embedding configuration"""
        self.embedding_config.model = model
        if provider:
            self.embedding_config.provider = provider.lower()
