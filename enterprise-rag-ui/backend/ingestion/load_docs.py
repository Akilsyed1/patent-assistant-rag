# backend/ingestion/load_docs.py

import os
from PyPDF2 import PdfReader

def load_documents(data_folder="data"):
    all_text = []

    # Look through each file in the data folder
    for filename in os.listdir(data_folder):
        if filename.endswith(".pdf"):
            filepath = os.path.join(data_folder, filename)
            print(f"Reading: {filepath}")
            
            reader = PdfReader(filepath)
            text = ""

            # Loop through each page and extract text
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            all_text.append(text.strip())

    return all_text
