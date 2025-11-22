
# ✅ Module 7 — Real-Time Graph-RAG Question Answering with Cosmos DB

## 📌 Objective:
Enable users to **ask questions** about your documentation, using **GraphRAG** for multi-hop reasoning with context expansion powered by Cosmos DB and GPT‑4o.

---

## 🧠 What You’ll Build:
- `/graphask` endpoint in FastAPI
- Graph query expansion (e.g., follow related nodes like `"Module 3" → "Vector Search"`)
- Combine expanded concepts with vector RAG from Azure AI Search
- Generate final GPT answer

---

## 🧱 Prerequisites:
- Cosmos DB graph populated with nodes and `related_to` edges (see Module 4)
- Working `/ask` endpoint with AI Search (Module 3)
- Installed: `gremlinpython`, `azure-search-documents`, `spacy`, etc.
- `.env` contains:
  ```env
  COSMOS_GREMLIN_ENDPOINT=wss://your-db.gremlin.cosmos.azure.com:443/
  COSMOS_GREMLIN_KEY=your_key
  COSMOS_GRAPH_NAME=tutorialgraph
  ```

---

## 🧩 Step-by-Step

### 1. **Create Graph Client** (`api/services/graph_client.py`)
```python
from gremlin_python.driver import client, serializer
import os

def get_graph_client():
    return client.Client(
        os.environ["COSMOS_GREMLIN_ENDPOINT"],
        "g",
        username=f"/dbs/knowledge/colls/{os.environ['COSMOS_GRAPH_NAME']}",
        password=os.environ["COSMOS_GREMLIN_KEY"],
        message_serializer=serializer.GraphSONSerializersV2d0()
    )
```

### 2. **Query Related Concepts** (`graph_expander.py`)
```python
def expand_graph_concepts(graph_client, concept):
    query = f"g.V('{concept}').out('related_to').values('id')"
    result = graph_client.submit(query).all().result()
    return [concept] + result
```

### 3. **RAG Search on Expanded Concepts** (`api/routers/graphask.py`)
```python
from fastapi import APIRouter
from services.search_engine import hybrid_search
from services.graph_client import get_graph_client
from utils.openai_client import gpt_answer

router = APIRouter()

@router.post("/graphask/")
async def graphask(query: str):
    graph = get_graph_client()
    concepts = expand_graph_concepts(graph, query)

    combined_context = ""
    for c in concepts:
        context = hybrid_search(c)
        combined_context += context + "\n"

    response = gpt_answer(query, combined_context)
    return {"response": response, "concepts_used": concepts}
```

### 4. **Test It**
Spin up your server:
```bash
uvicorn api.main:app --reload
```

Go to: `http://localhost:8000/docs`, try:
```json
POST /graphask/
{
  "query": "Module 4"
}
```

---

## 🧪 Output Example
```json
{
  "response": "Module 4 introduces GraphRAG using Cosmos DB...",
  "concepts_used": ["Module 4", "Cosmos DB", "GraphRAG"]
}
```

---

## ✅ Summary

Module 7 enables your app to reason across concept graphs + vector embeddings for **smarter answers**. This unlocks true **multi-hop question answering** over your private docs.

Up next? **Module 8: Agentic Orchestration** with LangChain or semantic memory!
