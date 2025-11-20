# api/services/search_indexer.py
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from api.services.embedding_client import get_embedding
from api.utils.chunker import prepare_documents
import os

AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE")
AZURE_SEARCH_INDEX = "docs-index"

search_client = SearchClient(
    endpoint=f"https://{AZURE_SEARCH_SERVICE}.search.windows.net/",
    index_name=AZURE_SEARCH_INDEX,
    credential=AzureKeyCredential(AZURE_SEARCH_KEY)
)

def index_document(text, title):
    docs = prepare_documents(text, title)
    for doc in docs:
        doc["embedding"] = get_embedding(doc["content"])
    search_client.upload_documents(docs)
