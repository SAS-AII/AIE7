"""Document ingestion system for chess knowledge base"""
import os
import hashlib
import tempfile
import logging
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException
import fitz  # PyMuPDF
from PIL import Image
import io
import uuid

from aimakerspace.text_utils import CharacterTextSplitter, TextFileLoader
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.openai_utils.embedding import EmbeddingModel

logger = logging.getLogger(__name__)

class ChessDocumentIngestor:
    """Handles ingestion of chess-related documents into the knowledge base"""
    
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.text_splitter = CharacterTextSplitter()
        
    def _calculate_file_hash(self, content: bytes) -> str:
        """Calculate hash of file content for deduplication"""
        return hashlib.md5(content).hexdigest()
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")
    
    def _extract_text_from_image(self, file_path: str) -> str:
        """Extract text from image using OCR (placeholder - you can implement OCR here)"""
        # For now, return a placeholder. You can implement OCR with pytesseract or similar
        try:
            with Image.open(file_path) as img:
                # Placeholder: In a real implementation, you'd use OCR here
                return f"[Image content from {os.path.basename(file_path)} - OCR not implemented yet]"
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    
    def _process_file_content(self, file_path: str, filename: str, content_type: str) -> str:
        """Process file and extract text content"""
        if content_type == "application/pdf":
            return self._extract_text_from_pdf(file_path)
        elif content_type.startswith("image/"):
            return self._extract_text_from_image(file_path)
        elif content_type == "text/plain":
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {content_type}"
            )
    
    def _chunk_text(self, text: str, filename: str) -> List[Dict[str, Any]]:
        """Split text into chunks for vector storage"""
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create chunk metadata
            chunk_data = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():  # Only include non-empty chunks
                    chunk_data.append({
                        "content": chunk.strip(),
                        "metadata": {
                            "filename": filename,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "content_type": "chess_knowledge",
                            "source": "uploaded_document"
                        }
                    })
            
            return chunk_data
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")
    
    async def upload_to_qdrant(self, file: UploadFile) -> Dict[str, Any]:
        """Upload and process file into Qdrant vector database"""
        try:
            # Read file content
            content = await file.read()
            file_hash = self._calculate_file_hash(content)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text from file
                text_content = self._process_file_content(
                    temp_file_path, 
                    file.filename, 
                    file.content_type
                )
                
                if not text_content.strip():
                    raise HTTPException(
                        status_code=400, 
                        detail="No text content could be extracted from the file"
                    )
                
                # Chunk the text
                chunks = self._chunk_text(text_content, file.filename)
                
                if not chunks:
                    raise HTTPException(
                        status_code=400, 
                        detail="No valid chunks could be created from the file"
                    )
                
                # Get Qdrant client
                from core.qdrant_client import get_qdrant
                client = get_qdrant()
                
                # Store chunks in Qdrant
                points = []
                for chunk_data in chunks:
                    # Generate embedding
                    embedding = self.embedding_model.get_embeddings([chunk_data["content"]])[0]
                    
                    # Create point
                    point_id = str(uuid.uuid4())
                    points.append({
                        "id": point_id,
                        "vector": embedding,
                        "payload": {
                            **chunk_data["metadata"],
                            "content": chunk_data["content"],
                            "file_hash": file_hash,
                        }
                    })
                
                # Upsert points to Qdrant
                client.upsert(
                    collection_name="chess_knowledge",
                    points=points
                )
                
                logger.info(f"Successfully uploaded {len(chunks)} chunks for file: {file.filename}")
                
                return {
                    "filename": file.filename,
                    "chunks_created": len(chunks),
                    "file_hash": file_hash,
                    "content_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

# Global instance
document_ingestor = ChessDocumentIngestor() 