"""
FastAPI application factory and configuration.

This module contains the FastAPI application factory function and
application-level configuration.
"""

from fastapi import FastAPI

from .routes import health, chat, root


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="FastAPI RAG Application",
        description="A FastAPI application with RAG capabilities using flowApi for AI interactions",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Include routers
    app.include_router(root.router)
    app.include_router(health.router)
    app.include_router(chat.router)
    
    return app