# src/app/main.py
import os

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from src.core.config import AppConfig
from src.services.document_service import DocumentService
from src.services.qa_service import QAService

app = FastAPI()

load_dotenv()  # Loads variables from .env into environment

api_key = os.getenv("OPENAI_API_KEY")
config = AppConfig.from_env(api_key=api_key)
doc_service = DocumentService(config)


@app.post("/ask")
async def ask_question(file: UploadFile = File(...), question: str = Form(...)):
    try:
        # Read file content into memory
        file_content = await file.read()
        # Wrap in a BytesIO object to mimic file-like interface
        from io import BytesIO
        file_like = BytesIO(file_content)
        file_like.name = file.filename  # Some loaders may expect a name attribute

        # Process the document
        vectorstore = doc_service.process_documents([file_like])
        qa_service = QAService(vectorstore=vectorstore,config=config)
        # Get answer from QA service
        answer = qa_service.ask_question_text(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Document Q&A API is running."}