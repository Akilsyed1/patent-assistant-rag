import os
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from backend.ingestion.load_docs import load_documents



# 1. Load text from PDFs
texts = load_documents()

# 2. Split the text into chunks (e.g. 1000 characters each)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

all_chunks = []
for text in texts:
    docs = splitter.split_text(text)
    # Wrap each chunk in a Document object (required by LangChain)
    all_chunks.extend([Document(page_content=chunk) for chunk in docs])

# 3. Create embedding model using Ollama (must be running locally)
embedding_model = OllamaEmbeddings(model="nomic-embed-text")

# 4. Create and store in Chroma vector DB
vectorstore = Chroma.from_documents(
    documents=all_chunks,
    embedding=embedding_model,
    persist_directory="chromadb"
)

# Save to disk
vectorstore.persist()

print("✅ Embeddings generated and stored in ChromaDB!")
for text in texts:
    docs = splitter.split_text(text)
    all_chunks.extend([Document(page_content=chunk) for chunk in docs])
    print(f"📄 Split document into {len(docs)} chunks")
    for i, chunk in enumerate(docs[:3]):  # Just show first 3 chunks
        print(f"\n🔹 Chunk {i+1}:\n{chunk[:300]}...\n")
