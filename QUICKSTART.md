# Quick Start Guide

## Step 1: Install Dependencies

```bash
python3.11 -m venv .venv311
source .venv311/bin/activate
pip install -r requirements.txt
```

## Step 2: Choose Model Provider

For OpenAI, create a `.env` file in the project root and add:

```
OPENAI_API_KEY=your_actual_api_key_here
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
```

Or you can enter it directly in the Streamlit app sidebar.

For local Ollama, start Ollama and pull the recommended models:

```bash
ollama serve
ollama pull phi3
ollama pull nomic-embed-text
```

Then use these settings in the Streamlit sidebar:

```text
Answer Model Provider = Ollama
Ollama Answer Model = phi3
Embedding Provider = Ollama
Ollama Embedding Model = nomic-embed-text
Ollama Base URL = http://127.0.0.1:11434
```

## Step 3: Run the Application

```bash
streamlit run app.py
```

## Step 4: Use the App

1. Open the browser (usually `http://localhost:8501`)
2. Select `Documents` or `YouTube` in the sidebar
3. Select OpenAI or Ollama model providers in the sidebar
4. Go to "Upload / Source" tab
5. Upload PDF files or provide a YouTube URL
6. Click the processing button
7. Switch to "Ask Questions" tab
8. Start asking questions!

## Troubleshooting

- **Import errors**: Make sure all packages are installed: `pip install -r requirements.txt`
- **API key errors**: Verify your OpenAI API key is correct and has credits; it is only required when using OpenAI for answers or embeddings
- **Ollama errors**: Verify Ollama is running on `http://127.0.0.1:11434` and the selected models are pulled
- **PDF errors**: Ensure your PDF files are valid and not corrupted
