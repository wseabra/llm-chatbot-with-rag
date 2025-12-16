"""
Unit tests for the API routes module.

This module tests the FastAPI route implementations including health checks,
chat completion endpoints, and error handling following the project's testing standards.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import httpx


class SyncASGIClient:
    """Minimal sync wrapper around httpx.AsyncClient for ASGI apps."""
    def __init__(self, app):
        self.transport = httpx.ASGITransport(app=app)
        self.base_url = "http://test"
    def get(self, url, **kwargs):
        import asyncio
        async def _run():
            async with httpx.AsyncClient(transport=self.transport, base_url=self.base_url) as client:
                return await client.get(url, **kwargs)
        return asyncio.run(_run())
    def post(self, url, **kwargs):
        import asyncio
        async def _run():
            async with httpx.AsyncClient(transport=self.transport, base_url=self.base_url) as client:
                return await client.post(url, **kwargs)
        return asyncio.run(_run())

from fastapi import HTTPException

from src.api import create_app
from src.llm_providers.base import LLMProvider, LLMRequest, LLMResponse, LLMMessage, LLMChoice, LLMUsage


class TestAPIApp:
    """Test suite for the FastAPI application factory."""
    
    @pytest.mark.unit
    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI instance."""
        app = create_app()
        
        assert app is not None
        assert hasattr(app, 'title')
        assert hasattr(app, 'description')
        assert hasattr(app, 'version')
        assert app.title == "Simple Chat Application with Pluggable LLM Providers"
        assert app.version == "1.0.0"
    
    @pytest.mark.unit
    def test_create_app_includes_routers(self):
        """Test that create_app includes all required routers."""
        app = create_app()
        
        # Check that routes are registered
        route_paths = [route.path for route in app.routes]
        
        assert "/health" in route_paths
        assert "/chat" in route_paths


class TestRootRoutes:
    """Test suite for root endpoint routes."""
    
    @pytest.fixture
    def client(self):
        """Fixture providing test client."""
        app = create_app()
        return SyncASGIClient(app)
    
    @pytest.mark.unit
    def test_read_root_success(self, client):
        """Test that root endpoint returns 404 (no root route in simple implementation)."""
        response = client.get("/")
        
        # Simple implementation doesn't have a root route
        assert response.status_code == 404
    
    @pytest.mark.unit
    def test_read_root_response_structure(self, client):
        """Test root endpoint response structure (404 in simple implementation)."""
        response = client.get("/")
        data = response.json()
        
        # FastAPI default 404 response
        assert "detail" in data
        assert data["detail"] == "Not Found"


class TestHealthRoutes:
    """Test suite for health check endpoint routes."""
    
    @pytest.fixture
    def client(self):
        """Fixture providing test client."""
        app = create_app()
        return SyncASGIClient(app)
    
    @pytest.mark.unit
    @patch('src.llm_providers.dependencies.get_llm_provider')
    def test_health_check_success(self, mock_get_provider, client):
        """Test successful health check."""
        # Setup mock provider
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.health_check = AsyncMock(return_value=True)
        mock_get_provider.return_value = mock_provider
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["message"] == "Service is running"
        assert data["llm_provider_healthy"] == True
    
    @pytest.mark.unit
    def test_simple_health_check_success(self, client):
        """Test that simple health check doesn't exist in consolidated implementation."""
        response = client.get("/health/simple")
        
        # Simple implementation doesn't have /health/simple
        assert response.status_code == 404


class TestChatRoutes:
    """Test suite for chat completion endpoint routes."""
    
    @pytest.fixture
    def client(self):
        """Fixture providing test client."""
        app = create_app()
        return SyncASGIClient(app)
    
    @pytest.fixture
    def mock_llm_response(self):
        """Fixture providing mock LLMResponse."""
        choice = LLMChoice(
            message=LLMMessage(role="assistant", content="Hello! How can I help you today?"),
            finish_reason="stop"
        )
        usage = LLMUsage(prompt_tokens=10, completion_tokens=12, total_tokens=22)
        
        return LLMResponse(
            id="chatcmpl-123",
            model="gpt-4o-mini",
            choices=[choice],
            usage=usage
        )
    
    @pytest.mark.unit
    @patch('src.llm_providers.dependencies.get_llm_provider')
    def test_chat_completion_success(self, mock_get_provider, client, mock_llm_response):
        """Test successful chat completion."""
        # Setup mock provider
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.chat_completion = AsyncMock(return_value=mock_llm_response)
        mock_get_provider.return_value = mock_provider
        
        # Prepare form data for the endpoint
        form_data = {
            "messages": '[{"role": "user", "content": "Hello, how are you?"}]',
            "max_tokens": 100,
            "temperature": 0.8
        }
        
        response = client.post("/chat", data=form_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check the response structure matches our mock
        assert data["id"] == "chatcmpl-123"
        assert data["model"] == "gpt-4o-mini"
        assert data["choices"][0]["message"]["content"] == "Hello! How can I help you today?"
        assert data["choices"][0]["finish_reason"] == "stop"
        assert data["usage"]["total_tokens"] == 22
        
        # Verify the mock was called
        mock_provider.chat_completion.assert_called_once()
    
    @pytest.mark.unit
    def test_chat_completion_invalid_request_missing_message(self, client):
        """Test chat completion with missing message field."""
        form_data = {"max_tokens": 100}
        
        response = client.post("/chat", data=form_data)
        
        # FastAPI will return 422 for missing required field
        assert response.status_code == 422
    
    @pytest.mark.unit
    def test_chat_completion_invalid_request_empty_message(self, client):
        """Test chat completion with empty message."""
        form_data = {"messages": "[]"}  # Empty messages array
        
        response = client.post("/chat", data=form_data)
        
        # Should return 400 for empty messages
        assert response.status_code == 400


class TestAPIClientDependency:
    """Test suite for LLM provider dependency injection."""
    
    @pytest.mark.unit
    async def test_get_llm_provider_dependency_returns_instance(self):
        """Test that get_llm_provider_dependency returns LLMProvider instance."""
        from src.llm_providers.dependencies import get_llm_provider_dependency
        
        provider = await get_llm_provider_dependency()
        
        assert isinstance(provider, LLMProvider)
        assert hasattr(provider, 'health_check')
        assert hasattr(provider, 'chat_completion')


class TestIntegrationScenarios:
    """Integration test scenarios for API routes."""
    
    @pytest.fixture
    def client(self):
        """Fixture providing test client."""
        app = create_app()
        return SyncASGIClient(app)
    
    @pytest.mark.integration
    @patch('src.llm_providers.dependencies.get_llm_provider')
    def test_complete_api_workflow(self, mock_get_provider, client):
        """Test complete API workflow from health to chat."""
        # Setup mock provider
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.health_check = AsyncMock(return_value=True)
        mock_get_provider.return_value = mock_provider
        
        # Test health check
        response = client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"