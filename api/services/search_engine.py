import os
import requests
from api.services.embedding_client import get_embedding

def search_docs(query):
    search_service = os.getenv("AZURE_SEARCH_SERVICE")
    index_name = os.getenv("AZURE_SEARCH_INDEX")
    api_key = os.getenv("AZURE_SEARCH_KEY")
    api_version = "2023-11-01"

    embedding = get_embedding(query)

    # Corrected URL - use /docs/search endpoint
    url = f"https://{search_service}.search.windows.net/indexes/{index_name}/docs/search?api-version={api_version}"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    body = {
        "search": query,
        "vectorQueries": [
            {
                "vector": embedding,
                "fields": "embedding",
                "kind": "vector",
                "k": 3
            }
        ],
        "top": 3
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    results = response.json()

    return [hit["content"] for hit in results.get("value", [])]