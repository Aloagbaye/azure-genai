import os
import asyncio
import threading
from fastapi import APIRouter
from pydantic import BaseModel
from api.services.aoai_client import get_completion
from gremlin_python.driver import client, serializer
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class GraphAskRequest(BaseModel):
    query: str

# Thread-local storage for gremlin clients to avoid event loop conflicts
_thread_local = threading.local()

# Shared thread pool executor for reusing threads
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="gremlin")

def get_gremlin_client():
    """Get or create a thread-local gremlin client"""
    if not hasattr(_thread_local, 'gremlin_client'):
        _thread_local.gremlin_client = client.Client(
            "wss://genai-graph.gremlin.cosmos.azure.com:443/",
            "g",
            username=f"/dbs/{os.getenv('COSMOS_DATABASE')}/colls/{os.getenv('COSMOS_GRAPH')}",
            password=os.getenv("COSMOS_KEY"),
            message_serializer=serializer.GraphSONSerializersV2d0()
        )
    return _thread_local.gremlin_client

def _expand_query_sync(query: str):
    try:
        gremlin = get_gremlin_client()
        related = gremlin.submit(f"g.V('{query}').out('related_to').values('id')").all().result()
        return list(set(related)) + [query]
    except Exception as e:
        print("🔴 Graph query failed:", e)
        return [query]

async def expand_query_with_graph(query: str) -> list[str]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _expand_query_sync, query)

@router.post("/")
async def graphask(req: GraphAskRequest):
    concepts = await expand_query_with_graph(req.query)
    context = "\n\n".join(concepts)
    messages = [
        {"role": "system", "content": f"Use the concepts below to help answer the question:\n\n{context}"},
        {"role": "user", "content": req.query}
    ]
    reply = await get_completion(messages)
    return {"response": reply, "concepts_used": concepts}