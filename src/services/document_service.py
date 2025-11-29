"""
Document Processing Service
Handles document loading, splitting, and vector store creation
Following Single Responsibility Principle
"""

from typing import List, Any
import tempfile
import os
from src.domain.interfaces import IDocumentService, IVectorStore
from src.domain.models import Document, DocumentChunk
from src.infrastructure.loaders.loader_factory import DocumentLoaderFactory
from src.infrastructure.embeddings.openai_embeddings import OpenAIEmbeddingService
from src.infrastructure.vectorstores.faiss_store import FAISSVectorStore
from src.utils.text_splitter import RecursiveTextSplitter
from src.core.config import AppConfig
from src.core.exceptions import DocumentProcessingError, APIKeyError
from src.core.logger import logger


class DocumentService(IDocumentService):
    """Service for processing documents (Single Responsibility Principle)"""
    
    def __init__(self, config: AppConfig):
        """
        Initialize document service
        
        Args:
            config: Application configuration
        """
        if not config.openai_api_key:
            raise APIKeyError("OpenAI API key is required")
        
        self.config = config
        self.embedding_service = OpenAIEmbeddingService(
            api_key=config.openai_api_key,
            model=config.embedding_config.model
        )
        self.text_splitter = RecursiveTextSplitter(
            chunk_size=config.embedding_config.chunk_size,
            chunk_overlap=config.embedding_config.chunk_overlap
        )
        logger.info("Initialized DocumentService")
    
    def process_documents(self, files: List[Any]) -> IVectorStore:
        """
        Process uploaded documents and create vector store
        
        Args:
            files: List of uploaded file objects
            
        Returns:
            Vector store containing document embeddings
            
        Raises:
            DocumentProcessingError: If processing fails
        """
        if not files:
            raise DocumentProcessingError("No files provided")
        
        try:
            logger.info(f"Processing {len(files)} file(s)")
            
            # Load all documents
            all_documents = []
            temp_files = []
            
            for uploaded_file in files:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name
                    temp_files.append(tmp_path)
                
                try:
                    # Get appropriate loader
                    loader = DocumentLoaderFactory.get_loader(tmp_path)
                    
                    # Load documents
                    documents = loader.load(tmp_path)
                    all_documents.extend(documents)
                    
                except Exception as e:
                    logger.error(f"Error loading file {uploaded_file.name}: {str(e)}")
                    raise DocumentProcessingError(f"Failed to load {uploaded_file.name}: {str(e)}") from e
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                        temp_files.remove(tmp_path)
            
            if not all_documents:
                raise DocumentProcessingError("No documents were loaded")
            
            logger.info(f"Loaded {len(all_documents)} document(s)")
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(all_documents)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Generate embeddings
            texts = [chunk.content for chunk in chunks]
            embeddings = self.embedding_service.embed_documents(texts)
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            # Create vector store
            vectorstore = FAISSVectorStore(
                embeddings=self.embedding_service.embeddings
            )
            vectorstore.add_documents(chunks, embeddings)
            
            logger.info("Successfully created vector store")
            return vectorstore
            
        except DocumentProcessingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing documents: {str(e)}")
            raise DocumentProcessingError(f"Failed to process documents: {str(e)}") from e

