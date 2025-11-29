# Document Q&A System

A professional document question-answering system built with LangChain, Streamlit, and OpenAI's ChatGPT API. This project follows SOLID principles and best practices for maintainable, scalable code.

## Features

- 📄 **PDF Document Processing**: Upload and process multiple PDF files
- 🔍 **Semantic Search**: Uses vector embeddings for intelligent document retrieval
- 💬 **Interactive Q&A**: Chat interface for asking questions about your documents
- 🤖 **OpenAI Integration**: Powered by GPT-3.5 or GPT-4 models
- 🎨 **Streamlit UI**: Clean and intuitive web interface
- 🏗️ **Professional Architecture**: SOLID principles, dependency injection, and clean code structure

## Architecture

This project follows a clean architecture pattern with:

- **Domain Layer**: Business logic interfaces and models
- **Service Layer**: Business logic implementation (Single Responsibility Principle)
- **Infrastructure Layer**: External integrations (OpenAI, FAISS, etc.)
- **Application Layer**: UI and orchestration
- **Core Layer**: Configuration, logging, and exceptions

### SOLID Principles Applied

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Extensible through interfaces without modification
- **Liskov Substitution**: Proper inheritance and abstraction
- **Interface Segregation**: Focused, specific interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy `env_example.txt` to `.env`
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

## Usage

1. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** to the URL shown (usually `http://localhost:8501`)

3. **Upload Documents**:
   - Go to the "Upload Documents" tab
   - Enter your OpenAI API key in the sidebar (or set it in `.env`)
   - Upload one or more PDF files
   - Click "Process Documents"

4. **Ask Questions**:
   - Switch to the "Ask Questions" tab
   - Type your question in the chat input
   - Get AI-powered answers based on your documents

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
│   │   │   └── openai_client.py
│   │   └── embeddings/        # Embedding services
│   │       └── openai_embeddings.py
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
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_K=3
```

### Model Selection
- Choose between GPT-3.5-turbo, GPT-4, or GPT-4-turbo-preview in the sidebar
- Adjust temperature to control response randomness (0.0 = deterministic, 1.0 = creative)

### Document Processing
- Documents are split into chunks of 1000 characters with 200 character overlap
- Top 3 most relevant chunks are retrieved for each question

## How It Works

1. **Document Processing**: 
   - PDFs are loaded using factory pattern (extensible for more formats)
   - Documents are split into smaller text chunks
   - Each chunk is converted to vector embeddings using OpenAI
   - Vectors are stored in a FAISS index for fast similarity search

2. **Question Answering**:
   - User question is processed through the QA service
   - Similar document chunks are retrieved from the vector store
   - Retrieved context and question are sent to ChatGPT via LLM service
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
2. Update service configuration to use the new provider

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

