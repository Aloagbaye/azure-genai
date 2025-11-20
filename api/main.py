from fastapi import FastAPI
from api.routers.chat import router as chat_router
from api.routers.embed import router as embed_router
from api.routers.ask import router as ask_router





app = FastAPI(title="GenAI API")

app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(embed_router, prefix="/embed", tags=["Embedding"])
app.include_router(ask_router, prefix="/ask", tags=["Ask"])
