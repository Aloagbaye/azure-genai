from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api.routers.chat import router as chat_router
from api.routers.embed import router as embed_router
from api.routers.ask import router as ask_router
from api.routers.graphask import router as graphask_router

app = FastAPI(title="GenAI API", version="1.0.0")

# Configure CORS to allow Streamlit to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(embed_router, prefix="/embed", tags=["Embedding"])
app.include_router(ask_router, prefix="/ask", tags=["Ask"])
app.include_router(graphask_router, prefix="/graphask", tags=["GraphRAG"])

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "GenAI API"}
    )

@app.get("/")
async def root():
    return {"message": "Azure GenAI API", "version": "1.0.0"}
