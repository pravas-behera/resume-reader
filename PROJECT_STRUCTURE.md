# Project Structure Guide

This document provides a quick reference to the project structure and where to find/modify different components.

## Quick Navigation

### 🎯 Want to add a new document format?
→ `src/infrastructure/loaders/`
- Create a new loader extending `BaseDocumentLoader`
- Register in `loader_factory.py`

### 🎯 Want to change the UI?
→ `src/app/main.py`
- Modify Streamlit components
- Update rendering functions

### 🎯 Want to modify business logic?
→ `src/services/`
- `document_service.py` - Document processing logic
- `qa_service.py` - Question-answering logic

### 🎯 Want to add a new vector store?
→ `src/infrastructure/vectorstores/`
- Implement `IVectorStore` interface
- Extend `BaseVectorStore` if needed

### 🎯 Want to change configuration?
→ `src/core/config.py`
- Modify `AppConfig` class
- Add new configuration options

### 🎯 Want to add a new LLM provider?
→ `src/infrastructure/llm/`
- Implement `ILLMService` interface
- Register it in `llm_factory.py`

### 🎯 Want to add a new embedding provider?
→ `src/infrastructure/embeddings/`
- Implement `IEmbeddingService` interface
- Register it in `embedding_factory.py`

## File Locations by Task

| Task | File Location |
|------|--------------|
| Change chunk size | `src/core/config.py` → `EmbeddingConfig` |
| Modify prompt template | `src/services/qa_service.py` → `prompt_template` |
| Add error handling | `src/core/exceptions.py` |
| Change logging format | `src/core/logger.py` |
| Add new document model | `src/domain/models.py` |
| Update UI layout | `src/app/main.py` |
| Change embedding model | `src/core/config.py` → `EmbeddingConfig.model` |
| Change LLM provider | `src/core/config.py` → `ModelConfig.provider` |
| Change embedding provider | `src/core/config.py` → `EmbeddingConfig.provider` |
| Change Ollama defaults | `src/core/config.py` → `OllamaConfig` |
| Modify text splitting | `src/utils/text_splitter.py` |

## Key Interfaces

### IDocumentLoader
Located: `src/domain/interfaces.py`
- Implemented by: All loaders in `src/infrastructure/loaders/`
- Used by: `DocumentService`

### IVectorStore
Located: `src/domain/interfaces.py`
- Implemented by: `FAISSVectorStore` and future stores
- Used by: `DocumentService`, `QAService`

### ILLMService
Located: `src/domain/interfaces.py`
- Implemented by: `OpenAIClient`, `OllamaClient`
- Selected by: `LLMFactory`
- Used by: `QAService`

### IEmbeddingService
Located: `src/domain/interfaces.py`
- Implemented by: `OpenAIEmbeddingService`, `OllamaEmbeddingService`
- Selected by: `EmbeddingFactory`
- Used by: `DocumentService`, `YouTubeService`

## Dependency Flow

```
app.py
  └─> src/app/main.py
        └─> src/services/document_service.py
              ├─> src/infrastructure/loaders/loader_factory.py
              ├─> src/utils/text_splitter.py
              ├─> src/infrastructure/embeddings/embedding_factory.py
              └─> src/infrastructure/vectorstores/faiss_store.py
        └─> src/services/youtube_service.py
              ├─> src/utils/youtube_transcript.py
              ├─> src/utils/text_splitter.py
              ├─> src/infrastructure/embeddings/embedding_factory.py
              └─> src/infrastructure/vectorstores/faiss_store.py
        └─> src/services/qa_service.py
              ├─> src/infrastructure/llm/llm_factory.py
              └─> src/infrastructure/vectorstores/faiss_store.py
```

## Adding New Features

### Example: Adding DOCX Support

1. **Create loader** (`src/infrastructure/loaders/docx_loader.py`):
```python
from src.infrastructure.loaders.base_loader import BaseDocumentLoader

class DOCXLoader(BaseDocumentLoader):
    def __init__(self):
        super().__init__(supported_extensions=[".docx"])
    
    def load(self, file_path: str) -> List[Document]:
        # Implementation here
        pass
```

2. **Register in factory** (`src/infrastructure/loaders/loader_factory.py`):
```python
from src.infrastructure.loaders.docx_loader import DOCXLoader

class DocumentLoaderFactory:
    @classmethod
    def _initialize_loaders(cls):
        cls._loaders = [
            PDFLoader(),
            DOCXLoader(),  # Add here
        ]
```

3. **Done!** The system will automatically support DOCX files.

## Testing Locations

(To be implemented)
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Test fixtures: `tests/fixtures/`

## Configuration Files

- Environment variables: `.env` (create from `env_example.txt`)
- Dependencies: `requirements.txt`
- Git ignore: `.gitignore`

## Documentation Files

- Main README: `README.md`
- Architecture: `ARCHITECTURE.md`
- Control flow: `CONTROL_FLOW.md`
- Quick Start: `QUICKSTART.md`
- This file: `PROJECT_STRUCTURE.md`
