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
from src.domain.models import Question, ChatMessage
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
    if "documents_loaded" not in st.session_state:
        st.session_state.documents_loaded = False
    if "config" not in st.session_state:
        st.session_state.config = None
    if "messages" not in st.session_state:
        st.session_state.messages = []


def get_config_from_ui() -> AppConfig:
    """Get configuration from UI inputs"""
    api_key = st.session_state.get("api_key_input", os.getenv("OPENAI_API_KEY", ""))
    model_name = st.session_state.get("model_name", "gpt-3.5-turbo")
    temperature = st.session_state.get("temperature", 0.7)
    
    if not api_key:
        raise APIKeyError("OpenAI API key is required")
    
    try:
        config = AppConfig.from_env(api_key=api_key)
        config.update_model_config(model_name, temperature)
        return config
    except Exception as e:
        raise ConfigurationError(f"Failed to create configuration: {str(e)}") from e


def render_sidebar():
    """Render sidebar configuration"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Enter your OpenAI API key or set it in .env file",
            key="api_key_input"
        )
        
        st.divider()
        
        # Model selection
        model_name = st.selectbox(
            "Model",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
            index=0,
            key="model_name"
        )
        
        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Controls randomness in responses",
            key="temperature"
        )


def render_upload_tab():
    """Render document upload tab"""
    st.header("Upload Documents")
    st.markdown("Upload PDF files to analyze")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    api_key = st.session_state.get("api_key_input", "")
    
    if uploaded_files and api_key:
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
                    st.session_state.qa_service = qa_service
                    st.session_state.documents_loaded = True
                    
                    st.success(f"✅ Successfully processed {len(uploaded_files)} document(s)!")
                    st.info("You can now switch to the 'Ask Questions' tab to query your documents.")
                    
                except (APIKeyError, ConfigurationError) as e:
                    st.error(f"Configuration error: {str(e)}")
                except DocumentProcessingError as e:
                    st.error(f"Error processing documents: {str(e)}")
                except Exception as e:
                    logger.exception("Unexpected error")
                    st.error(f"Unexpected error: {str(e)}")
    
    elif uploaded_files and not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to process documents.")


def render_qa_tab():
    """Render question-answering tab"""
    st.header("Ask Questions")
    
    if not st.session_state.documents_loaded:
        st.info("👈 Please upload and process documents in the 'Upload Documents' tab first.")
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
    st.markdown("Upload documents and ask questions about them using AI")
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    tab1, tab2 = st.tabs(["📄 Upload Documents", "💬 Ask Questions"])
    
    
    with tab1:
        render_upload_tab()
    
    with tab2:
        render_qa_tab()


if __name__ == "__main__":
    main()

