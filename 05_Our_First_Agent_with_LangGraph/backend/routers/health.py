from fastapi import APIRouter
from backend.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Health check endpoint for uptime monitoring"""
    logger.debug("Health check requested")
    return {"status": "ok"} 