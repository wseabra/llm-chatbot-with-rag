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
from src.flowApi.client import APIClient
from src.flowApi.models import HealthResponse, ChatCompletionResponse, ChatCompletionChoice, ChatCompletionUsage, ChatMessage
from src.flowApi.exceptions import (
    APIConnectionError, APITimeoutError, APIHTTPError, 
    APIResponseError, APIAuthenticationError, APIConfigurationError
)


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
        assert app.title == "FastAPI RAG Application"
        assert app.version == "1.0.0"
    
    @pytest.mark.unit
    def test_create_app_includes_routers(self):
        """Test that create_app includes all required routers."""
        app = create_app()
        
        # Check that routes are registered
        route_paths = [route.path for route in app.routes]
        
        assert "/" in route_paths
        assert "/health" in route_paths
        assert "/health/simple" in route_paths
        # Chat routes have prefix, so they appear as /chat/completion, etc.
        chat_routes = [path for path in route_paths if path.startswith("/chat")]
        assert len(chat_routes) >= 2  # At least /chat/completion and /chat/advanced


class TestRootRoutes:
    """Test suite for root endpoint routes."""
    
    @pytest.fixture
    def client(self):
        """Fixture providing test client."""
        app = create_app()
        return SyncASGIClient(app)
    
    @pytest.mark.unit
    def test_read_root_success(self, client):
        """Test successful root endpoint response."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "FastAPI RAG Application"
        assert data["status"] == "success"
        assert data["version"] == "1.0.0"
        assert "description" in data
        assert "endpoints" in data
        assert isinstance(data["endpoints"], dict)
    
    @pytest.mark.unit
    def test_read_root_response_structure(self, client):
        """Test root endpoint response structure."""
        response = client.get("/")
        data = response.json()
        
        required_fields = ["message", "status", "version", "description", "endpoints"]
        for field in required_fields:
            assert field in data
        
        # Check endpoints structure
        endpoints = data["endpoints"]
        expected_endpoints = ["health", "chat", "docs", "redoc"]
        for endpoint in expected_endpoints:
            assert endpoint in endpoints


class TestHealthRoutes:
    """Test suite for health check endpoint routes."""
    
    @pytest.fixture
    def client(self):
        """Fixture providing test client."""
        app = create_app()
        return SyncASGIClient(app)
    
    @pytest.fixture
    def mock_health_response(self):
        """Fixture providing mock HealthResponse."""
        return HealthResponse(
            result=True,
            timestamp="2025-12-11T15:01:23.000Z"
        )
    
    @pytest.fixture
    def mock_unhealthy_response(self):
        """Fixture providing mock unhealthy HealthResponse."""
        return HealthResponse(
            result=False,
            timestamp="2025-12-11T15:01:23.000Z"
        )
    
    @pytest.mark.unit
    def test_simple_health_check_success(self, client):
        """Test simple health check endpoint."""
        response = client.get("/health/simple")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["message"] == "Local service is running"
    
    @pytest.mark.unit
    @patch('src.api.routes.health.ClientManager.get_client')
    def test_health_check_success(self, mock_get_client, client, mock_health_response):
        """Test successful health check."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.health_check.return_value = mock_health_response
        mock_get_client.return_value = mock_client
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["message"] == "Service is running"
        assert data["external_api"]["status"] == "healthy"
        assert data["external_api"]["timestamp"] == "2025-12-11T15:01:23.000Z"
        
        # Verify API client was called correctly
        mock_client.health_check.assert_called_once_with()


class TestChatRoutes:
    """Test suite for chat completion endpoint routes."""
    
    @pytest.fixture
    def client(self):
        """Fixture providing test client."""
        app = create_app()
        return SyncASGIClient(app)
    
    @pytest.fixture
    def mock_chat_response(self):
        """Fixture providing mock ChatCompletionResponse."""
        message = ChatMessage(role="assistant", content="Hello! How can I help you today?")
        choice = ChatCompletionChoice(index=0, message=message, finish_reason="stop")
        usage = ChatCompletionUsage(prompt_tokens=10, completion_tokens=12, total_tokens=22)
        
        return ChatCompletionResponse(
            id="chatcmpl-123",
            object="chat.completion",
            created=1677652288,
            model="gpt-4o-mini",
            choices=[choice],
            usage=usage
        )
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_chat_completion_success(self, mock_get_client, client, mock_chat_response):
        """Test successful simple chat completion."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.chat_completion.return_value = mock_chat_response
        mock_get_client.return_value = mock_client
        
        request_data = {
            "message": "Hello, how are you?",
            "max_tokens": 100,
            "temperature": 0.8
        }
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "chatcmpl-123"
        assert data["model"] == "gpt-4o-mini"
        assert data["content"] == "Hello! How can I help you today?"
        assert data["finish_reason"] == "stop"
        assert data["usage"]["total_tokens"] == 22
        assert data["created"] == 1677652288
        
        # Verify API client was called correctly
        mock_client.chat_completion.assert_called_once_with(
            user_message="Hello, how are you?",
            max_tokens=100,
            temperature=0.8
        )
    
    @pytest.mark.unit
    def test_chat_completion_invalid_request_missing_message(self, client):
        """Test chat completion with missing message field."""
        request_data = {"max_tokens": 100}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 422  # FastAPI validation error
    
    @pytest.mark.unit
    def test_chat_completion_invalid_request_empty_message(self, client):
        """Test chat completion with empty message."""
        request_data = {"message": ""}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        # FastAPI validation error format
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert len(data["detail"]) > 0


class TestAPIClientDependency:
    """Test suite for APIClient dependency injection."""
    
    @pytest.mark.unit
    async def test_get_api_client_returns_instance(self):
        """Test that get_api_client dependency returns APIClient instance."""
        from src.api.routes.health import get_api_client
        
        # Since get_api_client is async, we need to run it in an event loop
        client = await get_api_client()
        
        assert isinstance(client, APIClient)
        assert hasattr(client, 'health_check')
        assert hasattr(client, 'chat_completion')
        assert hasattr(client, 'send_chat_request')


class TestIntegrationScenarios:
    """Integration test scenarios for API routes."""
    
    @pytest.fixture
    def client(self):
        """Fixture providing test client."""
        app = create_app()
        return SyncASGIClient(app)
    
    @pytest.mark.integration
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_complete_api_workflow(self, mock_get_client, client):
        """Test complete API workflow from root to health to chat."""
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        root_data = response.json()
        assert "endpoints" in root_data
        
        # Test simple health check
        response = client.get("/health/simple")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"