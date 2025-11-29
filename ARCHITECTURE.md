# Architecture Documentation

## Overview

This document describes the architecture of the Document Q&A System, which follows clean architecture principles and SOLID design patterns.

## Architecture Layers

### 1. Domain Layer (`src/domain/`)

**Purpose**: Contains business logic interfaces and domain models.

**Components**:
- `models.py`: Domain entities and DTOs (Document, Question, Answer, etc.)
- `interfaces.py`: Abstract interfaces defining contracts

**Principles**:
- No dependencies on other layers
- Pure business logic
- Framework-agnostic

### 2. Service Layer (`src/services/`)

**Purpose**: Implements business logic and orchestrates domain operations.

**Components**:
- `document_service.py`: Handles document processing
- `qa_service.py`: Handles question-answering

**Responsibilities**:
- Single Responsibility Principle: Each service has one clear purpose
- Orchestrates domain and infrastructure components
- Contains business rules and workflows

### 3. Infrastructure Layer (`src/infrastructure/`)

**Purpose**: External integrations and technical implementations.

**Components**:
- `loaders/`: Document loading implementations
- `vectorstores/`: Vector database implementations
- `llm/`: LLM provider clients
- `embeddings/`: Embedding service implementations

**Principles**:
- Implements domain interfaces
- Can be swapped without changing business logic
- Handles external API calls and technical details

### 4. Application Layer (`src/app/`)

**Purpose**: User interface and application entry point.

**Components**:
- `main.py`: Streamlit UI implementation

**Responsibilities**:
- User interaction
- Input validation
- Presentation logic
- Delegates to service layer

### 5. Core Layer (`src/core/`)

**Purpose**: Cross-cutting concerns.

**Components**:
- `config.py`: Configuration management
- `exceptions.py`: Custom exception hierarchy
- `logger.py`: Logging setup

## SOLID Principles

### Single Responsibility Principle (SRP)

Each class has one reason to change:
- `DocumentService`: Only handles document processing
- `QAService`: Only handles question-answering
- `PDFLoader`: Only loads PDF files
- `OpenAIClient`: Only interfaces with OpenAI API

### Open/Closed Principle (OCP)

Open for extension, closed for modification:
- New document loaders can be added without modifying existing code
- New vector stores can be added by implementing `IVectorStore`
- New LLM providers can be added by implementing `ILLMService`

### Liskov Substitution Principle (LSP)

Subtypes must be substitutable for their base types:
- All loaders can be used wherever `IDocumentLoader` is expected
- All vector stores can be used wherever `IVectorStore` is expected

### Interface Segregation Principle (ISP)

Clients shouldn't depend on interfaces they don't use:
- `IDocumentLoader` only has document loading methods
- `IEmbeddingService` only has embedding methods
- `ILLMService` only has text generation methods

### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions:
- Services depend on interfaces (`IDocumentLoader`, `IVectorStore`, etc.)
- Infrastructure implements these interfaces
- Easy to swap implementations

## Design Patterns

### Factory Pattern

`DocumentLoaderFactory` creates appropriate loaders based on file type:
- Extensible: Add new loaders without modifying factory logic
- Encapsulates object creation

### Strategy Pattern

Different implementations for:
- Document loaders (PDF, DOCX, etc.)
- Vector stores (FAISS, Pinecone, etc.)
- LLM providers (OpenAI, Anthropic, etc.)

### Service Layer Pattern

Business logic separated from:
- Infrastructure concerns
- UI concerns
- Data access concerns

### Repository Pattern

`IVectorStore` abstracts vector database operations:
- Can swap FAISS for other vector databases
- Business logic doesn't depend on specific implementation

## Dependency Flow

```
app (UI)
  ↓
services (Business Logic)
  ↓
domain (Interfaces)
  ↑
infrastructure (Implementations)
```

**Key Points**:
- UI depends on services
- Services depend on domain interfaces
- Infrastructure implements domain interfaces
- No circular dependencies

## Error Handling

Custom exception hierarchy:
- `DocumentQAAException`: Base exception
- `DocumentProcessingError`: Document processing failures
- `QAChainError`: QA chain failures
- `APIKeyError`: Configuration errors

Benefits:
- Clear error types
- Easy to handle specific errors
- Better error messages

## Configuration Management

`AppConfig` class:
- Centralized configuration
- Environment variable support
- Type-safe configuration
- Easy to extend

## Logging

Centralized logging:
- Consistent log format
- Configurable log levels
- Easy to add logging to new components

## Extension Points

### Adding New Document Format

1. Create loader in `src/infrastructure/loaders/`
2. Extend `BaseDocumentLoader`
3. Register in `DocumentLoaderFactory`
4. No changes needed elsewhere

### Adding New Vector Store

1. Create implementation in `src/infrastructure/vectorstores/`
2. Implement `IVectorStore` interface
3. Update `DocumentService` to use new store (or make it configurable)

### Adding New LLM Provider

1. Create client in `src/infrastructure/llm/`
2. Implement `ILLMService` interface
3. Update `QAService` to use new provider (or make it configurable)

## Testing Strategy

(To be implemented)
- Unit tests for services
- Integration tests for infrastructure
- Mock external dependencies
- Test interfaces, not implementations

## Performance Considerations

- Vector store caching
- Embedding batch processing
- Async operations (future improvement)
- Connection pooling (future improvement)

## Security Considerations

- API keys in environment variables
- Input validation
- File upload restrictions
- Error message sanitization

