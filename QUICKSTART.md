# Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up API Key

Create a `.env` file in the project root and add:

```
OPENAI_API_KEY=your_actual_api_key_here
```

Or you can enter it directly in the Streamlit app sidebar.

## Step 3: Run the Application

```bash
streamlit run app.py
```

## Step 4: Use the App

1. Open the browser (usually `http://localhost:8501`)
2. Go to "Upload Documents" tab
3. Upload PDF files
4. Click "Process Documents"
5. Switch to "Ask Questions" tab
6. Start asking questions!

## Troubleshooting

- **Import errors**: Make sure all packages are installed: `pip install -r requirements.txt`
- **API key errors**: Verify your OpenAI API key is correct and has credits
- **PDF errors**: Ensure your PDF files are valid and not corrupted

