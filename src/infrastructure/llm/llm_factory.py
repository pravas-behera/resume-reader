"""
LLM Client Factory
"""

from src.core.config import AppConfig
from src.core.exceptions import QAChainError


class LLMFactory:
    """Factory for creating configured LLM clients"""

    @staticmethod
    def create(config: AppConfig):
        provider = config.model_config.provider.lower()

        if provider == "openai":
            if not config.openai_api_key:
                raise QAChainError("OpenAI API key is required for OpenAI LLM provider")
            from src.infrastructure.llm.openai_client import OpenAIClient

            return OpenAIClient(
                api_key=config.openai_api_key,
                model_name=config.model_config.name,
                temperature=config.model_config.temperature
            )

        if provider == "ollama":
            from src.infrastructure.llm.ollama_client import OllamaClient

            return OllamaClient(
                model_name=config.model_config.name or config.ollama_config.llm_model,
                base_url=config.ollama_config.base_url,
                temperature=config.model_config.temperature
            )

        raise QAChainError(f"Unsupported LLM provider: {provider}")
