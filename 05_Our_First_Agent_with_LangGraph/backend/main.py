from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from routers import health, chess_analysis
from utils.logging import get_logger

# Load environment variables from .env file for local development
load_dotenv()

logger = get_logger(__name__)

app = FastAPI(
    title="Chess.com LangGraph Agent API",
    description="Production-ready chess analysis using LangGraph multi-agent system",
    version="1.0.0"
)

# Permissive CORS for public use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(chess_analysis.router, prefix="/analyze")

@app.on_event("startup")
async def startup_event():
    logger.info("Chess.com LangGraph Agent API starting up")
    # Log Qdrant availability for debugging
    qdrant_available = bool(os.getenv("QDRANT_API_KEY"))
    logger.info(f"Qdrant integration available: {qdrant_available}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Chess.com LangGraph Agent API shutting down")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 