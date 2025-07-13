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
    
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        self.client = None
        self.collection_name = "knowledge_base"
        self.url = url
        self.api_key = api_key
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Qdrant client with proper configuration"""
        try:
            # Use provided credentials or fallback to environment variables
            qdrant_url = self.url or os.getenv("QDRANT_URL")
            qdrant_api_key = self.api_key or os.getenv("QDRANT_API_KEY")
            
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
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                # Create collection with vector configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI embedding dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
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

def get_qdrant_client(url: Optional[str] = None, api_key: Optional[str] = None) -> Optional[QdrantClient]:
    """Get a Qdrant client instance with optional custom credentials"""
    if url and api_key:
        # Create a new client instance with provided credentials
        client_instance = ChessQdrantClient(url=url, api_key=api_key)
        return client_instance.get_client()
    else:
        # Return the global instance
        return get_qdrant()

def is_qdrant_available() -> bool:
    """Check if Qdrant is available"""
    return _qdrant_client.is_available() 