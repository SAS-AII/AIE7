"""
Chess analysis router with multi-agent support
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from agents.multi_agent_graph import chess_multi_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["chess-analysis"])

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    state: Optional[Dict[str, Any]] = {}
    openai_key: str
    langsmith_key: Optional[str] = None
    tavily_key: Optional[str] = None
    qdrant_api_key: Optional[str] = None
    qdrant_url: Optional[str] = "http://localhost:6333"

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    agent_used: str
    rag_sources: int
    conversation_state: Dict[str, Any]

@router.post("/chat", response_model=ChatResponse)
async def chat_with_chess_agent(request: ChatRequest):
    """
    Chat with the chess multi-agent system
    
    This endpoint routes queries to appropriate specialist agents:
    - RAG agent for chess knowledge from the knowledge base
    - Chess.com agent for player analysis and game data
    """
    try:
        # Validate required API key
        if not request.openai_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OpenAI API key is required"
            )
        
        # Prepare API keys
        api_keys = {
            "openai_key": request.openai_key,
            "langsmith_key": request.langsmith_key,
            "tavily_key": request.tavily_key,
            "qdrant_api_key": request.qdrant_api_key,
            "qdrant_url": request.qdrant_url
        }
        
        # Process the query through the multi-agent system
        result = await chess_multi_agent.process_query(
            query=request.message,
            conversation_state=request.state,
            api_keys=api_keys
        )
        
        return ChatResponse(
            response=result["response"],
            agent_used=result["agent_used"],
            rag_sources=result["rag_sources"],
            conversation_state=result["conversation_state"]
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chess-analysis"}

# Legacy endpoints for backward compatibility
class PlayerAnalysisRequest(BaseModel):
    username: str
    openai_key: str
    langsmith_key: Optional[str] = None

class PlayerAnalysisResponse(BaseModel):
    analysis: str
    player_data: Dict[str, Any]

@router.post("/player", response_model=PlayerAnalysisResponse)
async def analyze_player(request: PlayerAnalysisRequest):
    """
    Analyze a Chess.com player (legacy endpoint)
    """
    try:
        # Use the multi-agent system for player analysis
        api_keys = {
            "openai_key": request.openai_key,
            "langsmith_key": request.langsmith_key,
            "tavily_key": None,
            "qdrant_api_key": None,
            "qdrant_url": "http://localhost:6333"
        }
        
        query = f"Analyze Chess.com player {request.username}"
        
        result = await chess_multi_agent.process_query(
            query=query,
            conversation_state={},
            api_keys=api_keys
        )
        
        return PlayerAnalysisResponse(
            analysis=result["response"],
            player_data={"username": request.username}
        )
        
    except Exception as e:
        logger.error(f"Error analyzing player: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing player: {str(e)}"
        )

class PGNAnalysisRequest(BaseModel):
    pgn_content: str
    openai_key: str
    langsmith_key: Optional[str] = None

class PGNAnalysisResponse(BaseModel):
    analysis: str
    game_data: Dict[str, Any]

@router.post("/pgn", response_model=PGNAnalysisResponse)
async def analyze_pgn(request: PGNAnalysisRequest):
    """
    Analyze a PGN chess game (legacy endpoint)
    """
    try:
        # Use the multi-agent system for PGN analysis
        api_keys = {
            "openai_key": request.openai_key,
            "langsmith_key": request.langsmith_key,
            "tavily_key": None,
            "qdrant_api_key": None,
            "qdrant_url": "http://localhost:6333"
        }
        
        query = f"Analyze this chess game: {request.pgn_content}"
        
        result = await chess_multi_agent.process_query(
            query=query,
            conversation_state={},
            api_keys=api_keys
        )
        
        return PGNAnalysisResponse(
            analysis=result["response"],
            game_data={"pgn_provided": True}
        )
        
    except Exception as e:
        logger.error(f"Error analyzing PGN: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing PGN: {str(e)}"
        ) 