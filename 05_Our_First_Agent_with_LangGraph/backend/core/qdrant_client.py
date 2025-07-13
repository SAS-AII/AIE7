"""Qdrant vector database client for chess knowledge management"""
import os
import logging
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, CollectionInfo
from qdrant_client.http.exceptions import UnexpectedResponse

logger = logging.getLogger(__name__)

class ChessQdrantClient:
    """Qdrant client for chess knowledge storage"""
    
    def __init__(self):
        self.client = None
        self.collection_name = "chess_knowledge"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Qdrant client with proper configuration"""
        try:
            qdrant_url = os.getenv("QDRANT_URL")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")
            
            if not qdrant_url or not qdrant_api_key:
                logger.warning("Qdrant credentials not found. Vector search will be disabled.")
                return
            
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
                timeout=30
            )
            
            # Ensure collection exists
            self._ensure_collection_exists()
            
            logger.info("Qdrant client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            self.client = None
    
    def _ensure_collection_exists(self):
        """Ensure the chess knowledge collection exists"""
        if not self.client:
            return
        
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection with optimized settings for chess knowledge
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI embedding size
                        distance=Distance.COSINE  # Best for semantic similarity
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
    
    def is_available(self) -> bool:
        """Check if Qdrant client is available"""
        return self.client is not None
    
    def get_client(self) -> Optional[QdrantClient]:
        """Get the Qdrant client instance"""
        return self.client

# Global instance
_qdrant_client = ChessQdrantClient()

def get_qdrant() -> Optional[QdrantClient]:
    """Get the global Qdrant client instance"""
    return _qdrant_client.get_client()

def is_qdrant_available() -> bool:
    """Check if Qdrant is available"""
    return _qdrant_client.is_available() 