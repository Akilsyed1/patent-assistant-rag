"""
Script to ingest sample data into the ChromaDB vector database for testing.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the path to allow importing from backend
sys.path.append(str(Path(__file__).parent.parent.parent))

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# Create sample data directory if it doesn't exist
sample_data_dir = Path(__file__).parent / "sample_data"
sample_data_dir.mkdir(exist_ok=True)

# Create sample text files with patent information
sample_texts = [
    {
        "filename": "patent1.txt",
        "content": """
        Patent Title: Method and System for Natural Language Processing
        
        Abstract:
        A method and system for natural language processing that uses machine learning techniques to understand and generate human language. The system includes a neural network trained on large text corpora to recognize patterns in language and generate contextually appropriate responses.
        
        Background:
        Natural language processing (NLP) is a field of artificial intelligence that focuses on the interaction between computers and humans through natural language. The ultimate objective of NLP is to read, decipher, understand, and make sense of human languages in a valuable way.
        
        Description:
        The system comprises a multi-layer neural network architecture with attention mechanisms that allow it to focus on relevant parts of input text when generating responses. The system is trained using a combination of supervised and unsupervised learning techniques on diverse text datasets.
        """
    },
    {
        "filename": "patent2.txt",
        "content": """
        Patent Title: Improved Vector Database for Information Retrieval
        
        Abstract:
        An improved vector database system for efficient storage and retrieval of high-dimensional vector embeddings. The system uses novel indexing structures to enable fast similarity search across billions of vectors with minimal memory footprint.
        
        Background:
        Vector databases are specialized database systems designed to store and query high-dimensional vector embeddings. These embeddings are commonly used in machine learning applications, particularly for semantic search and recommendation systems.
        
        Description:
        The improved vector database uses a hierarchical navigable small world (HNSW) graph structure combined with product quantization to enable efficient approximate nearest neighbor search. The system includes a distributed architecture that allows horizontal scaling across multiple nodes while maintaining query performance.
        """
    },
    {
        "filename": "patent3.txt",
        "content": """
        Patent Title: Retrieval-Augmented Generation for Knowledge-Intensive Tasks
        
        Abstract:
        A system and method for retrieval-augmented generation (RAG) that enhances large language model outputs with relevant information retrieved from external knowledge sources. The system improves factual accuracy and reduces hallucinations in AI-generated content.
        
        Background:
        Large language models (LLMs) have demonstrated impressive capabilities in generating human-like text. However, they often produce factually incorrect information or "hallucinations" when dealing with knowledge-intensive tasks that require specific information not captured in their parameters.
        
        Description:
        The RAG system comprises three main components: (1) a retriever that identifies relevant documents from a knowledge corpus based on the input query, (2) an encoder that converts the retrieved documents into a format suitable for the language model, and (3) a generator that produces the final output by conditioning on both the input query and the retrieved information.
        """
    }
]

# Write sample texts to files
for sample in sample_texts:
    with open(sample_data_dir / sample["filename"], "w") as f:
        f.write(sample["content"])

def ingest_documents():
    """Load documents, split into chunks, and store in the vector database."""
    # Load documents
    documents = []
    for file_path in sample_data_dir.glob("*.txt"):
        loader = TextLoader(str(file_path))
        documents.extend(loader.load())
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    
    print(f"Split {len(documents)} documents into {len(chunks)} chunks")
    
    # Create embeddings
    embedding_model = OllamaEmbeddings(model="nomic-embed-text")
    
    # Create and persist the vector database
    db_path = Path(__file__).parent.parent.parent / "chromadb"
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=str(db_path)
    )
    
    # Persist the database
    vectorstore.persist()
    print(f"Ingested {len(chunks)} chunks into ChromaDB at {db_path}")
    
    return vectorstore

if __name__ == "__main__":
    print("Ingesting sample documents into ChromaDB...")
    ingest_documents()
    print("Ingestion complete!")
