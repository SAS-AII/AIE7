"""Document retrieval system for chess knowledge base"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from aimakerspace.openai_utils.embedding import EmbeddingModel
from aimakerspace.vectordatabase import VectorDatabase
from core.qdrant_client import get_qdrant_client
from .prompts import CHESS_QUERY_EXPANSION_PROMPT, CHESS_RESPONSE_PROMPT

logger = logging.getLogger(__name__)

class ChessDocumentRetriever:
    def __init__(self, api_key: Optional[str] = None):
        self.embedding_model = EmbeddingModel(api_key=api_key) if api_key else None
        self.vector_db = None
        self.qdrant_client = None
        self.collection_name = "chess_knowledge"
        
    def _ensure_clients(self, api_key: str, qdrant_url: str, qdrant_api_key: str):
        """Ensure all clients are initialized"""
        if not self.embedding_model:
            self.embedding_model = EmbeddingModel(api_key=api_key)
        
        if not self.qdrant_client:
            self.qdrant_client = get_qdrant_client(qdrant_url, qdrant_api_key)
            
        if not self.vector_db and self.qdrant_client:
            self.vector_db = VectorDatabase(
                collection_name=self.collection_name,
                embedding_model=self.embedding_model,
                qdrant_client=self.qdrant_client
            )
    
    async def expand_chess_query(self, query: str, api_key: str) -> List[str]:
        """Expand a chess query into multiple search terms"""
        try:
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=api_key
            )
            
            expanded_query = await llm.ainvoke(
                CHESS_QUERY_EXPANSION_PROMPT.format(query=query)
            )
            
            # Parse the response to extract search terms
            content = expanded_query.content.strip()
            if content.startswith('[') and content.endswith(']'):
                import ast
                try:
                    terms = ast.literal_eval(content)
                    return terms if isinstance(terms, list) else [query]
                except:
                    pass
            
            # Fallback: split by lines and clean up
            lines = content.split('\n')
            terms = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('//'):
                    # Remove bullet points and numbering
                    line = line.lstrip('- •*123456789. ')
                    if line:
                        terms.append(line)
            
            return terms[:5] if terms else [query]  # Limit to 5 terms
            
        except Exception as e:
            logger.error(f"Error expanding query: {e}")
            return [query]
    
    async def retrieve_documents(
        self, 
        query: str, 
        api_key: str,
        qdrant_url: str,
        qdrant_api_key: str,
        k: int = 5
    ) -> List[Document]:
        """Retrieve relevant documents for a chess query"""
        try:
            self._ensure_clients(api_key, qdrant_url, qdrant_api_key)
            
            if not self.qdrant_client:
                logger.warning("Qdrant client not available, returning empty results")
                return []
            
            # Expand the query for better retrieval
            expanded_queries = await self.expand_chess_query(query, api_key)
            
            all_documents = []
            seen_content = set()
            
            # Search with each expanded query
            for expanded_query in expanded_queries:
                try:
                    # Get embedding for the query
                    query_embedding = await self.embedding_model.async_get_embedding(expanded_query)
                    
                    # Search in vector database
                    search_results = self.qdrant_client.search(
                        collection_name=self.collection_name,
                        query_vector=query_embedding,
                        limit=k,
                        score_threshold=0.5
                    )
                    
                    # Convert to Document objects
                    for result in search_results:
                        content = result.payload.get('content', '')
                        if content and content not in seen_content:
                            seen_content.add(content)
                            doc = Document(
                                page_content=content,
                                metadata={
                                    'source': result.payload.get('source', 'unknown'),
                                    'score': result.score,
                                    'query': expanded_query
                                }
                            )
                            all_documents.append(doc)
                            
                except Exception as e:
                    logger.error(f"Error searching with query '{expanded_query}': {e}")
                    continue
            
            # Sort by score and return top k
            all_documents.sort(key=lambda x: x.metadata.get('score', 0), reverse=True)
            return all_documents[:k]
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    async def get_contextual_answer(
        self, 
        query: str, 
        documents: List[Document],
        api_key: str
    ) -> str:
        """Generate a contextual answer using retrieved documents"""
        try:
            from langchain_openai import ChatOpenAI
            
            if not documents:
                return "I don't have enough information in my knowledge base to answer this chess question. Please try asking about chess openings, tactics, endgames, or strategy."
            
            # Prepare context from documents
            context_parts = []
            for i, doc in enumerate(documents[:3], 1):  # Use top 3 documents
                context_parts.append(f"Source {i}: {doc.page_content}")
            
            context = "\n\n".join(context_parts)
            
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=api_key
            )
            
            response = await llm.ainvoke(
                CHESS_RESPONSE_PROMPT.format(
                    context=context,
                    query=query
                )
            )
            
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating contextual answer: {e}")
            return "I encountered an error while processing your chess question. Please try again."

    def get_collection_info(self, qdrant_url: str, qdrant_api_key: str) -> Dict[str, Any]:
        """Get information about the chess knowledge collection"""
        try:
            if not self.qdrant_client:
                self.qdrant_client = get_qdrant_client(qdrant_url, qdrant_api_key)
            
            if not self.qdrant_client:
                return {
                    "exists": False,
                    "points_count": 0,
                    "vectors_count": 0,
                    "status": "client_unavailable"
                }
            
            try:
                collection_info = self.qdrant_client.get_collection(self.collection_name)
                return {
                    "exists": True,
                    "points_count": collection_info.points_count,
                    "vectors_count": collection_info.vectors_count,
                    "status": collection_info.status
                }
            except Exception:
                return {
                    "exists": False,
                    "points_count": 0,
                    "vectors_count": 0,
                    "status": "not_found"
                }
                
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                "exists": False,
                "points_count": 0,
                "vectors_count": 0,
                "status": "error"
            }

# Create a function to get a retriever instance instead of a global instance
def get_document_retriever(api_key: Optional[str] = None) -> ChessDocumentRetriever:
    """Get a document retriever instance"""
    return ChessDocumentRetriever(api_key=api_key)

# For backward compatibility, create a default instance only when needed
document_retriever = None

def get_default_document_retriever():
    """Get the default document retriever instance"""
    global document_retriever
    if document_retriever is None:
        document_retriever = ChessDocumentRetriever()
    return document_retriever 