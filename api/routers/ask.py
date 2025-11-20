# api/routers/ask.py
from fastapi import APIRouter
from pydantic import BaseModel
from api.services.aoai_client import get_completion
from api.services.search_engine import search_docs

router = APIRouter()

class AskRequest(BaseModel):
    query: str

@router.post("/")
async def ask(req: AskRequest):
    docs = search_docs(req.query)
    context = "\n\n".join(docs)
    messages = [
        {"role": "system", "content": "Answer using the context below:\n\n" + context},
        {"role": "user", "content": req.query}
    ]
    reply = await get_completion(messages)
    return {"response": reply}
