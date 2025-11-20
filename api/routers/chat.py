from fastapi import APIRouter
from pydantic import BaseModel
from api.services.aoai_client import get_completion

router = APIRouter()

class ChatRequest(BaseModel):
    user_input: str

@router.post("/")
async def chat(req: ChatRequest):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": req.user_input}
    ]
    try:
        reply = await get_completion(messages)
        return {"response": reply}
    except Exception as e:
        return {"error": str(e)}
