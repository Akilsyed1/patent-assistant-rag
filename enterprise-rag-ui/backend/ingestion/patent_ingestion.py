"""
Patent Document Ingestion Pipeline

This module implements the document ingestion layer for the Patent Assistant RAG system.
It handles parsing, extraction, and indexing of patent documents from various formats.
"""

import os
import fitz  # PyMuPDF
from pathlib import Path
import re
from typing import List, Dict, Any, Optional
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PatentMetadata:
    """Class to store and extract patent metadata"""
    
    def __init__(self, text: str, filename: str):
        self.text = text
        self.filename = filename
        self.patent_number = self._extract_patent_number()
        self.title = self._extract_title()
        self.abstract = self._extract_abstract()
        self.claims = self._extract_claims()
        
    def _extract_patent_number(self) -> Optional[str]:
        """Extract patent number from text"""
        # Try to find patent number patterns like US11391262
        pattern = r'US\d{7,8}'
        match = re.search(pattern, self.filename)
        if match:
            return match.group(0)
        return None
        
    def _extract_title(self) -> str:
        """Extract patent title from text"""
        # Simple heuristic: Look for "Title:" or try to find title patterns
        title_match = re.search(r'Title[:\s]+([^\n]+)', self.text)
        if title_match:
            return title_match.group(1).strip()
        return "Unknown Title"
        
    def _extract_abstract(self) -> str:
        """Extract abstract from text"""
        abstract_match = re.search(r'Abstract[:\s]+(.+?)(?=\n\n|\n[A-Z]+:)', self.text, re.DOTALL)
        if abstract_match:
            return abstract_match.group(1).strip()
        return ""
        
    def _extract_claims(self) -> List[str]:
        """Extract claims from text"""
        claims_section = re.search(r'Claims[:\s]+(.*?)(?=\n\n[A-Z]+:|\Z)', self.text, re.DOTALL)
        if not claims_section:
            return []
            
        claims_text = claims_section.group(1)
        # Split by claim numbers
        claims = re.findall(r'\d+\.\s+(.*?)(?=\n\d+\.|\Z)', claims_text, re.DOTALL)
        return [claim.strip() for claim in claims]
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "patent_number": self.patent_number,
            "title": self.title,
            "abstract": self.abstract,
            "claims_count": len(self.claims),
            "filename": self.filename
        }


class PatentDocumentProcessor:
    """Process patent documents and extract text and metadata"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def process_pdf(self, file_path: str) -> Document:
        """Process a PDF file and extract text and metadata"""
        logger.info(f"Processing PDF: {file_path}")
        
        try:
            # Open the PDF
            doc = fitz.open(file_path)
            text = ""
            
            # Extract text from all pages
            for page in doc:
                text += page.get_text()
                
            # Create metadata
            filename = Path(file_path).name
            metadata = PatentMetadata(text, filename)
            
            # Create Document object
            return Document(
                page_content=text,
                metadata=metadata.to_dict()
            )
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            # Return empty document with error metadata
            return Document(
                page_content="",
                metadata={"error": str(e), "filename": Path(file_path).name}
            )
    
    def process_directory(self) -> List[Document]:
        """Process all patent documents in the data directory"""
        documents = []
        
        # Process PDF files
        for pdf_file in self.data_dir.glob("*.pdf"):
            doc = self.process_pdf(str(pdf_file))
            if doc.page_content:  # Only add if content was extracted
                documents.append(doc)
                
        logger.info(f"Processed {len(documents)} patent documents")
        return documents


class PatentVectorizer:
    """Convert patent documents to vector embeddings and store in vector database"""
    
    def __init__(self, embedding_model_name: str = "nomic-embed-text"):
        self.embedding_model = OllamaEmbeddings(model=embedding_model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
    def vectorize(self, documents: List[Document], persist_directory: str) -> Chroma:
        """Split documents into chunks, create embeddings, and store in vector database"""
        if not documents:
            logger.warning("No documents to vectorize")
            return None
            
        # Split documents into chunks
        logger.info(f"Splitting {len(documents)} documents into chunks")
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        
        # Create and persist the vector database
        logger.info(f"Creating vector database in {persist_directory}")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding_model,
            persist_directory=persist_directory
        )
        
        # Persist the database
        vectorstore.persist()
        logger.info(f"Vector database created with {len(chunks)} chunks")
        
        return vectorstore


def ingest_patents(data_dir: str, db_dir: str) -> None:
    """Main function to ingest patent documents"""
    logger.info(f"Starting patent document ingestion from {data_dir}")
    
    # Process documents
    processor = PatentDocumentProcessor(data_dir)
    documents = processor.process_directory()
    
    if not documents:
        logger.warning("No documents were processed successfully")
        return
    
    # Vectorize documents
    vectorizer = PatentVectorizer()
    vectorstore = vectorizer.vectorize(documents, db_dir)
    
    logger.info("Patent document ingestion complete")
    return vectorstore


if __name__ == "__main__":
    # Get data directory from command line or use default
    import argparse
    parser = argparse.ArgumentParser(description="Ingest patent documents into vector database")
    parser.add_argument("--data-dir", type=str, default="../data",
                        help="Directory containing patent documents")
    parser.add_argument("--db-dir", type=str, default="../chromadb",
                        help="Directory to store vector database")
    args = parser.parse_args()
    
    # Convert relative paths to absolute
    base_dir = Path(__file__).parent.parent.parent
    data_dir = str(base_dir / args.data_dir)
    db_dir = str(base_dir / args.db_dir)
    
    # Ingest patents
    ingest_patents(data_dir, db_dir)
