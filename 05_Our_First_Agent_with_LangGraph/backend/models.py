from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Base request model with API keys
class BaseRequest(BaseModel):
    openai_key: str = Field(..., description="OpenAI API key")
    langsmith_key: str = Field(..., description="LangSmith API key") 
    tavily_key: str = Field(..., description="Tavily API key")
    qdrant_api_key: Optional[str] = Field(None, description="Qdrant API key for vector storage")
    qdrant_url: Optional[str] = Field("https://cloud.qdrant.io", description="Qdrant cluster URL")

# Request models
class PlayerAnalysisRequest(BaseRequest):
    username: str = Field(..., description="Chess.com username")

class PGNAnalysisRequest(BaseRequest):
    pgn: str = Field(..., description="PGN game data")

class RecentGamesRequest(BaseRequest):
    username: str = Field(..., description="Chess.com username")
    num_games: int = Field(10, ge=1, le=50, description="Number of recent games to analyze")

# Response models
class GameStats(BaseModel):
    total_moves: int
    result: str
    opening: Optional[str] = None
    time_control: Optional[str] = None
    accuracy_white: Optional[float] = None
    accuracy_black: Optional[float] = None

class PlayerStats(BaseModel):
    username: str
    current_rating: Dict[str, int]
    followers: int
    status: str
    last_online: Optional[datetime] = None

class AnalysisResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]
    analysis_summary: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    timestamp: datetime = Field(default_factory=datetime.now) 