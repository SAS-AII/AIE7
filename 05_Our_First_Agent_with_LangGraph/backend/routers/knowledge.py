"""Knowledge management API endpoints for chess RAG functionality"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from starlette.concurrency import run_in_threadpool
from typing import List, Dict, Any, Optional
import logging

from rag.ingest import document_ingestor
from rag.retrieve import document_retriever

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

@router.post("/upload", status_code=201)
async def upload_chess_knowledge(file: UploadFile = File(...)):
    """
    Upload a chess-related document to the knowledge base
    
    - Accepts PDF files, images, and text files
    - Processes with chess-optimized chunking
    - Stores vectors in Qdrant with cosine distance
    - Returns upload statistics
    """
    try:
        logger.info(f"Uploading chess knowledge file: {file.filename}")
        
        # Validate file type
        allowed_types = {
            "application/pdf",
            "text/plain", 
            "image/jpeg",
            "image/png",
            "image/gif"
        }
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Supported types: PDF, text, images"
            )
        
        # Check if file already exists
        from core.qdrant_client import get_qdrant
        client = get_qdrant()
        
        if client:
            # Search for existing file with same name
            existing_files = client.scroll(
                collection_name="chess_knowledge",
                scroll_filter={
                    "must": [
                        {
                            "key": "filename",
                            "match": {
                                "value": file.filename
                            }
                        }
                    ]
                },
                limit=1
            )
            
            if existing_files[0]:  # existing_files is a tuple (points, next_page_offset)
                return {
                    "detail": "File already exists",
                    "filename": file.filename,
                    "exists": True,
                    "message": f"A file named '{file.filename}' already exists in the chess knowledge base. Use the overwrite endpoint to replace it."
                }
        
        # Process file and store in Qdrant
        result = await document_ingestor.upload_to_qdrant(file)
        
        return {
            "detail": "Chess knowledge uploaded successfully",
            "result": result,
            "exists": False
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (they have proper error messages)
        raise
    except Exception as e:
        logger.error(f"Unexpected error uploading {file.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error processing document: {str(e)}"
        )

@router.post("/search")
async def search_chess_knowledge(
    query: str = Form(...),
    limit: int = Form(10),
    score_threshold: float = Form(0.3)
):
    """
    Search the chess knowledge base for relevant information
    
    - Uses semantic search with chess-optimized embeddings
    - Returns relevant chunks with similarity scores
    - Includes source metadata
    """
    try:
        logger.info(f"Searching chess knowledge: {query[:50]}...")
        
        # Search for relevant documents
        results = await document_retriever.search_similar_documents(
            query=query,
            limit=limit,
            score_threshold=score_threshold
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching chess knowledge: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching chess knowledge: {str(e)}"
        )

@router.get("/files")
async def list_chess_knowledge_files():
    """
    List all uploaded files in the chess knowledge base
    
    - Returns unique filenames with metadata
    - Shows upload and chunk information
    """
    try:
        from core.qdrant_client import get_qdrant
        
        client = get_qdrant()
        if not client:
            raise HTTPException(
                status_code=503,
                detail="Vector database not available"
            )
        
        # Get all unique filenames
        files_map = {}
        offset = None
        
        while True:
            # Scroll through all points
            points, next_offset = client.scroll(
                collection_name="chess_knowledge",
                limit=100,
                offset=offset,
                with_payload=True
            )
            
            if not points:
                break
                
            for point in points:
                filename = point.payload.get("filename", "unknown")
                if filename not in files_map:
                    files_map[filename] = {
                        "filename": filename,
                        "content_type": point.payload.get("content_type", "unknown"),
                        "total_chunks": point.payload.get("total_chunks", 0),
                        "file_hash": point.payload.get("file_hash", ""),
                        "chunk_count": 0,
                        "source": point.payload.get("source", "uploaded_document")
                    }
                files_map[filename]["chunk_count"] += 1
            
            if next_offset is None:
                break
            offset = next_offset
        
        files_list = list(files_map.values())
        
        return {
            "files": files_list,
            "total_files": len(files_list),
            "total_chunks": sum(f["chunk_count"] for f in files_list)
        }
        
    except Exception as e:
        logger.error(f"Error listing chess knowledge files: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing files: {str(e)}"
        )

@router.delete("/files/{filename}")
async def delete_chess_knowledge_file(filename: str):
    """
    Delete a specific file from the chess knowledge base
    
    - Removes all chunks associated with the filename
    - Returns deletion statistics
    """
    try:
        from core.qdrant_client import get_qdrant
        
        client = get_qdrant()
        if not client:
            raise HTTPException(
                status_code=503,
                detail="Vector database not available"
            )
        
        # Find all points with this filename
        points_to_delete = []
        offset = None
        
        while True:
            points, next_offset = client.scroll(
                collection_name="chess_knowledge",
                scroll_filter={
                    "must": [
                        {
                            "key": "filename",
                            "match": {
                                "value": filename
                            }
                        }
                    ]
                },
                limit=100,
                offset=offset,
                with_payload=False  # We only need IDs
            )
            
            if not points:
                break
                
            points_to_delete.extend([point.id for point in points])
            
            if next_offset is None:
                break
            offset = next_offset
        
        if not points_to_delete:
            raise HTTPException(
                status_code=404,
                detail=f"File '{filename}' not found in chess knowledge base"
            )
        
        # Delete all points for this file
        client.delete(
            collection_name="chess_knowledge",
            points_selector=points_to_delete
        )
        
        logger.info(f"Deleted {len(points_to_delete)} chunks for file: {filename}")
        
        return {
            "detail": "Chess knowledge file deleted successfully",
            "filename": filename,
            "chunks_deleted": len(points_to_delete)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chess knowledge file {filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        )

@router.post("/files/{filename}/overwrite")
async def overwrite_chess_knowledge_file(filename: str, file: UploadFile = File(...)):
    """
    Overwrite an existing file in the chess knowledge base
    
    - Deletes existing file chunks
    - Uploads new file with same name
    """
    try:
        # First delete the existing file
        await delete_chess_knowledge_file(filename)
        
        # Then upload the new file
        result = await document_ingestor.upload_to_qdrant(file)
        
        return {
            "detail": "Chess knowledge file overwritten successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error overwriting chess knowledge file {filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error overwriting file: {str(e)}"
        )

@router.get("/stats")
async def get_chess_knowledge_stats():
    """
    Get statistics about the chess knowledge base
    
    - Collection information
    - Document counts
    - System health
    """
    try:
        from core.qdrant_client import get_qdrant
        
        client = get_qdrant()
        if not client:
            return {
                "status": "unavailable",
                "message": "Vector database not configured"
            }
        
        collection_info = client.get_collection("chess_knowledge")
        
        return {
            "collection_name": "chess_knowledge",
            "total_documents": collection_info.points_count,
            "vector_size": collection_info.config.params.vectors.size,
            "distance_metric": collection_info.config.params.vectors.distance.value,
            "status": "healthy"
        }
        
    except Exception as e:
        logger.error(f"Error getting chess knowledge stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting knowledge base stats: {str(e)}"
        ) 