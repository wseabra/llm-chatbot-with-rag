"""
Root endpoint routes.

This module contains the root endpoint and basic application information routes.
"""

from fastapi import APIRouter

router = APIRouter(tags=["root"])


@router.get("/")
async def read_root():
    """
    Root endpoint that returns application information.
    
    Returns:
        dict: Welcome message with application information
    """
    return {
        "message": "FastAPI RAG Application", 
        "status": "success",
        "version": "1.0.0",
        "description": "A FastAPI application with RAG capabilities using flowApi",
        "endpoints": {
            "health": "/health - Health check endpoints",
            "chat": "/chat - Chat completion endpoints",
            "docs": "/docs - Interactive API documentation",
            "redoc": "/redoc - Alternative API documentation"
        }
    }