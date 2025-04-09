from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

embedding_model = OllamaEmbeddings(model="nomic-embed-text")

vectorstore = Chroma(
    persist_directory="chromadb",
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

def retrieve_context(question: str):
    results = retriever.get_relevant_documents(question)
    
    print(f"\n🔍 Question: {question}")
    print("\n📎 Top Matching Chunks:\n")
    for i, doc in enumerate(results):
        print(f"--- Chunk {i+1} ---")
        print(doc.page_content[:500])  # print first 500 characters
        print("\n")

    return results
