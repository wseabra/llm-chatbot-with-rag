"""
Unit tests for the API module.

This module tests the API client functionality including health checks,
error handling, response validation, and authentication following the project's testing standards.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import json

# Import the API classes
from src.api import (
    APIClient,
    HealthResponse,
    APIError,
    APIConnectionError,
    APITimeoutError,
    APIHTTPError,
    APIResponseError,
    APIAuthenticationError,
    APIConfigurationError
)


class TestHealthResponse:
    """Test suite for the HealthResponse model."""
    
    @pytest.fixture
    def valid_health_data(self):
        """Fixture providing valid health response data."""
        return {
            'result': True,
            'timestamp': '2025-12-11T15:01:23.000Z'
        }
    
    @pytest.fixture
    def invalid_health_data_missing_fields(self):
        """Fixture providing health data with missing fields."""
        return {
            'result': True
            # Missing timestamp
        }
    
    @pytest.fixture
    def invalid_health_data_wrong_types(self):
        """Fixture providing health data with wrong field types."""
        return {
            'result': 'true',  # Should be boolean
            'timestamp': 1234567890  # Should be string
        }
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_response_from_dict_valid(self, valid_health_data):
        """Test creating HealthResponse from valid dictionary."""
        response = HealthResponse.from_dict(valid_health_data)
        
        assert isinstance(response, HealthResponse)
        assert response.result is True
        assert response.timestamp == '2025-12-11T15:01:23.000Z'
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_response_from_dict_missing_fields(self, invalid_health_data_missing_fields):
        """Test HealthResponse creation with missing required fields."""
        with pytest.raises(APIResponseError) as exc_info:
            HealthResponse.from_dict(invalid_health_data_missing_fields)
        
        assert "Missing required fields" in str(exc_info.value)
        assert "timestamp" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_response_from_dict_wrong_types(self, invalid_health_data_wrong_types):
        """Test HealthResponse creation with wrong field types."""
        with pytest.raises(APIResponseError) as exc_info:
            HealthResponse.from_dict(invalid_health_data_wrong_types)
        
        assert "Invalid 'result' field type" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_response_from_dict_invalid_input(self):
        """Test HealthResponse creation with invalid input types."""
        invalid_inputs = [
            None,
            "not a dict",
            123,
            [],
            set()
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises(APIResponseError) as exc_info:
                HealthResponse.from_dict(invalid_input)
            
            assert "Invalid response format" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_response_to_dict(self, valid_health_data):
        """Test converting HealthResponse to dictionary."""
        response = HealthResponse.from_dict(valid_health_data)
        result_dict = response.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict == valid_health_data
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_response_str_representation(self, valid_health_data):
        """Test string representation of HealthResponse."""
        response = HealthResponse.from_dict(valid_health_data)
        str_repr = str(response)
        
        assert "Health Status: healthy" in str_repr
        assert "2025-12-11T15:01:23.000Z" in str_repr
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_response_str_unhealthy(self):
        """Test string representation for unhealthy response."""
        unhealthy_data = {
            'result': False,
            'timestamp': '2025-12-11T15:01:23.000Z'
        }
        response = HealthResponse.from_dict(unhealthy_data)
        str_repr = str(response)
        
        assert "Health Status: unhealthy" in str_repr
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_response_whitespace_handling(self):
        """Test handling of whitespace in timestamp."""
        data_with_whitespace = {
            'result': True,
            'timestamp': '  2025-12-11T15:01:23.000Z  '
        }
        response = HealthResponse.from_dict(data_with_whitespace)
        
        assert response.timestamp == '2025-12-11T15:01:23.000Z'
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_health_response_empty_timestamp(self):
        """Test handling of empty timestamp."""
        empty_timestamp_data = {
            'result': True,
            'timestamp': ''
        }
        
        with pytest.raises(APIResponseError) as exc_info:
            HealthResponse.from_dict(empty_timestamp_data)
        
        assert "Invalid timestamp" in str(exc_info.value)


class TestAPIClient:
    """Test suite for the APIClient class."""
    
    @pytest.fixture
    def api_client(self):
        """Fixture providing APIClient instance."""
        return APIClient()
    
    @pytest.fixture
    def custom_api_client(self):
        """Fixture providing APIClient with custom configuration."""
        return APIClient(base_url="https://custom.api.com", timeout=60)
    
    @pytest.fixture
    def mock_response_success(self):
        """Fixture providing successful mock response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': True,
            'timestamp': '2025-12-11T15:01:23.000Z'
        }
        mock_response.text = json.dumps({
            'result': True,
            'timestamp': '2025-12-11T15:01:23.000Z'
        })
        return mock_response
    
    @pytest.fixture
    def mock_response_http_error(self):
        """Fixture providing HTTP error mock response."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        return mock_response
    
    @pytest.fixture
    def mock_response_invalid_json(self):
        """Fixture providing invalid JSON mock response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Invalid JSON response"
        return mock_response
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_client_init_default(self):
        """Test APIClient initialization with default parameters."""
        client = APIClient()
        
        assert client.base_url == "https://flow.ciandt.com"
        assert client.timeout == 30
        assert hasattr(client, 'session')
        assert isinstance(client.session, requests.Session)
        assert client._auth_response is None
        assert not client.is_authenticated()
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_client_init_custom(self, custom_api_client):
        """Test APIClient initialization with custom parameters."""
        assert custom_api_client.base_url == "https://custom.api.com"
        assert custom_api_client.timeout == 60
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_client_init_base_url_trailing_slash(self):
        """Test APIClient handles base URL with trailing slash."""
        client = APIClient(base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_client_init_with_config(self):
        """Test APIClient initialization with config."""
        mock_config = Mock()
        client = APIClient(config=mock_config)
        
        assert client.config is mock_config
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_client_session_headers(self, api_client):
        """Test that APIClient sets proper default headers."""
        headers = api_client.session.headers
        
        assert 'User-Agent' in headers
        assert 'Accept' in headers
        assert 'Content-Type' in headers
        assert headers['Accept'] == 'application/json'
        assert headers['Content-Type'] == 'application/json'
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.api.client.requests.Session.request')
    def test_health_check_success(self, mock_request, api_client, mock_response_success):
        """Test successful health check."""
        mock_request.return_value = mock_response_success
        
        result = api_client.health_check()
        
        assert isinstance(result, HealthResponse)
        assert result.result is True
        assert result.timestamp == '2025-12-11T15:01:23.000Z'
        
        # Verify the request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert args[0] == 'GET'
        assert '/ai-orchestration-api/v1/health' in args[1]
        assert kwargs['timeout'] == 30
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.api.client.requests.Session.request')
    def test_health_check_http_error(self, mock_request, api_client, mock_response_http_error):
        """Test health check with HTTP error response."""
        mock_request.return_value = mock_response_http_error
        
        with pytest.raises(APIHTTPError) as exc_info:
            api_client.health_check()
        
        assert exc_info.value.status_code == 500
        assert "HTTP 500 error" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.api.client.requests.Session.request')
    def test_health_check_auth_error_401(self, mock_request, api_client):
        """Test health check with 401 authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_request.return_value = mock_response
        
        with pytest.raises(APIAuthenticationError) as exc_info:
            api_client.health_check()
        
        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.api.client.requests.Session.request')
    def test_health_check_auth_error_403(self, mock_request, api_client):
        """Test health check with 403 authorization error."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_request.return_value = mock_response
        
        with pytest.raises(APIAuthenticationError) as exc_info:
            api_client.health_check()
        
        assert exc_info.value.status_code == 403
        assert "Access forbidden" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.api.client.requests.Session.request')
    def test_health_check_connection_error(self, mock_request, api_client):
        """Test health check with connection error."""
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(APIConnectionError) as exc_info:
            api_client.health_check()
        
        assert "Failed to connect" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.api.client.requests.Session.request')
    def test_health_check_timeout_error(self, mock_request, api_client):
        """Test health check with timeout error."""
        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(APITimeoutError) as exc_info:
            api_client.health_check()
        
        assert "timed out" in str(exc_info.value)
        assert exc_info.value.timeout == 30
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.api.client.requests.Session.request')
    def test_health_check_invalid_json(self, mock_request, api_client, mock_response_invalid_json):
        """Test health check with invalid JSON response."""
        mock_request.return_value = mock_response_invalid_json
        
        with pytest.raises(APIResponseError) as exc_info:
            api_client.health_check()
        
        assert "Invalid JSON response" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.api.client.requests.Session.request')
    def test_health_check_custom_timeout(self, mock_request, mock_response_success):
        """Test health check with custom timeout."""
        client = APIClient(timeout=60)
        mock_request.return_value = mock_response_success
        
        client.health_check()
        
        # Verify timeout was passed correctly
        args, kwargs = mock_request.call_args
        assert kwargs['timeout'] == 60
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_client_context_manager(self):
        """Test APIClient as context manager."""
        with APIClient() as client:
            assert isinstance(client, APIClient)
            assert hasattr(client, 'session')
        
        # Session should be closed after context exit
        # Note: We can't easily test this without mocking, but the structure is correct
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_client_close(self, api_client):
        """Test APIClient close method."""
        # Mock the session to verify close is called
        api_client.session = Mock()
        
        api_client.close()
        
        api_client.session.close.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_client_close_clears_auth(self, api_client):
        """Test APIClient close method clears authentication."""
        # Set up some auth state
        api_client._auth_response = Mock()
        api_client.session.headers['Authorization'] = 'Bearer token123'
        
        api_client.close()
        
        assert api_client._auth_response is None
        assert 'Authorization' not in api_client.session.headers
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.api.client.requests.Session.request')
    def test_make_request_url_construction(self, mock_request, api_client, mock_response_success):
        """Test URL construction in _make_request method."""
        mock_request.return_value = mock_response_success
        
        # Test different endpoint formats
        test_cases = [
            '/health',
            'health',
            '/api/v1/health',
            'api/v1/health'
        ]
        
        for endpoint in test_cases:
            api_client._make_request('GET', endpoint)
            
            args, kwargs = mock_request.call_args
            url = args[1]
            assert url.startswith('https://flow.ciandt.com/')
            assert endpoint.lstrip('/') in url


class TestAPIExceptions:
    """Test suite for API exception classes."""
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_error_base(self):
        """Test base APIError exception."""
        error = APIError("Test error", status_code=400)
        
        assert str(error) == "API Error 400: Test error"
        assert error.message == "Test error"
        assert error.status_code == 400
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_error_no_status_code(self):
        """Test APIError without status code."""
        error = APIError("Test error")
        
        assert str(error) == "API Error: Test error"
        assert error.status_code is None
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_connection_error(self):
        """Test APIConnectionError exception."""
        error = APIConnectionError("Connection failed")
        
        assert "Connection failed" in str(error)
        assert isinstance(error, APIError)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_timeout_error(self):
        """Test APITimeoutError exception."""
        error = APITimeoutError("Timeout occurred", timeout=30.0)
        
        assert "Timeout occurred" in str(error)
        assert "30.0s" in str(error)
        assert error.timeout == 30.0
        assert isinstance(error, APIError)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_timeout_error_no_timeout(self):
        """Test APITimeoutError without timeout value."""
        error = APITimeoutError("Timeout occurred")
        
        assert "Timeout occurred" in str(error)
        assert error.timeout is None
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_http_error(self):
        """Test APIHTTPError exception."""
        error = APIHTTPError("Not found", status_code=404, response_text="Page not found")
        
        assert "API HTTP Error 404: Not found" in str(error)
        assert error.status_code == 404
        assert error.response_text == "Page not found"
        assert isinstance(error, APIError)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_response_error(self):
        """Test APIResponseError exception."""
        error = APIResponseError("Invalid format", response_data='{"invalid": json}')
        
        assert "Invalid format" in str(error)
        assert error.response_data == '{"invalid": json}'
        assert isinstance(error, APIError)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_authentication_error(self):
        """Test APIAuthenticationError exception."""
        error = APIAuthenticationError("Auth failed", status_code=401, auth_type="token")
        
        assert "API Authentication Error 401 (token): Auth failed" in str(error)
        assert error.status_code == 401
        assert error.auth_type == "token"
        assert isinstance(error, APIError)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_authentication_error_no_details(self):
        """Test APIAuthenticationError without optional details."""
        error = APIAuthenticationError("Auth failed")
        
        assert "API Authentication Error: Auth failed" in str(error)
        assert error.status_code is None
        assert error.auth_type is None
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_configuration_error(self):
        """Test APIConfigurationError exception."""
        error = APIConfigurationError("Missing config", config_key="CLIENT_ID")
        
        assert "API Configuration Error (key: CLIENT_ID): Missing config" in str(error)
        assert error.config_key == "CLIENT_ID"
        assert isinstance(error, APIError)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_configuration_error_no_key(self):
        """Test APIConfigurationError without config key."""
        error = APIConfigurationError("Config error")
        
        assert "API Configuration Error: Config error" in str(error)
        assert error.config_key is None


class TestAPIIntegration:
    """Integration tests for API module."""
    
    @pytest.mark.integration
    @pytest.mark.api
    @patch('src.api.client.requests.Session.request')
    def test_complete_health_check_workflow(self, mock_request):
        """Integration test for complete health check workflow."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': True,
            'timestamp': '2025-12-11T15:01:23.000Z'
        }
        mock_request.return_value = mock_response
        
        # Test complete workflow
        with APIClient() as client:
            health = client.health_check()
            
            # Verify response
            assert isinstance(health, HealthResponse)
            assert health.result is True
            assert health.timestamp == '2025-12-11T15:01:23.000Z'
            
            # Verify string representation
            assert "healthy" in str(health)
            
            # Verify dict conversion
            health_dict = health.to_dict()
            assert health_dict['result'] is True
            assert health_dict['timestamp'] == '2025-12-11T15:01:23.000Z'


# Parametrized tests for different scenarios
class TestAPIParametrized:
    """Parametrized tests for different API scenarios."""
    
    @pytest.mark.parametrize("status_code,expected_exception", [
        (400, APIHTTPError),
        (401, APIAuthenticationError),
        (403, APIAuthenticationError),
        (404, APIHTTPError),
        (500, APIHTTPError),
        (502, APIHTTPError),
        (503, APIHTTPError),
    ])
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.api.client.requests.Session.request')
    def test_http_error_status_codes(self, mock_request, status_code, expected_exception):
        """Test different HTTP error status codes."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = f"Error {status_code}"
        mock_request.return_value = mock_response
        
        client = APIClient()
        
        with pytest.raises(expected_exception) as exc_info:
            client.health_check()
        
        assert exc_info.value.status_code == status_code
    
    @pytest.mark.parametrize("exception_class,expected_api_exception", [
        (requests.exceptions.ConnectionError, APIConnectionError),
        (requests.exceptions.Timeout, APITimeoutError),
        (requests.exceptions.RequestException, APIConnectionError),
    ])
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.api.client.requests.Session.request')
    def test_requests_exception_mapping(self, mock_request, exception_class, expected_api_exception):
        """Test mapping of requests exceptions to API exceptions."""
        mock_request.side_effect = exception_class("Test error")
        
        client = APIClient()
        
        with pytest.raises(expected_api_exception):
            client.health_check()
    
    @pytest.mark.parametrize("base_url,expected_normalized", [
        ("https://api.example.com", "https://api.example.com"),
        ("https://api.example.com/", "https://api.example.com"),
        ("https://api.example.com///", "https://api.example.com"),
    ])
    @pytest.mark.unit
    @pytest.mark.api
    def test_base_url_normalization(self, base_url, expected_normalized):
        """Test base URL normalization."""
        client = APIClient(base_url=base_url)
        assert client.base_url == expected_normalized