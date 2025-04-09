from retriever.search import retrieve_context
from langchain_community.llms import Ollama
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import re

load_dotenv()
# 1. Load the local LLM from Ollama
llm = ChatGroq(model="llama3-70b-8192")  # You can change to "llama2", "llama3", etc.

# 2. Custom prompt to guide LLM
prompt_template = PromptTemplate.from_template("""
You are a specialized Patent Assistant with expertise in patent writing, analysis, and the patent application process. 

Your capabilities include:
- Helping users draft patent claims and descriptions
- Analyzing patent documents for novelty and patentability
- Providing guidance on patent application processes
- Explaining patent terminology and concepts
- Offering insights on patent strategy

IMPORTANT INSTRUCTIONS:
1. You MUST ONLY answer questions related to patents, intellectual property, or the patent application process.
2. If the question is not related to patents or intellectual property, you MUST refuse to answer and explain that you are a specialized Patent Assistant.
3. Do not provide information on topics unrelated to patents, even if you know the answer.
4. If the context doesn't contain relevant information to answer a patent-related question, state that you don't have enough information, but still try to provide general patent guidance if possible.

Use the following context from patent documents to answer the question thoroughly and accurately. 
If the question is about writing a patent, provide clear, structured guidance with examples where appropriate.

Context:
{context}

Question:
{question}

Answer:""")

# 3. Chain: combine retriever + LLM + prompt
qa_chain = load_qa_chain(llm=llm, chain_type="stuff", prompt=prompt_template)

# Patent-related keywords for filtering questions
PATENT_KEYWORDS = [
    'patent', 'intellectual property', 'ip', 'invention', 'inventor', 'claim', 
    'prior art', 'novelty', 'non-obvious', 'utility', 'provisional', 'pct', 
    'uspto', 'epo', 'wipo', 'trademark', 'copyright', 'trade secret', 
    'infringement', 'licensing', 'royalty', 'assignee', 'assignor', 'filing', 
    'examination', 'prosecution', 'office action', 'rejection', 'allowance',
    'grant', 'issue', 'maintenance', 'term', 'expiration', 'invalidation',
    'reexamination', 'continuation', 'divisional', 'cip', 'rce', 'ipr', 'pgr',
    'interference', 'opposition', 'appeal', 'litigation', 'injunction', 'damages'
]

def is_patent_related(question):
    """Check if a question is related to patents or intellectual property"""
    # Convert to lowercase for case-insensitive matching
    question_lower = question.lower()
    
    # Check for patent-related keywords
    for keyword in PATENT_KEYWORDS:
        if keyword in question_lower:
            return True
    
    # Use regex to catch more complex patterns
    patent_patterns = [
        r'\b[a-z]{2}\d{6,}\b',  # Basic patent number pattern (e.g., US7654321)
        r'\b\d{2}/\d{3},\d{3}\b',  # Application number format
        r'\b35 U\.?S\.?C\.?\b',  # US patent law reference
        r'\bpatentable\b',
        r'\binvent\w*\b'
    ]
    
    for pattern in patent_patterns:
        if re.search(pattern, question_lower):
            return True
    
    return False

# 4. Function to answer the question
def answer_question(question):
    print(f"🔍 Asking question: {question}")  # Debugging line
    
    # Check if the question is patent-related
    if not is_patent_related(question):
        print("❌ Question is not related to patents")
        return "I'm a specialized Patent Assistant and can only answer questions related to patents, intellectual property, or the patent application process. Please ask a question related to these topics."
    
    # Retrieve relevant documents
    docs = retrieve_context(question)
    print(f"📚 Retrieved {len(docs)} documents")  # Debugging line
    
    # If no relevant documents found but question is patent-related,
    # still try to answer with general patent knowledge
    answer = qa_chain.run(input_documents=docs, question=question)
    
    print("\n🧠 Final Answer:\n")
    print(answer)  # This will show the final answer
    return answer

