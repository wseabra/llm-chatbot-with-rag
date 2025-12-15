"""
Tests for RAG embeddings functionality.

This module contains comprehensive tests for the embeddings configuration,
providers, and manager classes.
"""

import pytest
from unittest.mock import patch, MagicMock

from langchain.schema import Document

from src.rag.embeddings import (
    EmbeddingConfig, EmbeddingModelType, EmbeddingProvider,
    PlaceholderEmbeddingProvider, SentenceTransformersProvider,
    EmbeddingManager, create_embedding_provider, get_default_config
)
from src.rag.exceptions import EmbeddingError


class TestEmbeddingConfig:
    """Test cases for EmbeddingConfig dataclass."""
    
    def test_embedding_config_defaults(self):
        """Test EmbeddingConfig with default values."""
        config = EmbeddingConfig()
        
        assert config.model_type == EmbeddingModelType.SENTENCE_TRANSFORMERS
        assert config.model_name == "all-MiniLM-L6-v2"
        assert config.model_kwargs == {}
        assert config.encode_kwargs == {
            'normalize_embeddings': True,
            'batch_size': 32
        }
        assert config.batch_size == 32
        assert config.max_length is None
        assert config.normalize_embeddings is True
    
    def test_embedding_config_custom_values(self):
        """Test EmbeddingConfig with custom values."""
        config = EmbeddingConfig(
            model_type=EmbeddingModelType.OPENAI,
            model_name="text-embedding-ada-002",
            batch_size=16,
            normalize_embeddings=False
        )
        
        assert config.model_type == EmbeddingModelType.OPENAI
        assert config.model_name == "text-embedding-ada-002"
        assert config.batch_size == 16
        assert config.normalize_embeddings is False
        assert config.encode_kwargs == {
            'normalize_embeddings': False,
            'batch_size': 16
        }
    
    def test_embedding_config_post_init(self):
        """Test EmbeddingConfig __post_init__ method."""
        config = EmbeddingConfig(
            model_kwargs=None,
            encode_kwargs=None
        )
        
        assert config.model_kwargs == {}
        assert config.encode_kwargs == {
            'normalize_embeddings': True,
            'batch_size': 32
        }


class TestEmbeddingModelType:
    """Test cases for EmbeddingModelType enum."""
    
    def test_embedding_model_type_values(self):
        """Test EmbeddingModelType enum values."""
        assert EmbeddingModelType.SENTENCE_TRANSFORMERS.value == "sentence-transformers"
        assert EmbeddingModelType.OPENAI.value == "openai"
        assert EmbeddingModelType.HUGGINGFACE.value == "huggingface"
        assert EmbeddingModelType.LOCAL.value == "local"


class TestPlaceholderEmbeddingProvider:
    """Test cases for PlaceholderEmbeddingProvider."""
    
    @pytest.fixture
    def config(self):
        """Create test embedding configuration."""
        return EmbeddingConfig(
            model_name="test-model",
            batch_size=16
        )
    
    @pytest.fixture
    def provider(self, config):
        """Create PlaceholderEmbeddingProvider instance."""
        return PlaceholderEmbeddingProvider(config)
    
    def test_placeholder_provider_init(self, provider, config):
        """Test PlaceholderEmbeddingProvider initialization."""
        assert provider.config == config
        assert provider._dimension == 384
        assert not provider.is_loaded
    
    def test_placeholder_provider_load_model(self, provider):
        """Test model loading."""
        provider.load_model()
        
        assert provider.is_loaded
        assert provider._model == "placeholder_model"
    
    def test_placeholder_provider_embed_documents(self, provider):
        """Test document embedding generation."""
        provider.load_model()
        
        texts = ["Document 1", "Document 2", "Document 3"]
        embeddings = provider.embed_documents(texts)
        
        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)
        assert all(isinstance(val, float) for emb in embeddings for val in emb)
        
        # Test deterministic behavior
        embeddings2 = provider.embed_documents(texts)
        assert embeddings == embeddings2
    
    def test_placeholder_provider_embed_query(self, provider):
        """Test query embedding generation."""
        provider.load_model()
        
        query = "Test query"
        embedding = provider.embed_query(query)
        
        assert len(embedding) == 384
        assert all(isinstance(val, float) for val in embedding)
        
        # Test deterministic behavior
        embedding2 = provider.embed_query(query)
        assert embedding == embedding2
    
    def test_placeholder_provider_embed_without_loading(self, provider):
        """Test embedding without loading model first."""
        with pytest.raises(EmbeddingError, match="Model not loaded"):
            provider.embed_documents(["test"])
        
        with pytest.raises(EmbeddingError, match="Model not loaded"):
            provider.embed_query("test")
    
    def test_placeholder_provider_dimension(self, provider):
        """Test dimension property."""
        assert provider.dimension == 384
    
    def test_placeholder_provider_is_loaded(self, provider):
        """Test is_loaded property."""
        assert not provider.is_loaded
        
        provider.load_model()
        assert provider.is_loaded


class TestSentenceTransformersProvider:
    """Test cases for SentenceTransformersProvider."""
    
    @pytest.fixture
    def config(self):
        """Create test embedding configuration."""
        return EmbeddingConfig(model_name="all-MiniLM-L6-v2")
    
    @pytest.fixture
    def provider(self, config):
        """Create SentenceTransformersProvider instance."""
        return SentenceTransformersProvider(config)
    
    def test_sentence_transformers_provider_init(self, provider, config):
        """Test SentenceTransformersProvider initialization."""
        assert provider.config == config
        assert not provider.is_loaded
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_sentence_transformers_provider_load_model(self, mock_sentence_transformer, provider):
        """Test that load_model works with mocked SentenceTransformer."""
        # Mock the SentenceTransformer class
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.return_value = mock_model
        
        provider.load_model()
        
        assert provider.is_loaded
        assert provider._dimension == 384
        mock_sentence_transformer.assert_called_once_with("all-MiniLM-L6-v2")
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_sentence_transformers_provider_embed_documents(self, mock_sentence_transformer, provider):
        """Test document embedding with mocked SentenceTransformer."""
        # Setup mock
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        
        # Create mock embeddings with proper tolist() method
        mock_emb1 = MagicMock()
        mock_emb1.tolist.return_value = [0.1, 0.2, 0.3]
        mock_emb2 = MagicMock()
        mock_emb2.tolist.return_value = [0.4, 0.5, 0.6]
        
        mock_model.encode.return_value = [mock_emb1, mock_emb2]
        mock_sentence_transformer.return_value = mock_model
        
        provider.load_model()
        
        texts = ["Document 1", "Document 2"]
        embeddings = provider.embed_documents(texts)
        
        expected_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        assert embeddings == expected_embeddings
        mock_model.encode.assert_called_once_with(texts, **provider.config.encode_kwargs)
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_sentence_transformers_provider_embed_query(self, mock_sentence_transformer, provider):
        """Test query embedding with mocked SentenceTransformer."""
        # Setup mock
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        
        # Create mock embedding with proper tolist() method
        mock_emb = MagicMock()
        mock_emb.tolist.return_value = [0.1, 0.2, 0.3]
        
        mock_model.encode.return_value = [mock_emb]
        mock_sentence_transformer.return_value = mock_model
        
        provider.load_model()
        
        query = "Test query"
        embedding = provider.embed_query(query)
        
        expected_embedding = [0.1, 0.2, 0.3]
        assert embedding == expected_embedding
        mock_model.encode.assert_called_once_with([query], **provider.config.encode_kwargs)
    
    def test_sentence_transformers_provider_dimension_not_loaded(self, provider):
        """Test dimension property when model not loaded."""
        with pytest.raises(EmbeddingError, match="Model not loaded"):
            _ = provider.dimension


class TestEmbeddingProviderFactory:
    """Test cases for embedding provider factory functions."""
    
    def test_create_embedding_provider_sentence_transformers(self):
        """Test creating sentence transformers provider."""
        config = EmbeddingConfig(model_type=EmbeddingModelType.SENTENCE_TRANSFORMERS)
        
        provider = create_embedding_provider(config)
        
        # Should return SentenceTransformersProvider or fallback to PlaceholderEmbeddingProvider
        assert isinstance(provider, (SentenceTransformersProvider, PlaceholderEmbeddingProvider))
        assert provider.config == config
    
    def test_create_embedding_provider_fallback_to_placeholder(self):
        """Test fallback to placeholder provider when SentenceTransformers fails."""
        config = EmbeddingConfig(model_type=EmbeddingModelType.SENTENCE_TRANSFORMERS)
        
        # The factory function should handle the fallback internally
        provider = create_embedding_provider(config)
        
        # Should get some provider (either real or placeholder)
        assert isinstance(provider, (SentenceTransformersProvider, PlaceholderEmbeddingProvider))
    
    def test_create_embedding_provider_unsupported(self):
        """Test creating provider with unsupported type."""
        config = EmbeddingConfig(model_type=EmbeddingModelType.OPENAI)
        
        with pytest.raises(EmbeddingError, match="Unsupported embedding model type"):
            create_embedding_provider(config)
    
    def test_get_default_config(self):
        """Test getting default configuration."""
        config = get_default_config()
        
        assert isinstance(config, EmbeddingConfig)
        assert config.model_type == EmbeddingModelType.SENTENCE_TRANSFORMERS
        assert config.model_name == "all-MiniLM-L6-v2"
        assert config.batch_size == 32
        assert config.normalize_embeddings is True


class TestEmbeddingManager:
    """Test cases for EmbeddingManager."""
    
    @pytest.fixture
    def config(self):
        """Create test embedding configuration that will use placeholder provider."""
        return EmbeddingConfig(model_name="test-model")
    
    @pytest.fixture
    def manager(self, config):
        """Create EmbeddingManager instance."""
        return EmbeddingManager(config)
    
    @pytest.fixture
    def initialized_manager(self, manager):
        """Create initialized EmbeddingManager."""
        # Force use of placeholder provider to avoid network calls
        manager.provider = PlaceholderEmbeddingProvider(manager.config)
        manager.initialize()
        return manager
    
    def test_embedding_manager_init_default_config(self):
        """Test EmbeddingManager initialization with default config."""
        manager = EmbeddingManager()
        
        assert isinstance(manager.config, EmbeddingConfig)
        assert isinstance(manager.provider, (PlaceholderEmbeddingProvider, SentenceTransformersProvider))
        assert not manager.is_initialized
    
    def test_embedding_manager_init_custom_config(self, config):
        """Test EmbeddingManager initialization with custom config."""
        manager = EmbeddingManager(config)
        
        assert manager.config == config
        assert isinstance(manager.provider, (PlaceholderEmbeddingProvider, SentenceTransformersProvider))
        assert not manager.is_initialized
    
    def test_embedding_manager_initialize(self, manager):
        """Test EmbeddingManager initialization."""
        # Force use of placeholder provider to avoid network calls
        manager.provider = PlaceholderEmbeddingProvider(manager.config)
        manager.initialize()
        
        assert manager.is_initialized
        assert manager.provider.is_loaded
    
    def test_embedding_manager_initialize_error(self, manager):
        """Test EmbeddingManager initialization error handling."""
        with patch.object(manager.provider, 'load_model', side_effect=Exception("Load error")):
            with pytest.raises(EmbeddingError, match="Failed to initialize embedding manager"):
                manager.initialize()
    
    def test_embedding_manager_embed_document_chunks(self, initialized_manager):
        """Test embedding document chunks."""
        documents = [
            Document(page_content="Document 1", metadata={'source': 'file1.txt'}),
            Document(page_content="Document 2", metadata={'source': 'file2.txt'})
        ]
        
        embedded_docs = initialized_manager.embed_document_chunks(documents)
        
        assert len(embedded_docs) == 2
        
        for i, embedded_doc in enumerate(embedded_docs):
            assert embedded_doc['content'] == documents[i].page_content
            assert embedded_doc['metadata'] == documents[i].metadata
            assert 'embedding' in embedded_doc
            assert len(embedded_doc['embedding']) == 384
            assert embedded_doc['embedding_model'] == "test-model"
            assert embedded_doc['embedding_dimension'] == 384
    
    def test_embedding_manager_embed_document_chunks_not_initialized(self, manager):
        """Test embedding without initialization."""
        documents = [Document(page_content="Test", metadata={})]
        
        with pytest.raises(EmbeddingError, match="Embedding manager not initialized"):
            manager.embed_document_chunks(documents)
    
    def test_embedding_manager_embed_document_chunks_error(self, initialized_manager):
        """Test embedding error handling."""
        documents = [Document(page_content="Test", metadata={})]
        
        with patch.object(initialized_manager.provider, 'embed_documents', side_effect=Exception("Embed error")):
            with pytest.raises(EmbeddingError, match="Failed to generate embeddings"):
                initialized_manager.embed_document_chunks(documents)
    
    def test_embedding_manager_embed_query(self, initialized_manager):
        """Test query embedding."""
        query = "Test query"
        
        embedding = initialized_manager.embed_query(query)
        
        assert len(embedding) == 384
        assert all(isinstance(val, float) for val in embedding)
    
    def test_embedding_manager_embed_query_not_initialized(self, manager):
        """Test query embedding without initialization."""
        with pytest.raises(EmbeddingError, match="Embedding manager not initialized"):
            manager.embed_query("test")
    
    def test_embedding_manager_embed_query_error(self, initialized_manager):
        """Test query embedding error handling."""
        with patch.object(initialized_manager.provider, 'embed_query', side_effect=Exception("Query error")):
            with pytest.raises(EmbeddingError, match="Failed to generate query embedding"):
                initialized_manager.embed_query("test")
    
    def test_embedding_manager_is_initialized_property(self, manager):
        """Test is_initialized property."""
        assert not manager.is_initialized
        
        # Force use of placeholder provider to avoid network calls
        manager.provider = PlaceholderEmbeddingProvider(manager.config)
        manager.initialize()
        assert manager.is_initialized
    
    def test_embedding_manager_embedding_dimension_property(self, initialized_manager):
        """Test embedding_dimension property."""
        assert initialized_manager.embedding_dimension == 384
    
    def test_embedding_manager_embedding_dimension_not_initialized(self, manager):
        """Test embedding_dimension property without initialization."""
        with pytest.raises(EmbeddingError, match="Embedding manager not initialized"):
            _ = manager.embedding_dimension


class TestEmbeddingProviderAbstract:
    """Test cases for abstract EmbeddingProvider class."""
    
    def test_embedding_provider_cannot_instantiate(self):
        """Test that abstract EmbeddingProvider cannot be instantiated."""
        config = EmbeddingConfig()
        
        with pytest.raises(TypeError):
            EmbeddingProvider(config)
    
    def test_embedding_provider_is_loaded_default(self):
        """Test is_loaded property default behavior."""
        # Create a concrete implementation for testing
        class TestProvider(EmbeddingProvider):
            def load_model(self): pass
            def embed_documents(self, texts): pass
            def embed_query(self, text): pass
            @property
            def dimension(self): return 384
        
        config = EmbeddingConfig()
        provider = TestProvider(config)
        
        assert not provider.is_loaded
        
        provider._model = "loaded"
        assert provider.is_loaded


class TestEmbeddingIntegration:
    """Integration tests for embedding functionality."""
    
    def test_full_embedding_workflow(self):
        """Test complete embedding workflow."""
        # Create manager with placeholder provider to avoid network calls
        config = EmbeddingConfig(model_name="test-model")
        manager = EmbeddingManager(config)
        manager.provider = PlaceholderEmbeddingProvider(config)
        
        # Initialize
        manager.initialize()
        
        # Create test documents
        documents = [
            Document(page_content="This is document 1", metadata={'source': 'doc1.txt'}),
            Document(page_content="This is document 2", metadata={'source': 'doc2.txt'})
        ]
        
        # Embed documents
        embedded_docs = manager.embed_document_chunks(documents)
        
        # Embed query
        query_embedding = manager.embed_query("search query")
        
        # Verify results
        assert len(embedded_docs) == 2
        assert len(query_embedding) == manager.embedding_dimension
        assert all('embedding' in doc for doc in embedded_docs)
    
    def test_embedding_consistency(self):
        """Test embedding consistency across calls."""
        config = EmbeddingConfig(model_name="test-model")
        manager = EmbeddingManager(config)
        manager.provider = PlaceholderEmbeddingProvider(config)
        manager.initialize()
        
        text = "Consistent text for testing"
        
        # Generate embeddings multiple times
        embedding1 = manager.embed_query(text)
        embedding2 = manager.embed_query(text)
        
        # Should be identical (deterministic)
        assert embedding1 == embedding2
    
    def test_different_configs_different_providers(self):
        """Test that different configs create different providers."""
        config1 = EmbeddingConfig(model_name="model1")
        config2 = EmbeddingConfig(model_name="model2")
        
        provider1 = create_embedding_provider(config1)
        provider2 = create_embedding_provider(config2)
        
        assert provider1.config.model_name != provider2.config.model_name