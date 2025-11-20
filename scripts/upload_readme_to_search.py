import os
from dotenv import load_dotenv
# Load env vars
load_dotenv()

from api.services.search_indexer import index_document


# Load the uploaded markdown file
with open("azure_genai_tutorial_modules_0_to_3.md", "r", encoding="utf-8") as f:
    text = f.read()

# Index the document
index_document(text, title="Azure GenAI Tutorial")
print("✅ Uploaded to Azure AI Search!")
