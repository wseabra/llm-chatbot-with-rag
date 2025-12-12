"""
Unit tests for the API routes module.

This module tests the FastAPI route implementations including health checks,
chat completion endpoints, and error handling following the project's testing standards.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
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
        return TestClient(app)
    
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
        return TestClient(app)
    
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
    
    @pytest.mark.unit
    @patch('src.api.routes.health.ClientManager.get_client')
    def test_health_check_unhealthy_external_api(self, mock_get_client, client, mock_unhealthy_response):
        """Test health check with unhealthy external API."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.health_check.return_value = mock_unhealthy_response
        mock_get_client.return_value = mock_client
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"  # Local service is still healthy
        assert data["external_api"]["status"] == "unhealthy"
    
    @pytest.mark.unit
    @patch('src.api.routes.health.ClientManager.get_client')
    def test_health_check_connection_error(self, mock_get_client, client):
        """Test health check with connection error."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.health_check.side_effect = APIConnectionError("Connection failed")
        mock_get_client.return_value = mock_client
        
        response = client.get("/health")
        
        assert response.status_code == 503
        data = response.json()
        
        assert data["detail"]["status"] == "degraded"
        assert "External API is unreachable" in data["detail"]["message"]
        assert data["detail"]["local_service"] == "healthy"
    
    @pytest.mark.unit
    @patch('src.api.routes.health.ClientManager.get_client')
    def test_health_check_timeout_error(self, mock_get_client, client):
        """Test health check with timeout error."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.health_check.side_effect = APITimeoutError("Request timed out", timeout=30)
        mock_get_client.return_value = mock_client
        
        response = client.get("/health")
        
        assert response.status_code == 503
        data = response.json()
        
        assert data["detail"]["status"] == "degraded"
        assert "External API is unreachable" in data["detail"]["message"]
    
    @pytest.mark.unit
    @patch('src.api.routes.health.ClientManager.get_client')
    def test_health_check_http_error(self, mock_get_client, client):
        """Test health check with HTTP error."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.health_check.side_effect = APIHTTPError(
            "Server error",
            status_code=500,
            response_text="Internal Server Error"
        )
        mock_get_client.return_value = mock_client
        
        response = client.get("/health")
        
        assert response.status_code == 502
        data = response.json()
        
        assert data["detail"]["status"] == "degraded"
        assert "External API returned an error" in data["detail"]["message"]
    
    @pytest.mark.unit
    @patch('src.api.routes.health.ClientManager.get_client')
    def test_health_check_response_error(self, mock_get_client, client):
        """Test health check with response parsing error."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.health_check.side_effect = APIResponseError(
            "Invalid response format",
            response_data="invalid json"
        )
        mock_get_client.return_value = mock_client
        
        response = client.get("/health")
        
        assert response.status_code == 502
        data = response.json()
        
        assert data["detail"]["status"] == "degraded"
        assert "External API returned an error" in data["detail"]["message"]
    
    @pytest.mark.unit
    @patch('src.api.routes.health.ClientManager.get_client')
    def test_health_check_unexpected_error(self, mock_get_client, client):
        """Test health check with unexpected error."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.health_check.side_effect = Exception("Unexpected error")
        mock_get_client.return_value = mock_client
        
        response = client.get("/health")
        
        assert response.status_code == 500
        data = response.json()
        
        assert data["detail"]["status"] == "error"
        assert "Unexpected error during health check" in data["detail"]["message"]


class TestChatRoutes:
    """Test suite for chat completion endpoint routes."""
    
    @pytest.fixture
    def client(self):
        """Fixture providing test client."""
        app = create_app()
        return TestClient(app)
    
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
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_chat_completion_default_parameters(self, mock_get_client, client, mock_chat_response):
        """Test chat completion with default parameters."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.chat_completion.return_value = mock_chat_response
        mock_get_client.return_value = mock_client
        
        request_data = {"message": "Hello"}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 200
        
        # Verify default parameters were used
        mock_client.chat_completion.assert_called_once_with(
            user_message="Hello",
            max_tokens=4096,
            temperature=0.7
        )
    
    @pytest.mark.unit
    def test_chat_completion_invalid_request_missing_message(self, client):
        """Test chat completion with missing message field."""
        request_data = {"max_tokens": 100}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 422  # FastAPI validation error
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_chat_completion_invalid_request_empty_message(self, mock_get_client, client):
        """Test chat completion with empty message."""
        # Setup mock to raise ValueError for empty message
        mock_client = Mock(spec=APIClient)
        mock_client.chat_completion.side_effect = ValueError("user_message cannot be empty")
        mock_get_client.return_value = mock_client
        
        request_data = {"message": ""}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        # FastAPI validation error format
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert len(data["detail"]) > 0
        assert "user_message cannot be empty" in str(data["detail"])
    
    @pytest.mark.unit
    def test_chat_completion_invalid_request_parameters(self, client):
        """Test chat completion with invalid parameters."""
        # Test invalid max_tokens
        request_data = {"message": "Hello", "max_tokens": 0}
        response = client.post("/chat/completion", json=request_data)
        assert response.status_code == 422
        
        # Test invalid temperature
        request_data = {"message": "Hello", "temperature": 3.0}
        response = client.post("/chat/completion", json=request_data)
        assert response.status_code == 422
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_chat_completion_value_error(self, mock_get_client, client):
        """Test chat completion with ValueError from API client."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.chat_completion.side_effect = ValueError("Invalid message")
        mock_get_client.return_value = mock_client
        
        request_data = {"message": "Hello"}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        
        assert data["detail"]["status"] == "error"
        assert "Invalid request parameters" in data["detail"]["message"]
        assert "Invalid message" in data["detail"]["error"]
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_chat_completion_configuration_error(self, mock_get_client, client):
        """Test chat completion with configuration error."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.chat_completion.side_effect = APIConfigurationError(
            "Missing CLIENT_ID",
            config_key="CLIENT_ID"
        )
        mock_get_client.return_value = mock_client
        
        request_data = {"message": "Hello"}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        
        assert data["detail"]["status"] == "error"
        assert "Configuration error" in data["detail"]["message"]
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_chat_completion_authentication_error(self, mock_get_client, client):
        """Test chat completion with authentication error."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.chat_completion.side_effect = APIAuthenticationError(
            "Authentication failed",
            status_code=401
        )
        mock_get_client.return_value = mock_client
        
        request_data = {"message": "Hello"}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 401
        data = response.json()
        
        assert data["detail"]["status"] == "error"
        assert "Authentication failed" in data["detail"]["message"]
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_chat_completion_connection_error(self, mock_get_client, client):
        """Test chat completion with connection error."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.chat_completion.side_effect = APIConnectionError("Connection failed")
        mock_get_client.return_value = mock_client
        
        request_data = {"message": "Hello"}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 503
        data = response.json()
        
        assert data["detail"]["status"] == "error"
        assert "External API is unreachable" in data["detail"]["message"]
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_advanced_chat_completion_success(self, mock_get_client, client, mock_chat_response):
        """Test successful advanced chat completion."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.send_chat_request.return_value = mock_chat_response
        mock_get_client.return_value = mock_client
        
        request_data = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ],
            "max_tokens": 500,
            "temperature": 0.5,
            "stream": False,
            "allowed_models": ["gpt-4o-mini"]
        }
        
        response = client.post("/chat/advanced", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return the complete response
        assert data["id"] == "chatcmpl-123"
        assert data["model"] == "gpt-4o-mini"
        assert len(data["choices"]) == 1
        assert data["usage"]["total_tokens"] == 22
        
        # Verify API client was called correctly
        mock_client.send_chat_request.assert_called_once()
        call_args = mock_client.send_chat_request.call_args[0][0]
        
        assert len(call_args.messages) == 2
        assert call_args.messages[0].role == "system"
        assert call_args.messages[1].role == "user"
        assert call_args.max_tokens == 500
        assert call_args.temperature == 0.5
        
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_advanced_chat_completion_default_parameters(self, mock_get_client, client, mock_chat_response):
        """Test advanced chat completion with default parameters."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.send_chat_request.return_value = mock_chat_response
        mock_get_client.return_value = mock_client
        
        request_data = {
            "messages": [{"role": "user", "content": "Hello!"}]
        }
        
        response = client.post("/chat/advanced", json=request_data)
        
        assert response.status_code == 200
        
        # Verify default parameters were used
        call_args = mock_client.send_chat_request.call_args[0][0]
        assert call_args.max_tokens == 4096
        assert call_args.temperature == 0.7
        assert call_args.stream is False
        assert call_args.allowed_models == ["gpt-4o-mini"]
    
    @pytest.mark.unit
    def test_advanced_chat_completion_invalid_request_missing_messages(self, client):
        """Test advanced chat completion with missing messages field."""
        request_data = {"max_tokens": 100}
        
        response = client.post("/chat/advanced", json=request_data)
        
        assert response.status_code == 422  # FastAPI validation error
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_advanced_chat_completion_invalid_request_empty_messages(self, mock_get_client, client):
        """Test advanced chat completion with empty messages list."""
        # Setup mock to raise ValueError for empty messages
        mock_client = Mock(spec=APIClient)
        mock_client.send_chat_request.side_effect = ValueError("messages cannot be empty")
        mock_get_client.return_value = mock_client
        
        request_data = {"messages": []}
        
        response = client.post("/chat/advanced", json=request_data)
        
        assert response.status_code == 422  # Pydantic validation error
    
    @pytest.mark.unit
    def test_advanced_chat_completion_invalid_message_structure(self, client):
        """Test advanced chat completion with invalid message structure."""
        request_data = {
            "messages": [{"role": "user"}]  # Missing content
        }
        
        response = client.post("/chat/advanced", json=request_data)
        
        assert response.status_code == 422  # FastAPI validation error
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_advanced_chat_completion_invalid_role(self, mock_get_client, client):
        """Test advanced chat completion with invalid role."""
        # Setup mock to raise ValueError for invalid role
        mock_client = Mock(spec=APIClient)
        mock_client.send_chat_request.side_effect = ValueError("Invalid role: invalid")
        mock_get_client.return_value = mock_client
        
        request_data = {
            "messages": [{"role": "invalid", "content": "Hello"}]
        }
        
        response = client.post("/chat/advanced", json=request_data)
        
        assert response.status_code == 422  # Pydantic validation error


class TestChatRoutesErrorHandling:
    """Test suite for chat routes error handling scenarios."""
    
    @pytest.fixture
    def client(self):
        """Fixture providing test client."""
        app = create_app()
        return TestClient(app)
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_chat_completion_timeout_error(self, mock_get_client, client):
        """Test chat completion with timeout error."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.chat_completion.side_effect = APITimeoutError("Request timed out", timeout=30)
        mock_get_client.return_value = mock_client
        
        request_data = {"message": "Hello"}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 503
        data = response.json()
        
        assert data["detail"]["status"] == "error"
        assert "External API is unreachable" in data["detail"]["message"]
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_chat_completion_http_error(self, mock_get_client, client):
        """Test chat completion with HTTP error."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.chat_completion.side_effect = APIHTTPError(
            "Bad request",
            status_code=400,
            response_text="Invalid parameters"
        )
        mock_get_client.return_value = mock_client
        
        request_data = {"message": "Hello"}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 502
        data = response.json()
        
        assert data["detail"]["status"] == "error"
        assert "External API returned an error" in data["detail"]["message"]
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_chat_completion_response_error(self, mock_get_client, client):
        """Test chat completion with response parsing error."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.chat_completion.side_effect = APIResponseError(
            "Invalid response format",
            response_data="malformed json"
        )
        mock_get_client.return_value = mock_client
        
        request_data = {"message": "Hello"}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 502
        data = response.json()
        
        assert data["detail"]["status"] == "error"
        assert "External API returned an error" in data["detail"]["message"]
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_chat_completion_unexpected_error(self, mock_get_client, client):
        """Test chat completion with unexpected error."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.chat_completion.side_effect = Exception("Unexpected error")
        mock_get_client.return_value = mock_client
        
        request_data = {"message": "Hello"}
        
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        
        assert data["detail"]["status"] == "error"
        assert "Unexpected error during chat completion" in data["detail"]["message"]
    
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_advanced_chat_completion_value_error(self, mock_get_client, client):
        """Test advanced chat completion with ValueError."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        mock_client.send_chat_request.side_effect = ValueError("Invalid request data")
        mock_get_client.return_value = mock_client
        
        request_data = {
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = client.post("/chat/advanced", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        
        assert data["detail"]["status"] == "error"
        assert "Invalid request parameters" in data["detail"]["message"]


class TestAPIClientDependency:
    """Test suite for APIClient dependency injection."""
    
    @pytest.mark.unit
    def test_get_api_client_returns_instance(self):
        """Test that get_api_client dependency returns APIClient instance."""
        from src.api.routes.health import get_api_client
        
        # Since get_api_client is async, we need to run it in an event loop
        client = asyncio.run(get_api_client())
        
        assert isinstance(client, APIClient)
        assert hasattr(client, 'health_check')
        assert hasattr(client, 'chat_completion')
        assert hasattr(client, 'send_chat_request')
    
    @pytest.mark.unit
    def test_get_api_client_chat_returns_instance(self):
        """Test that get_api_client dependency in chat routes returns APIClient instance."""
        from src.api.routes.chat import get_api_client
        
        # Since get_api_client is async, we need to run it in an event loop
        client = asyncio.run(get_api_client())
        
        assert isinstance(client, APIClient)


class TestIntegrationScenarios:
    """Integration test scenarios for API routes."""
    
    @pytest.fixture
    def client(self):
        """Fixture providing test client."""
        app = create_app()
        return TestClient(app)
    
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
        
        # Test chat completion with mocked external API
        # Setup mock response
        mock_client = Mock(spec=APIClient)
        mock_response = Mock()
        mock_response.id = "test-123"
        mock_response.model = "gpt-4o-mini"
        mock_response.get_first_choice_content.return_value = "Hello there!"
        mock_response.choices = [Mock(finish_reason="stop")]
        mock_response.usage = Mock()
        mock_response.usage.to_dict.return_value = {"total_tokens": 15}
        mock_response.created = 1677652288
        
        mock_client.chat_completion.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        request_data = {"message": "Hello"}
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == 200
        chat_data = response.json()
        assert chat_data["content"] == "Hello there!"
    

class TestAPIParametrized:
    """Parametrized tests for different API scenarios."""
    
    @pytest.fixture
    def client(self):
        """Fixture providing test client."""
        app = create_app()
        return TestClient(app)
    
    @pytest.mark.parametrize("exception_class,expected_status,expected_message", [
        (APIAuthenticationError, 401, "Authentication failed"),
        (APIConnectionError, 503, "External API is unreachable"),
        (APITimeoutError, 503, "External API is unreachable"),
        (APIResponseError, 502, "External API returned an error"),
        (APIConfigurationError, 500, "Configuration error"),
    ])
    @pytest.mark.unit
    @patch('src.api.routes.chat.ClientManager.get_client')
    def test_chat_completion_error_mapping(
        self, mock_get_client, client, exception_class, expected_status, expected_message
    ):
        """Test mapping of different exceptions to HTTP status codes in chat completion."""
        # Setup async mock
        mock_client = Mock(spec=APIClient)
        
        # Create exception with proper parameters
        if exception_class == APIHTTPError:
            mock_client.chat_completion.side_effect = exception_class(
                "Test error", status_code=500, response_text="Server Error"
            )
        else:
            mock_client.chat_completion.side_effect = exception_class("Test error")
        
        mock_get_client.return_value = mock_client
        
        request_data = {"message": "Hello"}
        response = client.post("/chat/completion", json=request_data)
        
        assert response.status_code == expected_status
        data = response.json()
        assert expected_message in data["detail"]["message"]
    
    @pytest.mark.parametrize("max_tokens,temperature,should_pass", [
        (1, 0.0, True),      # Minimum valid values
        (8192, 2.0, True),   # Maximum valid values
        (4096, 0.7, True),   # Default values
        (0, 0.7, False),     # Invalid max_tokens
        (4096, -0.1, False), # Invalid temperature (too low)
        (4096, 2.1, False),  # Invalid temperature (too high)
    ])
    @pytest.mark.unit
    def test_chat_completion_parameter_validation(self, client, max_tokens, temperature, should_pass):
        """Test parameter validation for chat completion."""
        request_data = {
            "message": "Hello",
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = client.post("/chat/completion", json=request_data)
        
        if should_pass:
            # Should pass validation (might fail later due to no mock, but that's OK)
            assert response.status_code != 422
        else:
            # Should fail validation
            assert response.status_code == 422
    
    @pytest.mark.parametrize("role,content,should_pass", [
        ("user", "Hello", True),
        ("assistant", "Hi there", True),
        ("system", "You are helpful", True),
        ("invalid", "Hello", False),
        ("user", "", False),
        ("", "Hello", False),
    ])
    @pytest.mark.unit
    def test_advanced_chat_message_validation(self, client, role, content, should_pass):
        """Test message validation for advanced chat completion."""
        request_data = {
            "messages": [{"role": role, "content": content}]
        }
        
        response = client.post("/chat/advanced", json=request_data)
        
        if should_pass:
            # Should pass validation (might fail later due to no mock, but that's OK)
            assert response.status_code != 422
        else:
            # Should fail validation (either 422 for FastAPI or 400 for business logic)
            assert response.status_code in [400, 422]