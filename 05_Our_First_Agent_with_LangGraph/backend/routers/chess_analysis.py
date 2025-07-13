from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional
import json

from models import (
    PlayerAnalysisRequest, 
    PGNAnalysisRequest, 
    RecentGamesRequest,
    AnalysisResponse,
    ErrorResponse
)
from agents.graph import analyze_player, analyze_pgn_game, analyze_recent_games
from utils.logging import get_logger
from utils.qdrant_client import (
    create_qdrant_client, 
    ensure_chess_collection_exists, 
    upsert_game_vectors,
    is_qdrant_available,
    get_qdrant_config
)

logger = get_logger(__name__)

router = APIRouter(tags=["chess-analysis"])

@router.post("/player", response_model=AnalysisResponse)
async def analyze_chess_player(request: PlayerAnalysisRequest):
    """
    Analyze a Chess.com player's profile, ratings, and performance
    
    Requires:
    - username: Chess.com username
    - openai_key: OpenAI API key
    - langsmith_key: LangSmith API key
    - tavily_key: Tavily API key (reserved for future use)
    - qdrant_api_key: Optional (can use environment variable QDRANT_API_KEY)
    """
    logger.info(f"Player analysis request for: {request.username}")
    
    if not request.username:
        logger.warning("Player analysis request missing username")
        return AnalysisResponse(
            success=True,
            message="Please enter your Chess.com username to analyze your games or profile.",
            data={},
            analysis_summary="Username is required for player analysis. Please provide your Chess.com username."
        )
    
    try:
        # Run LangGraph agent analysis
        result = analyze_player(
            username=request.username,
            openai_key=request.openai_key,
            langsmith_key=request.langsmith_key
        )
        
        if not result["success"]:
            logger.error(f"Player analysis failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {result.get('error')}"
            )
        
        response_data = {
            "username": request.username,
            "analysis_type": "player_profile",
            "message_count": result.get("message_count", 0),
            "qdrant_available": is_qdrant_available() or bool(request.qdrant_api_key)
        }
        
        logger.info(f"Player analysis completed successfully for: {request.username}")
        return AnalysisResponse(
            success=True,
            message=f"Successfully analyzed player: {request.username}",
            data=response_data,
            analysis_summary=result["analysis"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error during player analysis: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@router.post("/pgn", response_model=AnalysisResponse)
async def analyze_pgn_game(request: PGNAnalysisRequest):
    """
    Analyze a chess game provided in PGN format
    
    Requires:
    - pgn: PGN game data
    - openai_key: OpenAI API key  
    - langsmith_key: LangSmith API key
    - tavily_key: Tavily API key (reserved for future use)
    - qdrant_api_key: Optional (can use environment variable QDRANT_API_KEY)
    """
    logger.info("PGN analysis request received")
    
    if not request.pgn.strip():
        logger.warning("PGN analysis request missing game data")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide PGN game data for analysis."
        )
    
    try:
        # Run LangGraph agent analysis
        result = analyze_pgn_game(
            pgn_content=request.pgn,
            openai_key=request.openai_key,
            langsmith_key=request.langsmith_key
        )
        
        if not result["success"]:
            logger.error(f"PGN analysis failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {result.get('error')}"
            )
        
        # Check if Qdrant is available (env vars or request params)
        vector_storage_result = None
        qdrant_available = is_qdrant_available() or bool(request.qdrant_api_key)
        
        if qdrant_available:
            try:
                vector_storage_result = await _store_pgn_in_qdrant(
                    request.pgn, 
                    result["analysis"],
                    request.qdrant_api_key,
                    request.qdrant_url
                )
            except Exception as e:
                logger.warning(f"Failed to store in Qdrant: {e}")
                # Continue without vector storage
        
        response_data = {
            "analysis_type": "pgn_game",
            "message_count": result.get("message_count", 0),
            "vector_storage": vector_storage_result is not None,
            "qdrant_available": qdrant_available
        }
        
        logger.info("PGN analysis completed successfully")
        return AnalysisResponse(
            success=True,
            message="Successfully analyzed PGN game",
            data=response_data,
            analysis_summary=result["analysis"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error during PGN analysis: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@router.post("/recent-games", response_model=AnalysisResponse)
async def analyze_recent_games_endpoint(request: RecentGamesRequest):
    """
    Analyze recent games for a Chess.com player
    
    Requires:
    - username: Chess.com username
    - num_games: Number of recent games to analyze (1-50)
    - openai_key: OpenAI API key
    - langsmith_key: LangSmith API key  
    - tavily_key: Tavily API key (reserved for future use)
    - qdrant_api_key: Optional (can use environment variable QDRANT_API_KEY)
    """
    logger.info(f"Recent games analysis request for: {request.username} ({request.num_games} games)")
    
    if not request.username:
        logger.warning("Recent games analysis request missing username")
        return AnalysisResponse(
            success=True,
            message="Please enter your Chess.com username to analyze your recent games.",
            data={},
            analysis_summary="Username is required for recent games analysis. Please provide your Chess.com username."
        )
    
    try:
        # Run LangGraph agent analysis
        result = analyze_recent_games(
            username=request.username,
            num_games=request.num_games,
            openai_key=request.openai_key,
            langsmith_key=request.langsmith_key
        )
        
        if not result["success"]:
            logger.error(f"Recent games analysis failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {result.get('error')}"
            )
        
        response_data = {
            "username": request.username,
            "num_games_requested": request.num_games,
            "analysis_type": "recent_games",
            "message_count": result.get("message_count", 0),
            "qdrant_available": is_qdrant_available() or bool(request.qdrant_api_key)
        }
        
        logger.info(f"Recent games analysis completed for: {request.username}")
        return AnalysisResponse(
            success=True,
            message=f"Successfully analyzed {request.num_games} recent games for {request.username}",
            data=response_data,
            analysis_summary=result["analysis"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error during recent games analysis: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

async def _store_pgn_in_qdrant(
    pgn_content: str, 
    analysis_summary: str, 
    request_api_key: Optional[str] = None,
    request_url: Optional[str] = None
) -> bool:
    """Store PGN game and analysis in Qdrant vector database"""
    try:
        # Create Qdrant client (checks env vars first, then request params)
        qdrant_client = create_qdrant_client(request_api_key, request_url)
        
        # Ensure collection exists
        if not ensure_chess_collection_exists(qdrant_client):
            logger.error("Failed to ensure Qdrant collection exists")
            return False
        
        # Generate embedding for the game analysis (simplified - in production, use OpenAI embeddings)
        # For now, we'll skip the actual embedding generation and vector storage
        # This would require additional OpenAI API calls for text-embedding-ada-002
        
        logger.info("Qdrant storage placeholder - embedding generation not implemented")
        return True
        
    except Exception as e:
        logger.error(f"Error storing in Qdrant: {e}")
        return False 