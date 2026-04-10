# src/controllers/ask_api.py
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from src.core.config import AppConfig
from src.services.document_service import DocumentService
from src.services.qa_service import QAService
from src.services.youtube_service import YouTubeService
from src.core.exceptions import DocumentProcessingError

app = FastAPI()

load_dotenv()  # Loads variables from .env into environment


def build_config(
    api_key: str,
    llm_provider: str,
    llm_model: str,
    embedding_provider: str,
    embedding_model: str,
    ollama_base_url: str,
    temperature: float
) -> AppConfig:
    """Build per-request config from API form controls."""
    return AppConfig.from_env(
        api_key=api_key or None,
        llm_provider=llm_provider,
        embedding_provider=embedding_provider,
        model_name=llm_model or None,
        embedding_model=embedding_model or None,
        temperature=temperature,
        ollama_base_url=ollama_base_url,
        ollama_llm_model=llm_model or None,
        ollama_embedding_model=embedding_model or None
    )


@app.post("/document/ask")
async def ask_question(
    file: UploadFile = File(...),
    question: str = Form(...),
    api_key: str = Form(""),
    llm_provider: str = Form("openai"),
    llm_model: str = Form(""),
    embedding_provider: str = Form("openai"),
    embedding_model: str = Form(""),
    ollama_base_url: str = Form("http://localhost:11434"),
    temperature: float = Form(0.7)
):
    try:
        config = build_config(
            api_key=api_key,
            llm_provider=llm_provider,
            llm_model=llm_model,
            embedding_provider=embedding_provider,
            embedding_model=embedding_model,
            ollama_base_url=ollama_base_url,
            temperature=temperature
        )
        doc_service = DocumentService(config)

        # Read file content into memory
        file_content = await file.read()
        # Wrap in a BytesIO object to mimic file-like interface
        from io import BytesIO
        file_like = BytesIO(file_content)
        file_like.name = file.filename  # Some loaders may expect a name attribute

        # Process the document
        vectorstore = doc_service.process_documents([file_like])
        qa_service = QAService(vectorstore=vectorstore, config=config)
        # Get answer from QA service
        answer = qa_service.ask_question_text(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Document Q&A API is running."}


@app.post("/youtube/ask")
async def youtube_ask(
    url: str = Form(...),
    question: str = Form(...),
    api_key: str = Form(""),
    llm_provider: str = Form("openai"),
    llm_model: str = Form(""),
    embedding_provider: str = Form("openai"),
    embedding_model: str = Form(""),
    ollama_base_url: str = Form("http://localhost:11434"),
    temperature: float = Form(0.7)
):
    """Process a YouTube URL, build a vector store from transcript, and answer a question."""
    try:
        if not url or not url.strip():
            raise HTTPException(status_code=400, detail="YouTube URL is required")

        config = build_config(
            api_key=api_key,
            llm_provider=llm_provider,
            llm_model=llm_model,
            embedding_provider=embedding_provider,
            embedding_model=embedding_model,
            ollama_base_url=ollama_base_url,
            temperature=temperature
        )
        yt_service = YouTubeService(config)
        vectorstore = yt_service.process_video(url)

        qa_service = QAService(vectorstore=vectorstore, config=config)
        answer = qa_service.ask_question_text(question)
        return {"answer": answer}

    except DocumentProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected
        raise HTTPException(status_code=500, detail=str(e))
