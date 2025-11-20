# 🔍 Azure GenAI RAG Tutorial (Modules 0–3)

This tutorial walks you through building a Retrieval-Augmented Generation (RAG) pipeline using Azure OpenAI, Azure AI Search, and FastAPI.

---

## ✅ Module 0 — Environment Setup

### Tools Installed:
- Python 3.11+
- VS Code
- Azure CLI
- Azure Developer CLI (`azd`)
- Docker
- Git

### Azure Resources:
- Resource Group: `azure-genai`
- Region: `canadaeast`

### FastAPI App Setup:
- Folder: `api/`
- Virtualenv: `.venv/`
- Entry point: `api/main.py`
- Modules: `routers/`, `services/`, `utils/`
- Command: `python -m uvicorn api.main:app --reload`

---

## ✅ Module 1 — Python + Azure OpenAI

### What You Built:
- FastAPI backend with `/chat` endpoint
- AzureOpenAI client (`aoai_client.py`)
- `.env` with:
  ```env
  AZURE_OPENAI_ENDPOINT=https://canadaeast.api.cognitive.microsoft.com/
  AZURE_OPENAI_KEY=sk-xxxx
  AZURE_OPENAI_MODEL=gpt4o
  AZURE_OPENAI_API_VERSION=2024-08-01-preview
  ```

### Tested In:
- Swagger UI: `http://localhost:8000/docs`

---

## ✅ Module 2 — Embedding + Fine-Tuning

### What You Did:
- Deployed `text-embedding-ada-002` with version `2`
- Created `/embed` endpoint to return vector embeddings
- Created `embedding_client.py`

### .env updates:
```env
AZURE_EMBEDDINGS_MODEL=embedding-ada
```

---

## ✅ Module 3 — RAG with Azure AI Search

### What You Built:
- Vector-enabled Azure AI Search index (`docs-index`)
- Document chunking with `nltk`, `unstructured`
- Embedded and uploaded chunks to Search via `search_indexer.py`
- `/ask` endpoint to return GPT answer with document context

### .env additions:
```env
AZURE_SEARCH_SERVICE=genai-search
AZURE_SEARCH_KEY=your_key_here
AZURE_SEARCH_INDEX=docs-index
```

### File Structure Additions:
- `api/services/search_engine.py` – hybrid search logic
- `api/services/search_indexer.py` – document embedding/upload
- `api/routers/ask.py` – FastAPI endpoint for RAG query
- `api/utils/chunker.py` – chunking function
- `infrastructure/ai_search/index-schema.json` – index schema

---

## ✅ Commands Used

### Deploy GPT-4o
```bash
az cognitiveservices account deployment create \
  --deployment-name gpt4o \
  --model-name gpt-4o \
  --model-version 2024-11-20
```

### Deploy Embedding Model
```bash
az cognitiveservices account deployment create \
  --deployment-name embedding-ada \
  --model-name text-embedding-ada-002 \
  --model-version 2
```

### Create Azure AI Search Index
```bash
az search index create \
  --service-name genai-search \
  --resource-group azure-genai \
  --name docs-index \
  --body @infrastructure/ai_search/index-schema.json
```

---

## ✅ Requirements.txt Additions

```
pypdf
unstructured
nltk
azure-search-documents
openai
python-dotenv
fastapi
uvicorn
```

---

## Next Up: Module 4 — GraphRAG with Cosmos DB

You'll build a knowledge graph using:
- Cosmos DB Gremlin API
- Entity relationships
- Combined semantic + graph search