from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from routers import health, chess_analysis, knowledge
from utils.logging import get_logger

# Load environment variables from .env file for local development
load_dotenv()

logger = get_logger(__name__)

app = FastAPI(
    title="Chess.com Multi-Agent RAG API",
    description="Production-ready chess analysis using LangGraph multi-agent system with RAG",
    version="2.0.0"
)

# Permissive CORS for public use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(health.router, prefix="/api")
app.include_router(chess_analysis.router, prefix="/api")
app.include_router(knowledge.router)  # Already has /api/knowledge prefix

@app.on_event("startup")
async def startup_event():
    logger.info("Chess.com Multi-Agent RAG API starting up")
    
    # Initialize Qdrant connection
    from core.qdrant_client import is_qdrant_available
    qdrant_available = is_qdrant_available()
    logger.info(f"Qdrant vector database available: {qdrant_available}")
    
    # Log available features
    features = []
    if qdrant_available:
        features.append("RAG Knowledge Base")
    if os.getenv("OPENAI_API_KEY"):
        features.append("Multi-Agent System")
    if os.getenv("TAVILY_API_KEY"):
        features.append("Web Search")
    
    logger.info(f"Available features: {', '.join(features) if features else 'Basic chat only'}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Chess.com Multi-Agent RAG API shutting down")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 