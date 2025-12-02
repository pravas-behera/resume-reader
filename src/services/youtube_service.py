"""
YouTube Processing Service
Handles fetching transcript, splitting, embedding and creating a vectorstore
"""
from typing import Any, List
from src.core.config import AppConfig
from src.core.exceptions import DocumentProcessingError, APIKeyError
from src.infrastructure.embeddings.openai_embeddings import OpenAIEmbeddingService
from src.infrastructure.vectorstores.faiss_store import FAISSVectorStore
from src.utils.text_splitter import RecursiveTextSplitter
from src.utils.youtube_transcript import extract_video_id, fetch_transcript_text
from src.domain.models import Document, DocumentChunk
from src.core.logger import logger


class YouTubeService:
    """Service to process YouTube videos into a retrievable vector store"""

    def __init__(self, config: AppConfig):
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
        logger.info("Initialized YouTubeService")

    def process_video(self, url: str, existing_store: Any = None) -> Any:
        """Fetch transcript for the given YouTube URL and return an IVectorStore"""
        try:
            if not url or not url.strip():
                raise DocumentProcessingError("No YouTube URL provided")

            video_id = extract_video_id(url)
            transcript = fetch_transcript_text(video_id)

            if not transcript:
                raise DocumentProcessingError("Transcript is empty")

            # Create a single Document domain model
            doc = Document(content=transcript, metadata={"source": url})

            # Split into chunks
            chunks: List[DocumentChunk] = self.text_splitter.split_documents([doc])

            if not chunks:
                raise DocumentProcessingError("No chunks created from transcript")

            # Generate embeddings
            texts = [chunk.content for chunk in chunks]
            embeddings = self.embedding_service.embed_documents(texts)

            # Build vector store (append to existing store if provided)
            if existing_store is None:
                vectorstore = FAISSVectorStore(embeddings=self.embedding_service.embeddings)
                vectorstore.add_documents(chunks, embeddings)
            else:
                # Assume existing_store is a FAISSVectorStore instance
                existing_store.add_documents(chunks, embeddings)
                vectorstore = existing_store

            logger.info(f"Processed YouTube video {video_id} into vector store with {len(chunks)} chunks")
            return vectorstore

        except DocumentProcessingError:
            raise
        except Exception as e:
            logger.error(f"Error processing YouTube video: {str(e)}")
            raise DocumentProcessingError(f"Failed to process YouTube video: {str(e)}") from e

