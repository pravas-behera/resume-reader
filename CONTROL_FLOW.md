# Control Flow

This document explains how control moves through the app when a user provides a PDF document or a YouTube link and asks a question.

## Entry Points

| Entry point | File | Purpose |
| --- | --- | --- |
| Streamlit UI | `app.py` -> `src/app/main.py` | Browser UI for selecting a source, processing it, and asking questions |
| FastAPI API | `src/controllers/ask_api.py` | HTTP endpoints for one-shot document or YouTube Q&A |

Both entry points use the same service-level pipeline:

```text
source input
  -> processing service
  -> text chunks
  -> OpenAI embeddings
  -> FAISS vector store
  -> QA service
  -> retrieval QA chain
  -> OpenAI chat model
  -> answer
```

## Streamlit Control Flow

`app.py` imports and calls `main()` from `src/app/main.py`.

```text
app.py
  -> src.app.main.main()
      -> initialize_session_state()
      -> render_sidebar()
      -> render_upload_tab()
      -> render_qa_tab()
```

### 1. App Initialization

`initialize_session_state()` prepares the state that Streamlit keeps between reruns:

| Session key | Purpose |
| --- | --- |
| `document_service` | Current `DocumentService` instance for uploaded PDFs |
| `youtube_service` | Current `YouTubeService` instance for a processed video |
| `qa_service` | Current `QAService` instance connected to the latest vector store |
| `documents_loaded` | Boolean gate that enables the question tab |
| `config` | Current `AppConfig` |
| `messages` | Chat history rendered in the question tab |
| `feature` | Selected source type: `Documents` or `YouTube` |

`render_sidebar()` collects the OpenAI API key, model name, temperature, and source type.

### 2. Document Processing Flow

When the source is `Documents`, the user uploads one or more PDF files and clicks `Process Documents`.

```mermaid
sequenceDiagram
    participant User
    participant UI as src/app/main.py
    participant DS as DocumentService
    participant Factory as DocumentLoaderFactory
    participant Loader as PDFLoader
    participant Splitter as RecursiveTextSplitter
    participant Embed as OpenAIEmbeddingService
    participant Store as FAISSVectorStore
    participant QA as QAService

    User->>UI: Upload PDFs and click Process Documents
    UI->>UI: get_config_from_ui()
    UI->>DS: process_documents(uploaded_files)
    DS->>DS: Save each upload to a temp .pdf
    DS->>Factory: get_loader(tmp_path)
    Factory-->>DS: PDFLoader
    DS->>Loader: load(tmp_path)
    Loader-->>DS: Document objects
    DS->>Splitter: split_documents(documents)
    Splitter-->>DS: DocumentChunk list
    DS->>Embed: embed_documents(chunk_texts)
    Embed-->>DS: embedding vectors
    DS->>Store: add_documents(chunks, embeddings)
    Store-->>DS: populated vector store
    DS-->>UI: vector store
    UI->>QA: QAService(vectorstore, config)
    UI->>UI: Save services and mark documents_loaded = true
```
![alt text](image.png)

Key files:

| Step | File |
| --- | --- |
| UI event handling | `src/app/main.py` |
| PDF processing orchestration | `src/services/document_service.py` |
| Loader selection | `src/infrastructure/loaders/loader_factory.py` |
| PDF loading | `src/infrastructure/loaders/pdf_loader.py` |
| Chunking | `src/utils/text_splitter.py` |
| Embeddings | `src/infrastructure/embeddings/openai_embeddings.py` |
| Vector storage | `src/infrastructure/vectorstores/faiss_store.py` |

### 3. YouTube Processing Flow

When the source is `YouTube`, the user provides a video URL and clicks `Process YouTube`.

```mermaid
sequenceDiagram
    participant User
    participant UI as src/app/main.py
    participant YT as YouTubeService
    participant Utils as youtube_transcript utils
    participant Splitter as RecursiveTextSplitter
    participant Embed as OpenAIEmbeddingService
    participant Store as FAISSVectorStore
    participant QA as QAService

    User->>UI: Enter YouTube URL and click Process YouTube
    UI->>UI: get_config_from_ui()
    UI->>YT: process_video(youtube_url)
    YT->>Utils: extract_video_id(url)
    YT->>Utils: fetch_transcript_text(video_id)
    Utils-->>YT: transcript text
    YT->>YT: Wrap transcript in Document
    YT->>Splitter: split_documents([doc])
    Splitter-->>YT: DocumentChunk list
    YT->>Embed: embed_documents(chunk_texts)
    Embed-->>YT: embedding vectors
    YT->>Store: add_documents(chunks, embeddings)
    Store-->>YT: populated vector store
    YT-->>UI: vector store
    UI->>QA: QAService(vectorstore, config)
    UI->>UI: Save services and mark documents_loaded = true
```

Key files:

| Step | File |
| --- | --- |
| UI event handling | `src/app/main.py` |
| YouTube processing orchestration | `src/services/youtube_service.py` |
| Video ID and transcript fetching | `src/utils/youtube_transcript.py` |
| Chunking | `src/utils/text_splitter.py` |
| Embeddings | `src/infrastructure/embeddings/openai_embeddings.py` |
| Vector storage | `src/infrastructure/vectorstores/faiss_store.py` |

### 4. Question Answering Flow

After either source is processed, the UI stores a `QAService` in `st.session_state.qa_service`.

When the user asks a question:

```mermaid
sequenceDiagram
    participant User
    participant UI as src/app/main.py
    participant QA as QAService
    participant Retriever as FAISS retriever
    participant LLM as OpenAIClient / ChatOpenAI

    User->>UI: Submit question
    UI->>UI: Append user ChatMessage
    UI->>QA: ask_question_text(question_text)
    QA->>QA: Build Question domain object
    QA->>QA: ask_question(question)
    QA->>Retriever: Retrieve top-k relevant chunks
    Retriever-->>QA: source documents
    QA->>LLM: Send prompt with context and question
    LLM-->>QA: answer text
    QA-->>UI: answer text
    UI->>UI: Append assistant ChatMessage
    UI-->>User: Render answer
```

Important details:

| Detail | Behavior |
| --- | --- |
| Retriever size | `config.retrieval_config.k`, default `3` |
| Prompt location | `src/services/qa_service.py` |
| Prompt style | Uses retrieved context, says "I don't know" when answer is unavailable, and keeps the answer concise |
| Chat state | Stored only in Streamlit session state |
| Vector store persistence | In memory only for the current processed source/session |

## FastAPI Control Flow

The API app lives in `src/controllers/ask_api.py`.

At import/startup time:

```text
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
config = AppConfig.from_env(api_key=api_key)
doc_service = DocumentService(config)
```

### `POST /document/ask`

This is a one-shot flow: each request uploads a file, builds a vector store, creates a QA service, answers the question, and returns JSON.

```text
HTTP multipart form:
  file=<uploaded PDF>
  question=<question text>

ask_question()
  -> await file.read()
  -> wrap bytes in BytesIO and set file_like.name
  -> doc_service.process_documents([file_like])
  -> QAService(vectorstore, config)
  -> qa_service.ask_question_text(question)
  -> return {"answer": answer}
```

### `POST /youtube/ask`

This is also a one-shot flow: each request fetches the transcript, builds a vector store, creates a QA service, answers the question, and returns JSON.

```text
HTTP multipart form:
  url=<YouTube URL>
  question=<question text>

youtube_ask()
  -> validate url is not empty
  -> YouTubeService(config)
  -> yt_service.process_video(url)
  -> QAService(vectorstore, config)
  -> qa_service.ask_question_text(question)
  -> return {"answer": answer}
```

## Service Responsibilities

| Component | Responsibility |
| --- | --- |
| `DocumentService` | Turn uploaded PDF files into a FAISS vector store |
| `YouTubeService` | Turn a YouTube transcript into a FAISS vector store |
| `QAService` | Turn a question plus vector store into an answer |
| `OpenAIEmbeddingService` | Generate embeddings for chunks |
| `OpenAIClient` | Wrap the OpenAI chat model for answer generation |
| `FAISSVectorStore` | Hold chunk vectors and expose LangChain's retriever interface |
| `RecursiveTextSplitter` | Convert `Document` objects into overlapping `DocumentChunk` objects |

## Error Flow

The main custom exceptions are defined in `src/core/exceptions.py`.

| Error | Typical source |
| --- | --- |
| `APIKeyError` | Missing OpenAI API key while initializing services |
| `ConfigurationError` | UI configuration creation failure |
| `DocumentProcessingError` | Failed PDF loading, transcript fetching, chunking, embedding, or vector store creation |
| `QAChainError` | Failed QA chain setup or answer generation |
| `VectorStoreError` | Empty or failing FAISS vector store |

In Streamlit, these errors are caught in `src/app/main.py` and displayed with `st.error()`.

In FastAPI, errors are caught in `src/controllers/ask_api.py` and converted to `HTTPException` responses.

## Current Runtime Characteristics

| Area | Current behavior |
| --- | --- |
| State | Streamlit keeps state in `st.session_state`; FastAPI rebuilds per request |
| Persistence | Vector stores are not saved to disk |
| Supported documents | PDF only |
| Supported YouTube transcripts | English transcript lookup in `src/utils/youtube_transcript.py` |
| External services | OpenAI for embeddings and chat completion; YouTube transcript API for transcripts |
| Retrieval implementation | `QAService` uses LangChain `RetrievalQA` with `vectorstore.as_retriever()` |
