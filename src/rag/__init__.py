"""
RAG (Retrieval-Augmented Generation) module for document processing.

This module provides comprehensive functionality for loading, processing,
embedding, storing, and retrieving documents for RAG-based AI interactions.
"""

from .document_loader import DocumentLoader, DocumentMetadata
from .document_processor import DocumentProcessor, ProcessedDocument, ProcessingConfig
from .embeddings import (
    EmbeddingConfig, EmbeddingProvider, EmbeddingManager, EmbeddingModelType,
    SentenceTransformersProvider, PlaceholderEmbeddingProvider, 
    create_embedding_provider, get_default_config
)
from .vector_store import VectorStore, SearchResult
from .rag_manager import RAGManager, RAGConfig
from .exceptions import (
    RAGError,
    DocumentLoadError,
    DocumentProcessingError,
    EmbeddingError,
    UnsupportedFileTypeError,
    FileAccessError
)

__all__ = [
    # Document Loading
    'DocumentLoader',
    'DocumentMetadata',
    
    # Document Processing
    'DocumentProcessor',
    'ProcessedDocument', 
    'ProcessingConfig',
    
    # Embeddings
    'EmbeddingConfig',
    'EmbeddingProvider',
    'EmbeddingManager',
    'EmbeddingModelType',
    'SentenceTransformersProvider',
    'PlaceholderEmbeddingProvider',
    'create_embedding_provider',
    'get_default_config',
    
    # Vector Store
    'VectorStore',
    'SearchResult',
    
    # RAG Manager
    'RAGManager',
    'RAGConfig',
    
    # Exceptions
    'RAGError',
    'DocumentLoadError',
    'DocumentProcessingError',
    'EmbeddingError',
    'UnsupportedFileTypeError',
    'FileAccessError'
]