from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.routers import health, chess_analysis
from backend.utils.logging import get_logger

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

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Chess.com LangGraph Agent API shutting down")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 