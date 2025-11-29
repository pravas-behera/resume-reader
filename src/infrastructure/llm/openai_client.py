"""
OpenAI LLM Client Implementation
"""

from langchain_openai import ChatOpenAI
from src.domain.interfaces import ILLMService
from src.core.exceptions import QAChainError
from src.core.logger import logger


class OpenAIClient(ILLMService):
    """OpenAI LLM service implementation"""
    
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key
            model_name: Model name to use
            temperature: Temperature for generation
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            api_key=api_key
        )
        logger.info(f"Initialized OpenAI client with model: {model_name}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using OpenAI
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise QAChainError(f"Failed to generate text: {str(e)}") from e

