"""
Enhanced embeddings with real Sentence Transformers implementation.

This module provides real embedding functionality using the sentence-transformers library
for production RAG processing.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from langchain.schema import Document

from .exceptions import EmbeddingError


# Configure logging
logger = logging.getLogger(__name__)


class EmbeddingModelType(Enum):
    """Supported embedding model types."""
    SENTENCE_TRANSFORMERS = "sentence-transformers"
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


@dataclass
class EmbeddingConfig:
    """Configuration for embedding models."""
    model_type: EmbeddingModelType = EmbeddingModelType.SENTENCE_TRANSFORMERS
    model_name: str = "all-MiniLM-L6-v2"
    model_kwargs: Optional[Dict[str, Any]] = None
    encode_kwargs: Optional[Dict[str, Any]] = None
    batch_size: int = 32
    max_length: Optional[int] = None
    normalize_embeddings: bool = True
    device: Optional[str] = None  # 'cpu', 'cuda', or None for auto-detection
    
    def __post_init__(self):
        """Set default values for optional parameters."""
        if self.model_kwargs is None:
            self.model_kwargs = {}
        if self.encode_kwargs is None:
            self.encode_kwargs = {
                'normalize_embeddings': self.normalize_embeddings,
                'batch_size': self.batch_size
            }


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.
    """
    
    def __init__(self, config: EmbeddingConfig):
        """
        Initialize the embedding provider.
        
        Args:
            config: Embedding configuration
        """
        self.config = config
        self._model = None
    
    @abstractmethod
    def load_model(self) -> None:
        """
        Load the embedding model.
        
        Raises:
            EmbeddingError: If model loading fails
        """
        pass
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Embedding dimension
        """
        pass
    
    @property
    def is_loaded(self) -> bool:
        """
        Check if the model is loaded.
        
        Returns:
            True if model is loaded, False otherwise
        """
        return self._model is not None


class SentenceTransformersProvider(EmbeddingProvider):
    """
    Real Sentence Transformers embedding provider.
    
    Uses the sentence-transformers library for generating embeddings.
    """
    
    def __init__(self, config: EmbeddingConfig):
        """Initialize the Sentence Transformers provider."""
        super().__init__(config)
        self._dimension = None
        logger.info(f"Initialized Sentence Transformers provider with model: {config.model_name}")
    
    def load_model(self) -> None:
        """
        Load Sentence Transformers model.
        
        Raises:
            EmbeddingError: If model loading fails
        """
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Loading Sentence Transformers model: {self.config.model_name}")
            
            # Load the model with configuration
            model_kwargs = self.config.model_kwargs.copy()
            if self.config.device:
                model_kwargs['device'] = self.config.device
            
            self._model = SentenceTransformer(
                self.config.model_name,
                **model_kwargs
            )
            
            # Get embedding dimension
            self._dimension = self._model.get_sentence_embedding_dimension()
            
            logger.info(f"Sentence Transformers model loaded successfully. Dimension: {self._dimension}")
            
        except ImportError as e:
            raise EmbeddingError(
                f"sentence-transformers library not available: {e}. "
                "Install with: pip install sentence-transformers"
            )
        except Exception as e:
            raise EmbeddingError(f"Failed to load Sentence Transformers model: {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for documents using Sentence Transformers.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not self.is_loaded:
            raise EmbeddingError("Model not loaded. Call load_model() first.")
        
        if not texts:
            return []
        
        try:
            logger.debug(f"Generating embeddings for {len(texts)} documents")
            
            # Generate embeddings with configuration
            embeddings = self._model.encode(
                texts,
                **self.config.encode_kwargs
            )
            
            # Convert to list of lists (numpy arrays to lists)
            embeddings_list = [embedding.tolist() for embedding in embeddings]
            
            logger.debug(f"Generated {len(embeddings_list)} embeddings")
            return embeddings_list
            
        except Exception as e:
            raise EmbeddingError(f"Failed to generate document embeddings: {e}")
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a query using Sentence Transformers.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not self.is_loaded:
            raise EmbeddingError("Model not loaded. Call load_model() first.")
        
        try:
            logger.debug(f"Generating embedding for query: {text[:50]}...")
            
            # Generate single embedding
            embedding = self._model.encode(
                [text],
                **self.config.encode_kwargs
            )[0]
            
            # Convert to list (numpy array to list)
            return embedding.tolist()
            
        except Exception as e:
            raise EmbeddingError(f"Failed to generate query embedding: {e}")
    
    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        if self._dimension is None:
            raise EmbeddingError("Model not loaded or dimension not available")
        return self._dimension


class PlaceholderEmbeddingProvider(EmbeddingProvider):
    """
    Placeholder embedding provider for development and testing.
    
    This implementation provides mock functionality for fallback scenarios.
    """
    
    def __init__(self, config: EmbeddingConfig):
        """Initialize the placeholder provider."""
        super().__init__(config)
        self._dimension = 384  # Common dimension for sentence transformers
        logger.warning(f"Using placeholder embedding provider with model: {config.model_name}")
    
    def load_model(self) -> None:
        """Mock model loading."""
        logger.info(f"Loading placeholder model: {self.config.model_name}")
        self._model = "placeholder_model"
        logger.info("Placeholder model loaded successfully")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for documents."""
        if not self.is_loaded:
            raise EmbeddingError("Model not loaded. Call load_model() first.")
        
        logger.debug(f"Generating mock embeddings for {len(texts)} documents")
        
        embeddings = []
        for i, text in enumerate(texts):
            # Create deterministic mock embedding based on text hash
            mock_embedding = [
                float((hash(text + str(j)) % 1000) / 1000.0) 
                for j in range(self._dimension)
            ]
            embeddings.append(mock_embedding)
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Generate mock embedding for a query."""
        if not self.is_loaded:
            raise EmbeddingError("Model not loaded. Call load_model() first.")
        
        logger.debug(f"Generating mock embedding for query: {text[:50]}...")
        
        mock_embedding = [
            float((hash(text + str(i)) % 1000) / 1000.0) 
            for i in range(self._dimension)
        ]
        
        return mock_embedding
    
    @property
    def dimension(self) -> int:
        """Get the mock embedding dimension."""
        return self._dimension


def create_embedding_provider(config: EmbeddingConfig) -> EmbeddingProvider:
    """
    Factory function to create embedding providers.
    
    Args:
        config: Embedding configuration
        
    Returns:
        Embedding provider instance
        
    Raises:
        EmbeddingError: If provider type is not supported
    """
    if config.model_type == EmbeddingModelType.SENTENCE_TRANSFORMERS:
        try:
            return SentenceTransformersProvider(config)
        except EmbeddingError as e:
            logger.warning(f"Failed to create Sentence Transformers provider: {e}")
            logger.warning("Falling back to placeholder provider")
            return PlaceholderEmbeddingProvider(config)
    else:
        raise EmbeddingError(
            f"Unsupported embedding model type: {config.model_type}",
            config.model_name
        )


def get_default_config() -> EmbeddingConfig:
    """
    Get default embedding configuration.
    
    Returns:
        Default EmbeddingConfig
    """
    return EmbeddingConfig(
        model_type=EmbeddingModelType.SENTENCE_TRANSFORMERS,
        model_name="all-MiniLM-L6-v2",
        batch_size=32,
        normalize_embeddings=True,
        device=None  # Auto-detect
    )


class EmbeddingManager:
    """
    Manager class for embedding operations.
    
    Provides high-level interface for embedding document chunks
    and managing embedding providers.
    """
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        Initialize the embedding manager.
        
        Args:
            config: Embedding configuration. Uses default if not provided.
        """
        self.config = config or get_default_config()
        self.provider = create_embedding_provider(self.config)
        self._is_initialized = False
    
    def initialize(self) -> None:
        """
        Initialize the embedding provider.
        
        Raises:
            EmbeddingError: If initialization fails
        """
        try:
            self.provider.load_model()
            self._is_initialized = True
            logger.info("Embedding manager initialized successfully")
        except Exception as e:
            raise EmbeddingError(f"Failed to initialize embedding manager: {e}")
    
    def embed_document_chunks(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for document chunks.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of dictionaries containing document content, metadata, and embeddings
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not self._is_initialized:
            raise EmbeddingError("Embedding manager not initialized. Call initialize() first.")
        
        if not documents:
            return []
        
        logger.info(f"Generating embeddings for {len(documents)} document chunks")
        
        try:
            # Process in batches to manage memory
            batch_size = self.config.batch_size
            embedded_documents = []
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                texts = [doc.page_content for doc in batch]
                
                # Generate embeddings for batch
                embeddings = self.provider.embed_documents(texts)
                
                # Combine documents with embeddings
                for doc, embedding in zip(batch, embeddings):
                    embedded_doc = {
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'embedding': embedding,
                        'embedding_model': self.config.model_name,
                        'embedding_dimension': self.provider.dimension
                    }
                    embedded_documents.append(embedded_doc)
                
                logger.debug(f"Processed batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
            
            logger.info(f"Successfully generated embeddings for {len(embedded_documents)} chunks")
            return embedded_documents
            
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embeddings: {e}")
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query string.
        
        Args:
            query: Query text
            
        Returns:
            Query embedding vector
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not self._is_initialized:
            raise EmbeddingError("Embedding manager not initialized. Call initialize() first.")
        
        try:
            return self.provider.embed_query(query)
        except Exception as e:
            raise EmbeddingError(f"Failed to generate query embedding: {e}")
    
    @property
    def is_initialized(self) -> bool:
        """Check if the manager is initialized."""
        return self._is_initialized
    
    @property
    def embedding_dimension(self) -> int:
        """Get the embedding dimension."""
        if not self._is_initialized:
            raise EmbeddingError("Embedding manager not initialized")
        return self.provider.dimension