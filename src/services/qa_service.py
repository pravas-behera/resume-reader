"""
Question-Answering Service
Handles question-answering using LLM and vector store
Following Single Responsibility Principle
"""

from datetime import datetime
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from src.domain.interfaces import IQAService, IVectorStore
from src.domain.models import Question, Answer, DocumentChunk
from src.infrastructure.llm.openai_client import OpenAIClient
from src.core.config import AppConfig
from src.core.exceptions import QAChainError
from src.core.logger import logger


class QAService(IQAService):
    """Service for question-answering (Single Responsibility Principle)"""
    
    def __init__(self, vectorstore: IVectorStore, config: AppConfig):
        """
        Initialize QA service
        
        Args:
            vectorstore: Vector store with document embeddings
            config: Application configuration
        """
        if not config.openai_api_key:
            raise QAChainError("OpenAI API key is required")
        
        self.vectorstore = vectorstore
        self.config = config
        
        # Initialize LLM
        self.llm_client = OpenAIClient(
            api_key=config.openai_api_key,
            model_name=config.model_config.name,
            temperature=config.model_config.temperature
        )
        
        # Create prompt template
        prompt_template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Use three sentences maximum and keep the answer concise.

        Context: {context}

        Question: {question}

        Answer:"""
        
        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval QA chain
        # Note: This requires the vectorstore to have as_retriever method
        if hasattr(vectorstore, 'as_retriever'):
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm_client.llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(
                    search_kwargs={"k": config.retrieval_config.k}
                ),
                chain_type_kwargs={"prompt": self.prompt},
                return_source_documents=True
            )
        else:
            raise QAChainError("Vector store does not support retriever interface")
        
        logger.info("Initialized QAService")
    
    def ask_question(self, question: Question) -> Answer:
        """
        Answer a question based on documents
        
        Args:
            question: Question to answer
            
        Returns:
            Answer object
            
        Raises:
            QAChainError: If answering fails
        """
        try:
            logger.info(f"Processing question: {question.text[:50]}...")
            
            # Invoke QA chain
            result = self.qa_chain.invoke({"query": question.text})
            
            # Extract source documents
            source_docs = []
            if "source_documents" in result:
                for i, doc in enumerate(result["source_documents"]):
                    source_docs.append(
                        DocumentChunk(
                            content=doc.page_content,
                            metadata=doc.metadata,
                            chunk_index=i,
                            source=doc.metadata.get("source")
                        )
                    )
            
            # Create answer
            answer = Answer(
                text=result["result"],
                question=question.text,
                source_documents=source_docs,
                timestamp=datetime.now()
            )
            
            logger.info("Successfully generated answer")
            return answer
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            raise QAChainError(f"Failed to answer question: {str(e)}") from e
    
    def ask_question_text(self, question_text: str) -> str:
        """
        Convenience method to ask a question with just text
        
        Args:
            question_text: Question text
            
        Returns:
            Answer text
        """
        question = Question(
            text=question_text,
            timestamp=datetime.now()
        )
        answer = self.ask_question(question)
        return answer.text

