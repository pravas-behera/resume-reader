"""
Ollama LLM Client Implementation
"""

from langchain_community.llms import Ollama
from src.domain.interfaces import ILLMService
from src.core.exceptions import QAChainError
from src.core.logger import logger


class OllamaClient(ILLMService):
    """Local Ollama LLM service implementation"""

    def __init__(self, model_name: str = "phi3", base_url: str = "http://localhost:11434", temperature: float = 0.7):
        """
        Initialize Ollama client

        Args:
            model_name: Ollama model name to use
            base_url: Ollama server base URL
            temperature: Temperature for generation
        """
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.llm = Ollama(
            model=model_name,
            base_url=base_url,
            temperature=temperature
        )
        logger.info(f"Initialized Ollama client with model: {model_name}")

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using Ollama

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {str(e)}")
            raise QAChainError(f"Failed to generate text with Ollama: {str(e)}") from e
