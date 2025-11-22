## Building a Smarter RAG Pipeline on Azure: From FastAPI to GraphRAG

Retrieval-Augmented Generation (RAG) is already a game-changer for enterprise search, but what happens when you take it further—adding graphs, hybrid search, and full Azure deployment? In this article, I’ll walk you through the step-by-step journey of building a robust, low-cost GenAI-powered RAG system on Azure—from FastAPI to GraphRAG.

### 🧱 Module 0: Environment Setup
Before building anything, I set up a clean dev environment:
- Installed: Python 3.11, VS Code, Docker, Azure CLI, Azure Developer CLI
- Created a virtualenv and initialized a FastAPI project
- Set up a `.env` file to manage Azure credentials (OpenAI key, endpoint, model)

### ⚙️ Module 1: FastAPI + Azure OpenAI
Here, I built a REST API with FastAPI that connects to Azure OpenAI:
- `/chat` endpoint for conversational input
- AzureOpenAI client using the new SDK
- Logged and tested through Swagger UI

Key lesson: Use `AZURE_OPENAI_API_KEY` and regional endpoint (`canadaeast.api.cognitive.microsoft.com`) to authenticate correctly.

### 📐 Module 2: Embeddings and Fine-Tuning
To move beyond chat, I deployed an embedding model (`text-embedding-ada-002`) on Azure:
- Added `/embed` endpoint to convert text into vectors
- Added retry logic and secret management for production readiness

Bonus: Fine-tuning on Azure is currently limited to GPT-3.5. I skipped it in favor of RAG.

### 🔍 Module 3: Vector RAG with Azure AI Search
This is where the system started to become truly intelligent.

**Steps:**
1. Created an Azure AI Search service (basic tier)
2. Defined a vector-enabled index (`docs-index`) using `az rest` + REST API
3. Chunked markdown files with `nltk`
4. Embedded and uploaded them using `azure-search-documents`
5. Implemented a `/ask` endpoint for real-time RAG search

Hybrid search combines:
- `search_text` (keywords)
- `vector` (semantic match)

I uploaded a markdown file (`azure_genai_tutorial_modules_0_to_3.md`) and tested queries like "What does Module 1 cover?"

### 🧠 Module 4: GraphRAG with Cosmos DB
To improve context and relationships between concepts, I added GraphRAG:

**Steps:**
1. Created a Cosmos DB account with Gremlin API using CLI
2. Used SpaCy to extract named entities and build a graph
3. Created vertices and edges representing concepts and relationships
4. Inserted the graph into Cosmos DB using `gremlinpython`
5. Verified successful graph upload via `g.V().count()` and `g.V('Module 3').out('related_to')`

Benefits of GraphRAG:
- Understand not just what’s relevant, but *how* ideas connect
- Powerful when used with vector search
- Enables multi-hop reasoning in future agent-based pipelines

Final step: A `/graphask` endpoint combines:
- Graph-based expansion of query concepts
- RAG from nearby nodes
- GPT-4o generation with full context

### 🌐 Results
This setup enables:
- Accurate answers over private documents
- Structured exploration of topics
- Graph-enhanced semantic retrieval
- Easy hosting via FastAPI, deployable to Azure App Service or AKS

### ✅ Tools Used
- Azure OpenAI (GPT-4o, embeddings)
- Azure AI Search (vector index via REST)
- Cosmos DB (Gremlin graph)
- FastAPI, Python, SpaCy, GremlinPython, requests

### Final Thoughts
RAG is great. GraphRAG is better. And when you combine Azure-native tools like Cosmos DB and AI Search, you get a scalable, secure GenAI pipeline that feels like magic.

---

🗂️ [See the original tutorial file](sandbox:/mnt/data/azure_genai_tutorial_modules_0_to_3.md)

💬 Questions or want the repo? Reach out!

