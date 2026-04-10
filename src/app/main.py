"""
Main Streamlit Application
UI layer following separation of concerns
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from src.core.config import AppConfig
from src.services.document_service import DocumentService
from src.services.qa_service import QAService
from src.services.youtube_service import YouTubeService
from src.domain.models import ChatMessage
from src.core.exceptions import (
    DocumentProcessingError,
    QAChainError,
    APIKeyError,
    ConfigurationError
)
from src.core.logger import logger

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Document Q&A System",
    page_icon="📚",
    layout="wide"
)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if "document_service" not in st.session_state:
        st.session_state.document_service = None
    if "qa_service" not in st.session_state:
        st.session_state.qa_service = None
    if "youtube_service" not in st.session_state:
        st.session_state.youtube_service = None
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "qa_llm_signature" not in st.session_state:
        st.session_state.qa_llm_signature = None
    if "source_embedding_signature" not in st.session_state:
        st.session_state.source_embedding_signature = None
    if "processed_feature" not in st.session_state:
        st.session_state.processed_feature = None
    if "documents_loaded" not in st.session_state:
        st.session_state.documents_loaded = False
    if "config" not in st.session_state:
        st.session_state.config = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "feature" not in st.session_state:
        # Allows easy extension to add more feature sources later
        st.session_state.feature = "Documents"
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = (
            "Ollama" if os.getenv("LLM_PROVIDER", "openai").lower() == "ollama" else "OpenAI"
        )
    if "embedding_provider" not in st.session_state:
        st.session_state.embedding_provider = (
            "Ollama" if os.getenv("EMBEDDING_PROVIDER", "openai").lower() == "ollama" else "OpenAI"
        )


def normalize_provider(provider: str) -> str:
    """Normalize UI provider labels to config values."""
    return provider.lower()


def openai_api_key_required() -> bool:
    """Return whether current sidebar selections need an OpenAI API key."""
    llm_provider = normalize_provider(st.session_state.get("llm_provider", "OpenAI"))
    embedding_provider = normalize_provider(st.session_state.get("embedding_provider", "OpenAI"))
    return llm_provider == "openai" or embedding_provider == "openai"


def get_llm_signature(config: AppConfig) -> tuple:
    """Return settings that determine which answer model is used."""
    return (
        config.model_config.provider,
        config.model_config.name,
        config.model_config.temperature,
        config.ollama_config.base_url if config.model_config.provider == "ollama" else None
    )


def get_embedding_signature(config: AppConfig) -> tuple:
    """Return settings that determine how the vector store was embedded."""
    return (
        config.embedding_config.provider,
        config.embedding_config.model,
        config.embedding_config.chunk_size,
        config.embedding_config.chunk_overlap,
        config.ollama_config.base_url if config.embedding_config.provider == "ollama" else None
    )


def store_processed_source(vectorstore, qa_service: QAService, config: AppConfig, feature: str) -> None:
    """Persist processed source state in Streamlit session."""
    st.session_state.vectorstore = vectorstore
    st.session_state.qa_service = qa_service
    st.session_state.config = config
    st.session_state.qa_llm_signature = get_llm_signature(config)
    st.session_state.source_embedding_signature = get_embedding_signature(config)
    st.session_state.processed_feature = feature
    st.session_state.documents_loaded = True
    st.session_state.messages = []


def sync_qa_service_with_sidebar() -> bool:
    """
    Rebuild QAService when answer-model settings change.

    Returns:
        True when QA can proceed, False when the source must be reprocessed.
    """
    try:
        current_config = get_config_from_ui()
    except (APIKeyError, ConfigurationError) as e:
        st.error(f"Configuration error: {str(e)}")
        return False

    current_feature = st.session_state.get("feature", "Documents")
    if st.session_state.get("processed_feature") != current_feature:
        st.warning("The selected source type changed. Please process the source again before asking questions.")
        return False

    current_embedding_signature = get_embedding_signature(current_config)
    if current_embedding_signature != st.session_state.get("source_embedding_signature"):
        st.warning("Embedding settings changed. Please process the source again so retrieval uses the selected embedding model.")
        return False

    current_llm_signature = get_llm_signature(current_config)
    if current_llm_signature != st.session_state.get("qa_llm_signature"):
        try:
            st.session_state.qa_service = QAService(
                vectorstore=st.session_state.vectorstore,
                config=current_config
            )
            st.session_state.config = current_config
            st.session_state.qa_llm_signature = current_llm_signature
            st.info(f"Switched answer model to {current_config.model_config.provider}: {current_config.model_config.name}")
        except QAChainError as e:
            st.error(f"Error switching answer model: {str(e)}")
            return False

    return True


def get_config_from_ui() -> AppConfig:
    """Get configuration from UI inputs"""
    api_key = st.session_state.get("api_key_input", os.getenv("OPENAI_API_KEY", ""))
    llm_provider = normalize_provider(st.session_state.get("llm_provider", "OpenAI"))
    embedding_provider = normalize_provider(st.session_state.get("embedding_provider", "OpenAI"))
    model_name = (
        st.session_state.get("openai_model_name", "gpt-3.5-turbo")
        if llm_provider == "openai"
        else st.session_state.get("ollama_llm_model", "phi3")
    )
    embedding_model = (
        st.session_state.get("openai_embedding_model", "text-embedding-ada-002")
        if embedding_provider == "openai"
        else st.session_state.get("ollama_embedding_model", "nomic-embed-text")
    )
    ollama_base_url = st.session_state.get("ollama_base_url", "http://localhost:11434")
    temperature = st.session_state.get("temperature", 0.7)
    
    if openai_api_key_required() and not api_key:
        raise APIKeyError("OpenAI API key is required")
    
    try:
        config = AppConfig.from_env(
            api_key=api_key or None,
            llm_provider=llm_provider,
            embedding_provider=embedding_provider,
            model_name=model_name,
            embedding_model=embedding_model,
            temperature=temperature,
            ollama_base_url=ollama_base_url,
            ollama_llm_model=model_name,
            ollama_embedding_model=embedding_model
        )
        return config
    except Exception as e:
        raise ConfigurationError(f"Failed to create configuration: {str(e)}") from e


def render_sidebar():
    """Render sidebar configuration"""
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Feature selector - makes it easy to add more sources later
        feature = st.selectbox(
            "Source",
            ["Documents", "YouTube"],
            index=0,
            key="feature"
        )

        st.divider()

        st.selectbox(
            "Answer Model Provider",
            ["OpenAI", "Ollama"],
            index=0,
            key="llm_provider"
        )

        if normalize_provider(st.session_state.get("llm_provider", "OpenAI")) == "openai":
            st.selectbox(
                "OpenAI Answer Model",
                ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
                index=0,
                key="openai_model_name"
            )
        else:
            st.text_input(
                "Ollama Answer Model",
                value=os.getenv("OLLAMA_LLM_MODEL", "phi3"),
                help="Example: phi3",
                key="ollama_llm_model"
            )

        st.selectbox(
            "Embedding Provider",
            ["OpenAI", "Ollama"],
            index=0,
            key="embedding_provider"
        )

        if normalize_provider(st.session_state.get("embedding_provider", "OpenAI")) == "openai":
            st.text_input(
                "OpenAI Embedding Model",
                value=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002"),
                key="openai_embedding_model"
            )
        else:
            st.text_input(
                "Ollama Embedding Model",
                value=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
                help="Use an embedding model, not a chat model. Example: nomic-embed-text",
                key="ollama_embedding_model"
            )

        if (
            normalize_provider(st.session_state.get("llm_provider", "OpenAI")) == "ollama"
            or normalize_provider(st.session_state.get("embedding_provider", "OpenAI")) == "ollama"
        ):
            st.text_input(
                "Ollama Base URL",
                value=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                key="ollama_base_url"
            )

        if openai_api_key_required():
            st.text_input(
                "OpenAI API Key",
                type="password",
                value=os.getenv("OPENAI_API_KEY", ""),
                help="Required when either answer model or embedding provider is OpenAI",
                key="api_key_input"
            )
        
        # Temperature slider
        st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Controls randomness in responses",
            key="temperature"
        )


def render_upload_tab():
    """Render document upload / source processing tab"""
    st.header("Upload / Provide Source")
    st.markdown("Select a source type and provide input to process")

    feature = st.session_state.get("feature", "Documents")

    if feature == "Documents":
        st.subheader("Upload Documents")
        st.markdown("Upload PDF files to analyze")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=["pdf"],
            accept_multiple_files=True
        )
        api_key = st.session_state.get("api_key_input", "")
        can_process = not openai_api_key_required() or bool(api_key)

        if uploaded_files and can_process:
            if st.button("Process Documents", type="primary"):
                with st.spinner("Processing documents..."):
                    try:
                        # Get configuration
                        config = get_config_from_ui()
                        st.session_state.config = config

                        # Initialize document service
                        document_service = DocumentService(config)

                        # Process documents
                        vectorstore = document_service.process_documents(uploaded_files)

                        # Initialize QA service
                        qa_service = QAService(vectorstore=vectorstore, config=config)

                        # Store in session state
                        st.session_state.document_service = document_service
                        store_processed_source(vectorstore, qa_service, config, feature)

                        st.success(f"✅ Successfully processed {len(uploaded_files)} document(s)!")
                        st.info("You can now switch to the 'Ask Questions' tab to query your documents.")

                    except (APIKeyError, ConfigurationError) as e:
                        st.error(f"Configuration error: {str(e)}")
                    except DocumentProcessingError as e:
                        st.error(f"Error processing documents: {str(e)}")
                    except Exception as e:
                        logger.exception("Unexpected error")
                        st.error(f"Unexpected error: {str(e)}")

        elif uploaded_files and not can_process:
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar to process documents.")

    elif feature == "YouTube":
        st.subheader("YouTube URL")
        st.markdown("Provide a YouTube video URL to analyze its transcript")

        youtube_url = st.text_input("YouTube video URL", key="youtube_url_input", placeholder="https://www.youtube.com/watch?v=...")
        api_key = st.session_state.get("api_key_input", "")
        can_process = not openai_api_key_required() or bool(api_key)

        if youtube_url and can_process:
            if st.button("Process YouTube", type="primary"):
                with st.spinner("Processing YouTube video..."):
                    try:
                        # Get configuration
                        config = get_config_from_ui()
                        st.session_state.config = config

                        # Initialize YouTube service
                        yt_service = YouTubeService(config)

                        # Process video -> vectorstore
                        vectorstore = yt_service.process_video(youtube_url)

                        # Initialize QA service
                        qa_service = QAService(vectorstore=vectorstore, config=config)

                        # Store in session state
                        st.session_state.youtube_service = yt_service
                        store_processed_source(vectorstore, qa_service, config, feature)

                        st.success("✅ Successfully processed YouTube video!")
                        st.info("You can now switch to the 'Ask Questions' tab to query the video transcript.")

                    except (APIKeyError, ConfigurationError) as e:
                        st.error(f"Configuration error: {str(e)}")
                    except DocumentProcessingError as e:
                        st.error(f"Error processing YouTube video: {str(e)}")
                    except Exception as e:
                        logger.exception("Unexpected error")
                        st.error(f"Unexpected error: {str(e)}")
        elif youtube_url and not can_process:
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar to process the YouTube video.")


def render_qa_tab():
    """Render question-answering tab"""
    st.header("Ask Questions")
    
    if not st.session_state.documents_loaded:
        st.info("👈 Please upload and process documents or a video in the 'Upload / Provide Source' tab first.")
        return

    if not sync_qa_service_with_sidebar():
        return
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Question input using form instead of chat_input
    with st.form(key="question_form", clear_on_submit=True):
        question_text = st.text_input(
            "Ask a question about your documents...",
            key="question_input",
            placeholder="Type your question here"
        )
        submit_button = st.form_submit_button("Send", type="primary")
    
    # Process question only once per submission
    if submit_button and question_text:
        # Check if this exact question was just processed (prevent duplicates)
        # Compare with the last user message to avoid reprocessing
        should_process = True
        if st.session_state.messages:
            last_user_msg = None
            for msg in reversed(st.session_state.messages):
                if msg.get("role") == "user":
                    last_user_msg = msg
                    break
            if last_user_msg and last_user_msg.get("content") == question_text:
                should_process = False
        
        if should_process:
            # Add user question to chat
            user_message = ChatMessage(
                role="user",
                content=question_text,
                timestamp=datetime.now()
            )
            st.session_state.messages.append(user_message.to_dict())
            
            # Display user message immediately
            with st.chat_message("user"):
                st.markdown(question_text)
            
            # Get answer and display immediately
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        answer_text = st.session_state.qa_service.ask_question_text(question_text)
                        st.markdown(answer_text)
                        
                        assistant_message = ChatMessage(
                            role="assistant",
                            content=answer_text,
                            timestamp=datetime.now()
                        )
                        st.session_state.messages.append(assistant_message.to_dict())
                        
                    except QAChainError as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                    except Exception as e:
                        logger.exception("Unexpected error in QA")
                        error_msg = f"Unexpected error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()


def main():
    """Main application entry point"""
    initialize_session_state()
    
    st.title("📚 Document Q&A System")
    st.markdown("Upload documents or provide a YouTube link and ask questions about them using AI")

    # Render sidebar
    render_sidebar()
    
    # Main content area
    tab1, tab2 = st.tabs(["📄 Upload / Source", "💬 Ask Questions"])

    
    with tab1:
        render_upload_tab()
    
    with tab2:
        render_qa_tab()


if __name__ == "__main__":
    main()
