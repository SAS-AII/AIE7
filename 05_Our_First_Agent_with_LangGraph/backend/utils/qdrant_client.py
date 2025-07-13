import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Optional
import hashlib
import json
from utils.logging import get_logger

logger = get_logger(__name__)

def create_qdrant_client(api_key: Optional[str] = None, url: Optional[str] = None) -> QdrantClient:
    """Create a configured Qdrant client using environment variables or provided credentials"""
    try:
        # Check environment variables first, then fall back to parameters
        qdrant_api_key = api_key or os.getenv("QDRANT_API_KEY")
        qdrant_url = url or os.getenv("QDRANT_URL", "https://cloud.qdrant.io")
        
        if not qdrant_api_key:
            raise ValueError("Qdrant API key not found in environment variables or request parameters")
        
        client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=30
        )
        logger.info(f"Qdrant client created successfully for URL: {qdrant_url}")
        return client
    except Exception as e:
        logger.error(f"Failed to create Qdrant client: {e}")
        raise

def ensure_chess_collection_exists(client: QdrantClient, collection_name: str = "chess_games") -> bool:
    """Ensure the chess games collection exists with proper configuration"""
    try:
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if collection_name not in collection_names:
            # Create collection for chess game embeddings (1536 dimensions for OpenAI text-embedding-ada-002)
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            logger.info(f"Created collection: {collection_name}")
        else:
            logger.debug(f"Collection {collection_name} already exists")
        
        return True
    except Exception as e:
        logger.error(f"Failed to ensure collection exists: {e}")
        return False

def generate_point_id(content: str) -> str:
    """Generate consistent point ID from content hash"""
    return hashlib.md5(content.encode()).hexdigest()

def upsert_game_vectors(
    client: QdrantClient,
    games_data: List[Dict[str, Any]],
    embeddings: List[List[float]],
    collection_name: str = "chess_games"
) -> bool:
    """Upsert game data with embeddings to Qdrant collection"""
    try:
        points = []
        for i, (game_data, embedding) in enumerate(zip(games_data, embeddings)):
            # Generate consistent ID based on game content
            point_id = generate_point_id(str(game_data))
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "pgn": game_data.get("pgn", ""),
                    "white_player": game_data.get("white_player", "Unknown"),
                    "black_player": game_data.get("black_player", "Unknown"),
                    "result": game_data.get("result", "*"),
                    "opening": game_data.get("opening", "Unknown"),
                    "eco": game_data.get("eco", "Unknown"),
                    "time_control": game_data.get("time_control", "Unknown"),
                    "total_moves": game_data.get("total_moves", 0),
                    "date": game_data.get("date", "Unknown"),
                    "event": game_data.get("event", "Unknown"),
                    "analysis_summary": game_data.get("analysis_summary", ""),
                    "tactical_complexity": game_data.get("tactical_complexity", 0.0)
                }
            )
            points.append(point)
        
        # Synchronous upsert to ensure data is queryable immediately
        client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True  # Wait for completion before returning
        )
        
        logger.info(f"Successfully upserted {len(points)} game vectors to {collection_name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to upsert vectors: {e}")
        return False

def search_similar_games(
    client: QdrantClient,
    query_embedding: List[float],
    collection_name: str = "chess_games",
    limit: int = 5,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Search for similar games in the vector database"""
    try:
        search_result = client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )
        
        results = []
        for scored_point in search_result:
            result = {
                "id": scored_point.id,
                "score": scored_point.score,
                "payload": scored_point.payload
            }
            results.append(result)
        
        logger.info(f"Found {len(results)} similar games")
        return results
        
    except Exception as e:
        logger.error(f"Failed to search vectors: {e}")
        return []

def delete_game_vectors(
    client: QdrantClient,
    point_ids: List[str],
    collection_name: str = "chess_games"
) -> bool:
    """Delete specific game vectors from collection"""
    try:
        client.delete(
            collection_name=collection_name,
            points_selector=point_ids,
            wait=True
        )
        
        logger.info(f"Deleted {len(point_ids)} vectors from {collection_name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to delete vectors: {e}")
        return False

def is_qdrant_available() -> bool:
    """Check if Qdrant is available via environment variables or request parameters"""
    return bool(os.getenv("QDRANT_API_KEY"))

def get_qdrant_config() -> Dict[str, Optional[str]]:
    """Get Qdrant configuration from environment variables"""
    return {
        "api_key": os.getenv("QDRANT_API_KEY"),
        "url": os.getenv("QDRANT_URL", "https://cloud.qdrant.io")
    } 