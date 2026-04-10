# AI-Powered Knowledge Bot

A professional document and YouTube question-answering system built with LangChain, Streamlit, OpenAI, and local Ollama models. This project follows SOLID principles and best practices for maintainable, scalable code.

## Features

- 📄 **PDF Document Processing**: Upload and process multiple PDF files
- 🔍 **Semantic Search**: Uses vector embeddings for intelligent document retrieval
- 💬 **Interactive Q&A**: Chat interface for asking questions about your documents
- 🤖 **Provider Selection**: Use OpenAI or local Ollama models for answer generation
- 🧠 **Configurable Embeddings**: Use OpenAI embeddings or local Ollama embeddings such as `nomic-embed-text`
- 🎨 **Streamlit UI**: Clean and intuitive web interface
- 🏗️ **Professional Architecture**: SOLID principles, dependency injection, and clean code structure
- 📺 **YouTube Video Q&A**: Ask questions about YouTube videos by providing a video link

## Architecture

This project follows a clean architecture pattern with:

- **Domain Layer**: Business logic interfaces and models
- **Service Layer**: Business logic implementation (Single Responsibility Principle)
- **Infrastructure Layer**: External integrations (OpenAI, Ollama, FAISS, etc.)
- **Application Layer**: UI and orchestration
- **Core Layer**: Configuration, logging, and exceptions

### SOLID Principles Applied

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Extensible through interfaces without modification
- **Liskov Substitution**: Proper inheritance and abstraction
- **Interface Segregation**: Focused, specific interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

## Prerequisites

- Python 3.11 is recommended. Python 3.14 is not currently compatible with this project's pinned Streamlit/protobuf stack.
- OpenAI API key if using OpenAI models ([Get one here](https://platform.openai.com/api-keys))
- Ollama installed and running if using local models

## Installation

1. **Clone or download this repository**

2. **Create and activate a Python 3.11 environment**:
   ```bash
   python3.11 -m venv .venv311
   source .venv311/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `env_example.txt` to `.env`
   - For OpenAI, add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```
   - For local Ollama-only use, you can set:
     ```env
     LLM_PROVIDER=ollama
     EMBEDDING_PROVIDER=ollama
     OLLAMA_BASE_URL=http://127.0.0.1:11434
     OLLAMA_LLM_MODEL=phi3
     OLLAMA_EMBEDDING_MODEL=nomic-embed-text
     ```

5. **Prepare Ollama models if using local mode**:
   ```bash
   ollama serve
   ollama pull phi3
   ollama pull nomic-embed-text
   ```

## Usage

### Streamlit App (Document Q&A)

1. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** to the URL shown (usually `http://localhost:8501`)

3. **Upload Documents**:
   - Go to the "Upload / Source" tab
   - Choose `OpenAI` or `Ollama` for the answer model provider
   - Choose `OpenAI` or `Ollama` for the embedding provider
   - Enter your OpenAI API key only if either selected provider is OpenAI
   - For Ollama, set the base URL to `http://127.0.0.1:11434` or `http://localhost:11434`
   - Upload one or more PDF files
   - Click "Process Documents"

4. **Ask Questions**:
   - Switch to the "Ask Questions" tab
   - Type your question in the chat input
   - Get AI-powered answers based on your documents or YouTube transcript

Provider switching behavior:
- You can switch the answer model provider after processing a source. The app rebuilds the QA chain against the existing vector store.
- If you switch the embedding provider or embedding model after processing, reprocess the source. The FAISS index must be built and queried with the same embedding model.

### FastAPI Endpoints (API Q&A)

1. **Run the FastAPI server**:
   ```bash
   uvicorn src.controllers.ask_api:app --reload
   ```

2. **Open your browser** to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API docs.

3. **Ask questions about documents (file upload)**:
   - Endpoint: `POST /document/ask`
   - Required form fields: `file` (UploadFile), `question` (str)
   - Optional model fields: `api_key`, `llm_provider`, `llm_model`, `embedding_provider`, `embedding_model`, `ollama_base_url`, `temperature`

4. **Ask questions about YouTube videos**:
   - Endpoint: `POST /youtube/ask`
   - Required form fields: `url` (YouTube video link), `question` (str)
   - Optional model fields: `api_key`, `llm_provider`, `llm_model`, `embedding_provider`, `embedding_model`, `ollama_base_url`, `temperature`
   - Example using `curl`:
     ```bash
     curl -X POST http://127.0.0.1:8000/youtube/ask \
       -F "url=https://www.youtube.com/watch?v=YOUR_VIDEO_ID" \
       -F "question=What is this video about?"
     ```
   - Example using local Ollama:
     ```bash
     curl -X POST http://127.0.0.1:8000/youtube/ask \
       -F "url=https://www.youtube.com/watch?v=YOUR_VIDEO_ID" \
       -F "question=What is this video about?" \
       -F "llm_provider=ollama" \
       -F "llm_model=phi3" \
       -F "embedding_provider=ollama" \
       -F "embedding_model=nomic-embed-text" \
       -F "ollama_base_url=http://127.0.0.1:11434"
     ```

## Project Structure

```
DocResponse/
├── src/
│   ├── app/                    # Application layer (UI)
│   │   ├── __init__.py
│   │   └── main.py            # Streamlit application
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── logger.py          # Logging setup
│   ├── domain/                 # Domain layer
│   │   ├── __init__.py
│   │   ├── models.py          # Domain models/DTOs
│   │   └── interfaces.py      # Abstract interfaces
│   ├── services/               # Service layer (business logic)
│   │   ├── __init__.py
│   │   ├── document_service.py
│   │   ├── youtube_service.py
│   │   └── qa_service.py
│   ├── infrastructure/         # Infrastructure layer
│   │   ├── loaders/           # Document loaders
│   │   │   ├── base_loader.py
│   │   │   ├── pdf_loader.py
│   │   │   └── loader_factory.py
│   │   ├── vectorstores/      # Vector store implementations
│   │   │   ├── base_store.py
│   │   │   └── faiss_store.py
│   │   ├── llm/               # LLM clients
│   │   │   ├── llm_factory.py
│   │   │   ├── openai_client.py
│   │   │   └── ollama_client.py
│   │   └── embeddings/        # Embedding services
│   │       ├── embedding_factory.py
│   │       ├── openai_embeddings.py
│   │       └── ollama_embeddings.py
│   └── utils/                 # Utility functions
│       └── text_splitter.py
├── app.py                     # Application entry point
├── requirements.txt           # Python dependencies
├── env_example.txt           # Environment variables template
├── .gitignore                # Git ignore file
└── README.md                 # This file
```

## Design Patterns Used

- **Factory Pattern**: `DocumentLoaderFactory` for creating appropriate loaders
- **Strategy Pattern**: Different implementations for loaders, vector stores, LLMs
- **Dependency Injection**: Services receive dependencies through constructors
- **Repository Pattern**: Vector store abstraction
- **Service Layer Pattern**: Business logic separated from infrastructure

## Configuration

### Environment Variables

Create a `.env` file with:

```env
OPENAI_API_KEY=your_key_here
LLM_PROVIDER=openai
MODEL_NAME=gpt-3.5-turbo
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-ada-002
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_LLM_MODEL=phi3
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
TEMPERATURE=0.7
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_K=3
```

### Model Selection
- Choose `OpenAI` or `Ollama` as the answer model provider in the sidebar
- Choose `OpenAI` or `Ollama` as the embedding provider in the sidebar
- For local mode, use an Ollama answer model such as `phi3` and an Ollama embedding model such as `nomic-embed-text`
- Adjust temperature to control response randomness (0.0 = deterministic, 1.0 = creative)

### Document Processing
- Documents are split into chunks of 1000 characters with 200 character overlap
- Top 3 most relevant chunks are retrieved for each question

## How It Works

1. **Document Processing**: 
   - PDFs are loaded using factory pattern (extensible for more formats)
   - Documents are split into smaller text chunks
   - Each chunk is converted to vector embeddings using the selected embedding provider
   - Vectors are stored in a FAISS index for fast similarity search

2. **Question Answering**:
   - User question is processed through the QA service
   - Similar document chunks are retrieved from the vector store
   - Retrieved context and question are sent to the selected OpenAI or Ollama LLM service
   - AI generates an answer based on the document context

## Extending the System

### Adding New Document Formats

1. Create a new loader in `src/infrastructure/loaders/` extending `BaseDocumentLoader`
2. Register it in `DocumentLoaderFactory`
3. The system will automatically support the new format

### Adding New Vector Stores

1. Create implementation in `src/infrastructure/vectorstores/` extending `BaseVectorStore`
2. Implement the `IVectorStore` interface
3. Update service to use the new store

### Adding New LLM Providers

1. Create implementation in `src/infrastructure/llm/` implementing `ILLMService`
2. Register it in `src/infrastructure/llm/llm_factory.py`

### Adding New Embedding Providers

1. Create implementation in `src/infrastructure/embeddings/` implementing `IEmbeddingService`
2. Register it in `src/infrastructure/embeddings/embedding_factory.py`

## Future Improvements

- [ ] Support for more document formats (DOCX, TXT, etc.)
- [ ] Document persistence across sessions
- [ ] Export chat history
- [ ] Multiple vector store backends (Pinecone, Weaviate, etc.)
- [ ] Advanced chunking strategies
- [ ] Source citation in answers
- [ ] Multi-language support
- [ ] Unit and integration tests
- [ ] CI/CD pipeline

## Troubleshooting

**Error: "No module named 'langchain'"**
- Run `pip install -r requirements.txt` to install all dependencies

**Error: "Invalid API key"**
- Check that your OpenAI API key is correct in `.env` or the sidebar
- Ensure you have credits in your OpenAI account
- OpenAI API keys are only required when either the answer model provider or embedding provider is OpenAI

**Ollama connection errors**
- Make sure Ollama is running: `ollama serve`
- Use `http://127.0.0.1:11434` as the Ollama base URL if `localhost` does not work
- Pull the required local models: `ollama pull phi3` and `ollama pull nomic-embed-text`

**Answers still use the old provider**
- The app automatically rebuilds the QA chain when only the answer model changes
- If you change the embedding provider or embedding model, reprocess the source because the vector store depends on the embedding model

**Documents not processing**
- Verify PDF files are not corrupted
- Check that files are actual PDFs (not images)
- Check logs for detailed error messages

**Import errors**
- Ensure you're running from the project root directory
- Check that all `__init__.py` files are present

## Code Quality

This project emphasizes:
- Type hints throughout
- Comprehensive error handling
- Logging for debugging
- Clear separation of concerns
- Extensible architecture
- Clean, readable code

## License

This project is open source and available for learning purposes.

## Contributing

Feel free to fork this project and make improvements! This is a learning project demonstrating professional software engineering practices.

