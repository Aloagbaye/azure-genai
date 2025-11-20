from fastapi import APIRouter
from pydantic import BaseModel
from api.services.embedding_client import get_embedding

router = APIRouter()

class EmbedRequest(BaseModel):
    text: str

@router.post("/")
def embed_text(req: EmbedRequest):
    vector = get_embedding(req.text)
    return {"embedding": vector}
