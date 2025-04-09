# backend/main.py

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import shutil
from pathlib import Path
import glob

from llm.ask import answer_question
from ingestion.patent_ingestion import ingest_patents

# Define the request models
class QuestionRequest(BaseModel):
    question: str

class PatentAnalysisRequest(BaseModel):
    patent_number: Optional[str] = None
    text: Optional[str] = None
    analysis_type: str = "general"  # general, novelty, claims, etc.

# Create the FastAPI app
app = FastAPI(title="Patent Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, in production specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "chromadb"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Patent Assistant API"}

@app.post("/ask")
def ask(request: QuestionRequest):
    try:
        # Get the question from the request
        question = request.question
        
        # Import the is_patent_related function to check if the question is patent-related
        from llm.ask import is_patent_related
        
        # Check if the question is patent-related at the API level too
        if not is_patent_related(question):
            return {"answer": "I'm a specialized Patent Assistant and can only answer questions related to patents, intellectual property, or the patent application process. Please ask a question related to these topics."}
        
        # If the question is patent-related, proceed with the normal flow
        answer = answer_question(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patent-documents")
def get_patent_documents():
    """Get a list of all patent documents in the data directory"""
    try:
        # Get all files in the data directory with supported extensions
        files = []
        for ext in [".pdf", ".txt", ".docx"]:
            files.extend(glob.glob(str(DATA_DIR / f"*{ext}")))
        
        # Extract just the filenames
        documents = [os.path.basename(f) for f in files]
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-patent")
def upload_patent(file: UploadFile = File(...)):
    """Upload a patent document and ingest it into the vector database"""
    try:
        # Save the file
        file_path = DATA_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Ingest the patent into the vector database
        ingest_patents(str(DATA_DIR), str(DB_DIR))
        
        return {"message": f"Patent {file.filename} uploaded and ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-patent")
def analyze_patent(request: PatentAnalysisRequest):
    """Analyze a patent document"""
    try:
        # Construct a question based on the analysis type
        question = ""
        if request.analysis_type == "general":
            question = f"Provide a general analysis of patent {request.patent_number}"
        elif request.analysis_type == "novelty":
            question = f"Analyze the novelty aspects of patent {request.patent_number}"
        elif request.analysis_type == "claims":
            question = f"Analyze the claims of patent {request.patent_number}"
        else:
            question = f"Analyze patent {request.patent_number} focusing on {request.analysis_type}"
        
        # Use the existing question-answering function
        analysis = answer_question(question)
        
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
