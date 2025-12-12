"""
RAG (Retrieval-Augmented Generation) module for document processing.

This module provides functionality for loading, processing, and preparing
documents for RAG-based AI interactions.
"""

from .document_loader import DocumentLoader, DocumentMetadata
from .document_processor import DocumentProcessor, ProcessedDocument, ProcessingConfig
from .embeddings import (
    EmbeddingConfig, EmbeddingProvider, EmbeddingManager, EmbeddingModelType,
    PlaceholderEmbeddingProvider, create_embedding_provider, get_default_config
)
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
    'PlaceholderEmbeddingProvider',
    'create_embedding_provider',
    'get_default_config',
    
    # Exceptions
    'RAGError',
    'DocumentLoadError',
    'DocumentProcessingError',
    'EmbeddingError',
    'UnsupportedFileTypeError',
    'FileAccessError'
]