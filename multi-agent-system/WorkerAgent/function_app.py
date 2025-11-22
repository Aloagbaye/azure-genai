import azure.functions as func
import logging
import os
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import json

load_dotenv()

app = func.FunctionApp()

# Azure OpenAI client
aoai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Azure AI Search client
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)

@app.route(route="worker", auth_level=func.AuthLevel.FUNCTION)
def worker_agent(req: func.HttpRequest) -> func.HttpResponse:
    """
    Worker Agent: Retrieves information using RAG
    """
    logging.info('Worker Agent triggered')
    
    try:
        req_body = req.get_json()
        query = req_body.get('query', '')
        
        if not query:
            return func.HttpResponse(
                "Query is required",
                status_code=400
            )
        
        # Perform RAG search
        results = search_client.search(
            search_text=query,
            top=5,
            include_total_count=True
        )
        
        # Extract relevant documents
        documents = []
        for result in results:
            documents.append({
                "content": result.get("content", ""),
                "title": result.get("title", ""),
                "score": result.get("@search.score", 0)
            })
        
        # Generate embedding for query
        embedding_response = aoai_client.embeddings.create(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            input=query
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Vector search (if using vector fields)
        try:
            vector_results = search_client.search(
                search_text="",
                vector_queries=[{
                    "vector": query_embedding,
                    "k_nearest_neighbors": 3,
                    "fields": "embedding"
                }],
                top=3
            )
            
            # Combine results
            all_docs = list(documents)
            for result in vector_results:
                all_docs.append({
                    "content": result.get("content", ""),
                    "title": result.get("title", ""),
                    "score": result.get("@search.score", 0)
                })
        except Exception as e:
            # If vector search fails, use text search results only
            logging.warning(f"Vector search failed: {e}, using text search results only")
            all_docs = documents
        
        # Summarize findings
        context = "\n\n".join([doc["content"] for doc in all_docs[:5]])
        
        summary_response = aoai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a research assistant. Summarize the retrieved information to answer the query."
                },
                {
                    "role": "user",
                    "content": f"Query: {query}\n\nContext:\n{context}\n\nProvide a concise answer based on the context."
                }
            ],
            temperature=0.3
        )
        
        answer = summary_response.choices[0].message.content
        
        return func.HttpResponse(
            json.dumps({
                "query": query,
                "answer": answer,
                "sources": all_docs[:5],
                "source_count": len(all_docs)
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Error in worker agent: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

