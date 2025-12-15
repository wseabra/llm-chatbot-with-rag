"""
Enhanced FastAPI application factory with RAG initialization.

This module contains the FastAPI application factory function with
RAG system initialization at startup.
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import health, chat, root
from .rag_dependency import set_rag_manager, cleanup_rag_manager, get_rag_status
from ..config.config import Config
from ..rag.rag_manager import RAGManager, RAGConfig
from ..rag.exceptions import RAGError


# Configure logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting FastAPI RAG Application...")
    
    try:
        # Load configuration
        config = Config()
        config_dict = config.load_config()
        
        logger.info("Configuration loaded successfully")
        
        # Validate RAG folder
        if not config.validate_rag_folder():
            logger.error(f"RAG folder is not valid: {config_dict.get('RAG_FOLDER', 'Not set')}")
            logger.warning("RAG system will not be available")
        else:
            # Create RAG configuration
            rag_config = RAGConfig(
                chunk_size=config_dict.get('RAG_CHUNK_SIZE', 1000),
                chunk_overlap=config_dict.get('RAG_CHUNK_OVERLAP', 200),
                embedding_model=config_dict.get('RAG_EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
                embedding_batch_size=config_dict.get('RAG_EMBEDDING_BATCH_SIZE', 32),
                vector_db_path=config_dict.get('RAG_VECTOR_DB_PATH', './data/chroma_db'),
                collection_name=config_dict.get('RAG_COLLECTION_NAME', 'documents'),
                similarity_threshold=config_dict.get('RAG_SIMILARITY_THRESHOLD', 0.7),
                max_context_chunks=config_dict.get('RAG_MAX_CONTEXT_CHUNKS', 5),
                context_separator=config_dict.get('RAG_CONTEXT_SEPARATOR', '\n\n---\n\n'),
                include_source_info=config_dict.get('RAG_INCLUDE_SOURCE_INFO', True)
            )
            
            # Initialize RAG manager
            logger.info("Initializing RAG system...")
            rag_manager = RAGManager(
                documents_folder=config_dict['RAG_FOLDER'],
                config=rag_config
            )
            
            # Initialize RAG components
            await rag_manager.initialize()
            logger.info("RAG components initialized successfully")
            
            # Index all documents
            if config_dict.get('RAG_ENABLE_AUTO_INDEXING', True):
                logger.info("Starting document indexing...")
                indexing_stats = await rag_manager.index_all_documents()
                
                logger.info(f"Document indexing completed: {indexing_stats}")
                
                if indexing_stats['total_chunks'] == 0:
                    logger.warning("No documents were indexed. RAG will have no context to work with.")
                else:
                    logger.info(f"Successfully indexed {indexing_stats['total_documents']} documents "
                               f"into {indexing_stats['total_chunks']} chunks")
            else:
                logger.info("Auto-indexing disabled, skipping document indexing")
            
            # Set RAG manager for dependency injection
            set_rag_manager(rag_manager)
            
            logger.info("RAG system startup completed successfully")
        
    except RAGError as e:
        logger.error(f"RAG initialization failed: {e}")
        logger.warning("Application will continue without RAG functionality")
    except Exception as e:
        logger.error(f"Unexpected error during RAG initialization: {e}")
        logger.warning("Application will continue without RAG functionality")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI RAG Application...")
    
    try:
        cleanup_rag_manager()
        logger.info("RAG system cleanup completed")
    except Exception as e:
        logger.error(f"Error during RAG cleanup: {e}")
    
    logger.info("Application shutdown completed")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application with RAG integration.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="FastAPI RAG Application",
        description="A FastAPI application with RAG capabilities using flowApi for AI interactions",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Add CORS middleware to handle frontend requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React dev server default
            "http://localhost:5173",  # Vite dev server default
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(root.router)
    app.include_router(health.router)
    app.include_router(chat.router)
    
    @app.get("/rag/status", tags=["rag"])
    async def rag_status():
        """
        Get RAG system status.
        
        Returns:
            dict: RAG system status and statistics
        """
        return get_rag_status()
    
    return app