"""
RAG dependency provider for FastAPI.

This module provides dependency injection for the RAG manager,
ensuring a single instance is shared across all API requests.
"""

import logging
from typing import Optional
from fastapi import HTTPException

from ..rag.rag_manager import RAGManager


# Configure logging
logger = logging.getLogger(__name__)


# Global RAG manager instance
_rag_manager: Optional[RAGManager] = None


def set_rag_manager(rag_manager: RAGManager) -> None:
    """
    Set the global RAG manager instance.
    
    This should be called during application startup.
    
    Args:
        rag_manager: Initialized RAG manager instance
    """
    global _rag_manager
    _rag_manager = rag_manager
    logger.info("RAG manager set for dependency injection")


async def get_rag_manager() -> RAGManager:
    """
    FastAPI dependency to get the RAG manager instance.
    
    Returns:
        RAG manager instance
        
    Raises:
        HTTPException: If RAG manager is not initialized
    """
    global _rag_manager
    
    if _rag_manager is None:
        logger.error("RAG manager not initialized")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "RAG system not initialized",
                "error": "RAG manager is not available"
            }
        )
    
    if not _rag_manager.is_initialized:
        logger.error("RAG manager not properly initialized")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error", 
                "message": "RAG system not ready",
                "error": "RAG manager initialization incomplete"
            }
        )
    
    return _rag_manager


async def get_rag_manager_optional() -> Optional[RAGManager]:
    """
    FastAPI dependency to get the RAG manager instance (optional).
    
    Returns None if RAG manager is not available instead of raising an exception.
    This allows endpoints to gracefully degrade when RAG is not available.
    
    Returns:
        RAG manager instance or None
    """
    global _rag_manager
    
    if _rag_manager is None or not _rag_manager.is_initialized:
        logger.warning("RAG manager not available, returning None")
        return None
    
    return _rag_manager


def is_rag_available() -> bool:
    """
    Check if RAG system is available and ready.
    
    Returns:
        True if RAG is available, False otherwise
    """
    global _rag_manager
    
    return (
        _rag_manager is not None and 
        _rag_manager.is_initialized and 
        _rag_manager.is_ready
    )


def get_rag_status() -> dict:
    """
    Get the current status of the RAG system.
    
    Returns:
        Dictionary with RAG system status
    """
    global _rag_manager
    
    if _rag_manager is None:
        return {
            "status": "not_initialized",
            "is_available": False,
            "is_ready": False,
            "message": "RAG manager not set"
        }
    
    try:
        stats = _rag_manager.get_stats()
        return {
            "status": stats.get("status", "unknown"),
            "is_available": _rag_manager.is_initialized,
            "is_ready": _rag_manager.is_ready,
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "error",
            "is_available": False,
            "is_ready": False,
            "error": str(e)
        }


def cleanup_rag_manager() -> None:
    """
    Cleanup the RAG manager instance.
    
    This should be called during application shutdown.
    """
    global _rag_manager
    
    if _rag_manager is not None:
        try:
            _rag_manager.close()
            logger.info("RAG manager cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up RAG manager: {e}")
        finally:
            _rag_manager = None