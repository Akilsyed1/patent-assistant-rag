# Patent Assistant RAG Application

This project provides a specialized chat interface for interacting with patent documents using Retrieval-Augmented Generation (RAG) technology. It consists of a FastAPI backend that handles patent document retrieval and LLM-based question answering, and a Flask frontend that provides a user-friendly chat interface for patent analysis and exploration.

## Project Structure

```
enterprise-rag-ui/
├── backend/               # FastAPI backend
│   ├── embeddings/        # Embedding generation
│   ├── ingestion/         # Document loading
│   ├── llm/               # LLM integration
│   ├── retriever/         # Vector search
│   └── main.py            # FastAPI app
├── frontend/              # Flask frontend
│   ├── static/            # Static assets
│   ├── templates/         # HTML templates
│   ├── app.py             # Flask app
│   └── requirements.txt   # Frontend dependencies
└── README.md              # This file
```

## Setup and Installation

### Backend Setup

1. Install backend dependencies:

```bash
cd enterprise-rag-ui
pip install -r requirements.txt
```

2. Run the FastAPI backend:

```bash
cd enterprise-rag-ui
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8003
```

### Frontend Setup

1. Install frontend dependencies:

```bash
cd enterprise-rag-ui/frontend
pip install -r requirements.txt
```

2. Run the Flask frontend:

```bash
cd enterprise-rag-ui/frontend
FLASK_APP=app.py FLASK_DEBUG=1 flask run --host=0.0.0.0 --port=5003
```

## Usage

1. Open your browser and navigate to `http://localhost:5003`
2. You'll see a chat interface where you can ask questions about patents
3. Upload patent documents using the "Upload Patent" button
4. Ask questions about patents, and the system will retrieve relevant context and provide answers
5. Analyze specific patents using the "Analyze Patent" button
6. View available documents using the "Show Documents" button

## Features

- Modern, responsive chat interface
- Real-time patent question answering
- Patent document upload and processing
- Patent analysis capabilities (general, novelty, claims)
- Document management and viewing
- Chat history persistence during the session
- Markdown rendering for formatted responses
- Clear history functionality
