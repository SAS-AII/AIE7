"""Document retrieval system for chess knowledge base"""
import logging
from typing import List, Dict, Any, Optional
from aimakerspace.openai_utils.embedding import EmbeddingModel

logger = logging.getLogger(__name__)

class ChessDocumentRetriever:
    """Handles retrieval of relevant chess knowledge from the vector database"""
    
    def __init__(self):
        self.embedding_model = EmbeddingModel()
    
    def _expand_query(self, query: str) -> List[str]:
        """Expand query with chess-related terms for better retrieval"""
        base_queries = [query]
        
        # Add chess-specific expansions
        chess_terms = {
            "opening": ["chess opening", "opening theory", "opening moves"],
            "endgame": ["chess endgame", "endgame technique", "endgame theory"],
            "tactic": ["chess tactics", "tactical motifs", "chess combinations"],
            "strategy": ["chess strategy", "strategic concepts", "positional play"],
            "player": ["chess player", "grandmaster", "chess master"],
            "game": ["chess game", "chess match", "chess analysis"]
        }
        
        query_lower = query.lower()
        for key, expansions in chess_terms.items():
            if key in query_lower:
                base_queries.extend(expansions)
        
        return base_queries[:5]  # Limit to avoid too many queries
    
    async def search_similar_documents(
        self,
        query: str,
        limit: int = 10,
        score_threshold: float = 0.3,
        use_query_expansion: bool = True
    ) -> List[Dict[str, Any]]:
        """Search for similar documents in the chess knowledge base"""
        try:
            from core.qdrant_client import get_qdrant
            client = get_qdrant()
            
            # Generate query embedding
            query_embedding = self.embedding_model.get_embeddings([query])[0]
            
            # Search in Qdrant
            search_results = client.search(
                collection_name="chess_knowledge",
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "content": result.payload["content"],
                    "filename": result.payload.get("filename", "unknown"),
                    "chunk_index": result.payload.get("chunk_index", 0),
                    "similarity_score": result.score,
                    "source": result.payload.get("source", "unknown"),
                    "content_type": result.payload.get("content_type", "unknown")
                })
            
            # If no results and query expansion is enabled, try expanded queries
            if not results and use_query_expansion:
                expanded_queries = self._expand_query(query)
                for expanded_query in expanded_queries[1:]:  # Skip original query
                    expanded_embedding = self.embedding_model.get_embeddings([expanded_query])[0]
                    expanded_results = client.search(
                        collection_name="chess_knowledge",
                        query_vector=expanded_embedding,
                        limit=limit // 2,  # Use fewer results per expansion
                        score_threshold=score_threshold * 0.8,  # Lower threshold for expansions
                        with_payload=True
                    )
                    
                    for result in expanded_results:
                        results.append({
                            "content": result.payload["content"],
                            "filename": result.payload.get("filename", "unknown"),
                            "chunk_index": result.payload.get("chunk_index", 0),
                            "similarity_score": result.score,
                            "source": result.payload.get("source", "unknown"),
                            "content_type": result.payload.get("content_type", "unknown"),
                            "search_query": expanded_query
                        })
                    
                    if results:  # Stop if we found something
                        break
                
                # Remove duplicates and sort by score
                seen_content = set()
                unique_results = []
                for result in sorted(results, key=lambda x: x["similarity_score"], reverse=True):
                    content_key = (result["content"][:100], result["filename"])
                    if content_key not in seen_content:
                        seen_content.add(content_key)
                        unique_results.append(result)
                
                results = unique_results[:limit]
            
            logger.info(f"Retrieved {len(results)} documents for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    async def get_context_for_query(
        self,
        query: str,
        max_chunks: int = 8,
        max_chars: int = 6000
    ) -> Dict[str, Any]:
        """Get formatted context for RAG responses"""
        try:
            # Search for relevant documents
            documents = await self.search_similar_documents(
                query=query,
                limit=max_chunks,
                score_threshold=0.3
            )
            
            if not documents:
                return {
                    "context": "No relevant chess knowledge found for this query.",
                    "context_count": 0,
                    "similarity_scores": [],
                    "sources": []
                }
            
            # Build context string
            context_parts = []
            total_chars = 0
            similarity_scores = []
            sources = []
            
            for i, doc in enumerate(documents):
                if total_chars >= max_chars:
                    break
                
                chunk_text = f"[Source {i+1}: {doc['filename']}]\n{doc['content']}\n"
                
                if total_chars + len(chunk_text) <= max_chars:
                    context_parts.append(chunk_text)
                    total_chars += len(chunk_text)
                    similarity_scores.append(doc['similarity_score'])
                    sources.append({
                        "filename": doc['filename'],
                        "chunk_index": doc['chunk_index'],
                        "score": doc['similarity_score']
                    })
                else:
                    # Add partial content if it fits
                    remaining_chars = max_chars - total_chars
                    if remaining_chars > 100:  # Only if meaningful content can fit
                        partial_content = doc['content'][:remaining_chars-50] + "..."
                        chunk_text = f"[Source {i+1}: {doc['filename']}]\n{partial_content}\n"
                        context_parts.append(chunk_text)
                        similarity_scores.append(doc['similarity_score'])
                        sources.append({
                            "filename": doc['filename'],
                            "chunk_index": doc['chunk_index'],
                            "score": doc['similarity_score']
                        })
                    break
            
            context = "\n".join(context_parts)
            
            return {
                "context": context,
                "context_count": len(context_parts),
                "similarity_scores": similarity_scores,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error generating context: {e}")
            return {
                "context": "Error retrieving chess knowledge.",
                "context_count": 0,
                "similarity_scores": [],
                "sources": []
            }

# Global instance
document_retriever = ChessDocumentRetriever() 