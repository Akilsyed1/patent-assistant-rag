import sys
import os

# Add the project root (enterprise-rag-ui) to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Now import the module
from ask import answer_question

# Add a print to check if the script is running
print("✅ Running test_llm.py")

query= input("human: ")
# Test the function by asking a question
answer_question(query)