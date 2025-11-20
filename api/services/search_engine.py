# api/services/search_engine.py
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from services.embedding_client import get_embedding

AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "docs-index")

search_client = SearchClient(
    endpoint=f"https://{AZURE_SEARCH_SERVICE}.search.windows.net/",
    index_name=AZURE_SEARCH_INDEX,
    credential=AzureKeyCredential(AZURE_SEARCH_KEY)
)

def search_docs(query):
    vector = get_embedding(query)
    results = search_client.search(
        search_text=query,
        vectors=[{
            "value": vector,
            "fields": "embedding",
            "k": 3
        }],
        top=3
    )
    return [r["content"] for r in results]
