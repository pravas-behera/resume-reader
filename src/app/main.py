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
from src.domain.models import ChatMessage, Question
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
    if "documents_loaded" not in st.session_state:
        st.session_state.documents_loaded = False
    if "config" not in st.session_state:
        st.session_state.config = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "feature" not in st.session_state:
        # Allows easy extension to add more feature sources later
        st.session_state.feature = "Documents"


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

        # API Key input (required to process sources)
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
    """Render document upload / source processing tab"""
    st.header("Upload / Provide Source")
    st.markdown("Select a source type and provide input to process")

    # Show both Document upload and YouTube input on the same page
    st.subheader("Upload Documents")
    st.markdown("Upload PDF files to analyze")
    doc_col, yt_col = st.columns(2)

    with doc_col:
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            key="uploaded_files"
        )

    with yt_col:
        st.subheader("YouTube URL")
        st.markdown("Provide a YouTube video URL to analyze its transcript")
        youtube_url = st.text_input("YouTube video URL", key="youtube_url_input", placeholder="https://www.youtube.com/watch?v=...")
        if youtube_url:
            try:
                st.video(youtube_url)
            except Exception:
                embed_html = f"<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/{youtube_url.split('v=')[-1].split('&')[0]}\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>"
                st.components.v1.html(embed_html, height=360)

    api_key = st.session_state.get("api_key_input", "")

    # Single button to process whichever sources are provided. If one is empty, the other still runs.
    if st.button("Process Sources", type="primary"):
        if not api_key:
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar to process sources.")
        elif (not uploaded_files) and (not youtube_url):
            st.warning("⚠️ Please provide at least one source: upload documents or enter a YouTube URL.")
        else:
            with st.spinner("Processing sources..."):
                try:
                    config = get_config_from_ui()
                    st.session_state.config = config

                    qa_service = None
                    # If documents provided, process them and prefer resulting vectorstore for QA
                    if uploaded_files:
                        document_service = DocumentService(config)
                        vectorstore = document_service.process_documents(uploaded_files)
                        qa_service = QAService(vectorstore=vectorstore, config=config)
                        st.session_state.document_service = document_service
                        st.session_state.qa_service = qa_service
                        st.session_state.documents_loaded = True
                        st.success(f"✅ Successfully processed {len(uploaded_files)} document(s)!")

                    # If youtube provided, process it as well. If documents were processed we append youtube
                    if youtube_url:
                        yt_service = YouTubeService(config)
                        # If we already have a vectorstore from documents, append youtube data to it
                        if uploaded_files:
                            vectorstore = yt_service.process_video(youtube_url, existing_store=vectorstore)
                        else:
                            vectorstore = yt_service.process_video(youtube_url)

                        # If we didn't already have a qa_service (no documents), create one from youtube vectorstore
                        if qa_service is None:
                            qa_service = QAService(vectorstore=vectorstore, config=config)
                            st.session_state.qa_service = qa_service

                        st.session_state.youtube_service = yt_service
                        st.session_state.documents_loaded = True
                        st.success("✅ Successfully processed YouTube video!")

                    if qa_service:
                        st.info("You can now switch to the 'Ask Questions' tab to query processed sources.")

                except (APIKeyError, ConfigurationError) as e:
                    st.error(f"Configuration error: {str(e)}")
                except DocumentProcessingError as e:
                    st.error(f"Error processing documents/video: {str(e)}")
                except Exception as e:
                    logger.exception("Unexpected error")
                    st.error(f"Unexpected error: {str(e)}")


def render_qa_tab():
    """Render question-answering tab"""
    st.header("Ask Questions")
    
    if not st.session_state.documents_loaded:
        st.info("👈 Please upload and process documents or a video in the 'Upload / Provide Source' tab first.")
        return

    # Submission callback: runs before Streamlit rerenders when the form is submitted.
    def process_submission():
        q = st.session_state.get("question_input", "").strip()
        if not q:
            return

        # Prevent duplicate immediate resubmission
        last_user_msg = None
        for msg in reversed(st.session_state.messages):
            if msg.get("role") == "user":
                last_user_msg = msg
                break
        if last_user_msg and last_user_msg.get("content") == q:
            return

        # Append user message
        user_message = ChatMessage(role="user", content=q, timestamp=datetime.now())
        st.session_state.messages.append(user_message.to_dict())

        try:
            answer_obj = st.session_state.qa_service.ask_question(Question(text=q, timestamp=datetime.now()))
            answer_text = answer_obj.text
            assistant_message = ChatMessage(role="assistant", content=answer_text, timestamp=datetime.now())
            st.session_state.messages.append(assistant_message.to_dict())

            # Append sources as assistant message if present
            if getattr(answer_obj, 'source_documents', None):
                sources = []
                for sd in answer_obj.source_documents:
                    src = None
                    if hasattr(sd, 'source') and sd.source:
                        src = sd.source
                    elif hasattr(sd, 'metadata') and isinstance(sd.metadata, dict):
                        src = sd.metadata.get('source')
                    if src:
                        sources.append(str(src))
                # Intentionally omit appending source metadata to the chat to avoid exposing file paths/urls

        except Exception as e:
            logger.exception("Error in process_submission")
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})


    # Render chat history inside a scrollable container (auto-scroll to bottom)
    # Build HTML for messages
    chat_items = []
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        # Simple sanitization for HTML
        content_html = content.replace("\n", "<br/>")
        if role == "user":
            chat_items.append(f"<div class='bubble user'>{content_html}</div>")
        else:
            chat_items.append(f"<div class='bubble assistant'>{content_html}</div>")
    
    chat_html = f"""
    <html>
    <head>
    <style>
    .chat-container {{
        height: 60vh;
        overflow-y: auto;
        padding: 12px;
        background: #F8F9FA;
        border-radius: 6px;
        border: 1px solid #e6e6e6;
    }}
    .bubble {{
        padding: 10px 14px;
        margin: 8px 0;
        border-radius: 12px;
        max-width: 85%;
        word-wrap: break-word;
    }}
    .user {{
        background: #DCF8C6;
        align-self: flex-end;
        margin-left: auto;
    }}
    .assistant {{
        background: #FFFFFF;
        border: 1px solid #e6e6e6;
        margin-right: auto;
    }}
    .chat-wrap {{
        display: flex;
        flex-direction: column;
    }}
    </style>
    </head>
    <body>
    <div class='chat-container' id='chat-container'>
        <div class='chat-wrap'>
            {''.join(chat_items)}
        </div>
    </div>
    <script>
        // Scroll to bottom so newest messages are visible
        const chat = document.getElementById('chat-container');
        if (chat) {{ chat.scrollTop = chat.scrollHeight; }}
    </script>
    </body>
    </html>
    """

    # Render the chat HTML. Height matches the CSS container height.
    st.components.v1.html(chat_html, height=600)

    # Question input using form (kept below the chat container so it remains visible)
    # Inject CSS to style the chat card and the input form to match the requested look
    st.markdown(
        """
        <style>
        /* Style the Streamlit form container to look like a white rounded input box */
        [data-testid="stForm"] {
            position: sticky;
            bottom: 20px;
            background: #ffffff;
            z-index: 999;
            padding: 18px;
            border-radius: 10px;
            width: 92%;
            margin: 24px auto;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }

        /* Style the text input to be dark inside with rounded corners */
        [data-testid="stTextInput"] input {
            background: #262328 !important;
            color: #ddd !important;
            border-radius: 8px !important;
            padding: 14px !important;
            border: 1px solid #c84b4b !important;
            box-shadow: none !important;
        }
        [data-testid="stTextInput"] input::placeholder { color: #8b8b8b !important; }

        /* Style the Send button to be red like the screenshot */
        button[kind] {
            background: #ff5a57 !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* Make the chat HTML component appear centered and with a white card look on the page */
        .streamlit-expander, .stApp > div:nth-child(1) {
            /* minimal impact - keep defaults */
        }

        /* Ensure the chat component iframe (rendered HTML) doesn't look cramped */
        .stApp iframe[srcdoc] {
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Render the form inside the same visual card. Use a callback to handle submission so messages
    # are appended before the chat is re-rendered (makes new messages appear immediately).
    with st.form(key="question_form", clear_on_submit=True):
        st.text_input("", key="question_input", placeholder="Type your question here")
        st.form_submit_button("Send", on_click=process_submission)
    
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
