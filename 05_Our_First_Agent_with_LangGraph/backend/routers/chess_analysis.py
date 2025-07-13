"""Chess analysis API endpoints using multi-agent LangGraph system"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging

from agents.multi_agent_graph import ChessMultiAgentSystem

logger = logging.getLogger(__name__)

# Request models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User's chess-related message")
    state: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Conversation state")
    openai_key: str = Field(..., description="OpenAI API key")
    langsmith_key: Optional[str] = Field(None, description="LangSmith API key for tracing")
    tavily_key: Optional[str] = Field(None, description="Tavily API key for web search")
    qdrant_api_key: Optional[str] = Field(None, description="Qdrant API key")
    qdrant_url: Optional[str] = Field(None, description="Qdrant URL")

class PlayerAnalysisRequest(BaseModel):
    username: Optional[str] = Field(None, description="Chess.com username")
    openai_key: str = Field(..., description="OpenAI API key")
    langsmith_key: Optional[str] = Field(None, description="LangSmith API key")
    tavily_key: Optional[str] = Field(None, description="Tavily API key")
    qdrant_api_key: Optional[str] = Field(None, description="Qdrant API key")
    qdrant_url: Optional[str] = Field(None, description="Qdrant URL")

class PGNAnalysisRequest(BaseModel):
    pgn: str = Field(..., description="PGN string of the chess game")
    openai_key: str = Field(..., description="OpenAI API key")
    langsmith_key: Optional[str] = Field(None, description="LangSmith API key")
    tavily_key: Optional[str] = Field(None, description="Tavily API key")
    qdrant_api_key: Optional[str] = Field(None, description="Qdrant API key")
    qdrant_url: Optional[str] = Field(None, description="Qdrant URL")

class RecentGamesRequest(BaseModel):
    username: Optional[str] = Field(None, description="Chess.com username")
    num_games: int = Field(default=5, description="Number of recent games to analyze")
    openai_key: str = Field(..., description="OpenAI API key")
    langsmith_key: Optional[str] = Field(None, description="LangSmith API key")
    tavily_key: Optional[str] = Field(None, description="Tavily API key")
    qdrant_api_key: Optional[str] = Field(None, description="Qdrant API key")
    qdrant_url: Optional[str] = Field(None, description="Qdrant URL")

# Response models
class ChatResponse(BaseModel):
    response: str = Field(..., description="Chess assistant's response")
    state: Dict[str, Any] = Field(..., description="Updated conversation state")
    agent_used: Optional[str] = Field(None, description="Which agent handled the request")
    rag_sources: Optional[int] = Field(None, description="Number of RAG sources used")

router = APIRouter(prefix="/analyze", tags=["chess-analysis"])

@router.post("/chat", response_model=ChatResponse)
async def chat_with_chess_assistant(request: ChatRequest):
    """
    Chat with the multi-agent chess assistant
    
    - Uses supervisor agent to route to appropriate specialist
    - RAG agent for chess knowledge from documents
    - Chess agent for Chess.com data and game analysis
    - Instant response with proper state management
    """
    try:
        logger.info(f"Processing chat message: {request.message[:50]}...")
        
        # Validate required API key
        if not request.openai_key:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is required for chess assistance"
            )
        
        # Initialize multi-agent system
        chess_system = ChessMultiAgentSystem(
            openai_key=request.openai_key,
            langsmith_key=request.langsmith_key,
            tavily_key=request.tavily_key
        )
        
        # Process message through multi-agent system
        result = await chess_system.process_message(
            message=request.message,
            conversation_state=request.state
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"Error processing message: {result.get('error', 'Unknown error')}"
            )
        
        # Extract agent and RAG information
        agent_used = result["state"].get("current_agent", "unknown")
        rag_sources = 0
        if "rag_context" in result["state"]:
            rag_sources = result["state"]["rag_context"].get("context_count", 0)
        
        logger.info(f"Chat processed by {agent_used} agent with {rag_sources} RAG sources")
        
        return ChatResponse(
            response=result["response"],
            state=result["state"],
            agent_used=agent_used,
            rag_sources=rag_sources if rag_sources > 0 else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing chat request"
        )

@router.post("/player")
async def analyze_player(request: PlayerAnalysisRequest):
    """
    Analyze a Chess.com player using multi-agent system
    
    - Legacy endpoint that routes to chat system
    - Maintains backward compatibility
    """
    try:
        if not request.username:
            return {
                "response": "Please provide a Chess.com username to analyze. For example: 'Analyze player hikaru'",
                "state": {}
            }
        
        # Convert to chat request
        chat_message = f"Analyze the Chess.com player {request.username}. Provide detailed statistics and insights."
        
        chat_request = ChatRequest(
            message=chat_message,
            openai_key=request.openai_key,
            langsmith_key=request.langsmith_key,
            tavily_key=request.tavily_key,
            qdrant_api_key=request.qdrant_api_key,
            qdrant_url=request.qdrant_url
        )
        
        return await chat_with_chess_assistant(chat_request)
        
    except Exception as e:
        logger.error(f"Error in player analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error analyzing player"
        )

@router.post("/pgn")
async def analyze_pgn(request: PGNAnalysisRequest):
    """
    Analyze a chess game in PGN format using multi-agent system
    
    - Legacy endpoint that routes to chat system
    - Maintains backward compatibility
    """
    try:
        # Convert to chat request
        chat_message = f"Analyze this chess game:\n\n{request.pgn}\n\nProvide detailed analysis including key moves, tactics, and strategic insights."
        
        chat_request = ChatRequest(
            message=chat_message,
            openai_key=request.openai_key,
            langsmith_key=request.langsmith_key,
            tavily_key=request.tavily_key,
            qdrant_api_key=request.qdrant_api_key,
            qdrant_url=request.qdrant_url
        )
        
        return await chat_with_chess_assistant(chat_request)
        
    except Exception as e:
        logger.error(f"Error in PGN analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error analyzing PGN"
        )

@router.post("/recent-games")
async def analyze_recent_games(request: RecentGamesRequest):
    """
    Analyze recent games for a Chess.com player using multi-agent system
    
    - Legacy endpoint that routes to chat system
    - Maintains backward compatibility
    """
    try:
        if not request.username:
            return {
                "response": "Please provide a Chess.com username to analyze recent games. For example: 'Analyze recent games for hikaru'",
                "state": {}
            }
        
        # Convert to chat request
        chat_message = f"Analyze the {request.num_games} most recent games for Chess.com player {request.username}. Provide insights on performance, patterns, and areas for improvement."
        
        chat_request = ChatRequest(
            message=chat_message,
            openai_key=request.openai_key,
            langsmith_key=request.langsmith_key,
            tavily_key=request.tavily_key,
            qdrant_api_key=request.qdrant_api_key,
            qdrant_url=request.qdrant_url
        )
        
        return await chat_with_chess_assistant(chat_request)
        
    except Exception as e:
        logger.error(f"Error in recent games analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error analyzing recent games"
        ) 