"""
Unit tests for the API authentication functionality.

This module tests the authentication models, client authentication methods,
and error handling following the project's testing standards.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import json
import time

# Import the API classes
from src.flowApi import (
    APIClient,
    AuthRequest,
    AuthResponse,
    APIAuthenticationError,
    APIConfigurationError,
    APIConnectionError,
    APITimeoutError,
    APIHTTPError,
    APIResponseError
)


class TestAuthRequest:
    """Test suite for the AuthRequest model."""
    
    @pytest.fixture
    def valid_auth_data(self):
        """Fixture providing valid authentication request data."""
        return {
            'client_id': 'test_client_123',
            'client_secret': 'test_secret_456',
            'app_to_access': 'llm-api'
        }
    
    @pytest.fixture
    def minimal_auth_data(self):
        """Fixture providing minimal authentication request data."""
        return {
            'client_id': 'client',
            'client_secret': 'secret'
        }
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_request_creation_valid(self, valid_auth_data):
        """Test creating AuthRequest with valid data."""
        auth_req = AuthRequest(**valid_auth_data)
        
        assert auth_req.client_id == 'test_client_123'
        assert auth_req.client_secret == 'test_secret_456'
        assert auth_req.app_to_access == 'llm-api'
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_request_default_app_to_access(self, minimal_auth_data):
        """Test AuthRequest with default app_to_access."""
        auth_req = AuthRequest(**minimal_auth_data)
        
        assert auth_req.client_id == 'client'
        assert auth_req.client_secret == 'secret'
        assert auth_req.app_to_access == 'llm-api'
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_request_whitespace_handling(self):
        """Test AuthRequest handles whitespace properly."""
        auth_req = AuthRequest(
            client_id='  client_id  ',
            client_secret='  secret  ',
            app_to_access='  llm-api  '
        )
        
        assert auth_req.client_id == 'client_id'
        assert auth_req.client_secret == 'secret'
        assert auth_req.app_to_access == 'llm-api'
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_request_to_dict(self, valid_auth_data):
        """Test AuthRequest serialization to dictionary."""
        auth_req = AuthRequest(**valid_auth_data)
        result = auth_req.to_dict()
        
        expected = {
            'clientId': 'test_client_123',
            'clientSecret': 'test_secret_456',
            'appToAccess': 'llm-api'
        }
        
        assert result == expected
        assert isinstance(result, dict)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_request_str_representation(self, valid_auth_data):
        """Test AuthRequest string representation (should not expose secret)."""
        auth_req = AuthRequest(**valid_auth_data)
        str_repr = str(auth_req)
        
        assert 'test_client_123' in str_repr
        assert 'llm-api' in str_repr
        assert 'test_secret_456' not in str_repr  # Secret should not be exposed
    
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.parametrize("invalid_field,invalid_value", [
        ("client_id", ""),
        ("client_id", "   "),
        ("client_id", None),
        ("client_secret", ""),
        ("client_secret", "   "),
        ("client_secret", None),
        ("app_to_access", ""),
        ("app_to_access", "   "),
    ])
    def test_auth_request_invalid_values(self, invalid_field, invalid_value):
        """Test AuthRequest validation with invalid values."""
        valid_data = {
            'client_id': 'client',
            'client_secret': 'secret',
            'app_to_access': 'llm-api'
        }
        valid_data[invalid_field] = invalid_value
        
        with pytest.raises(ValueError) as exc_info:
            AuthRequest(**valid_data)
        
        # Check that the field name is mentioned in the error message
        assert invalid_field in str(exc_info.value).lower()


class TestAuthResponse:
    """Test suite for the AuthResponse model."""
    
    @pytest.fixture
    def valid_auth_response_data(self):
        """Fixture providing valid authentication response data."""
        return {
            'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token',
            'expires_in': 3599
        }
    
    @pytest.fixture
    def invalid_auth_response_missing_fields(self):
        """Fixture providing auth response data with missing fields."""
        return {
            'access_token': 'token123'
            # Missing expires_in
        }
    
    @pytest.fixture
    def invalid_auth_response_wrong_types(self):
        """Fixture providing auth response data with wrong field types."""
        return {
            'access_token': 123,  # Should be string
            'expires_in': 'not_a_number'  # Should be int
        }
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_response_from_dict_valid(self, valid_auth_response_data):
        """Test creating AuthResponse from valid dictionary."""
        auth_resp = AuthResponse.from_dict(valid_auth_response_data)
        
        assert isinstance(auth_resp, AuthResponse)
        assert auth_resp.access_token == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token'
        assert auth_resp.expires_in == 3599
        assert auth_resp._created_at is not None
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_response_from_dict_missing_fields(self, invalid_auth_response_missing_fields):
        """Test AuthResponse creation with missing required fields."""
        with pytest.raises(APIResponseError) as exc_info:
            AuthResponse.from_dict(invalid_auth_response_missing_fields)
        
        assert "Missing required fields" in str(exc_info.value)
        assert "expires_in" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_response_from_dict_wrong_types(self, invalid_auth_response_wrong_types):
        """Test AuthResponse creation with wrong field types."""
        with pytest.raises(APIResponseError) as exc_info:
            AuthResponse.from_dict(invalid_auth_response_wrong_types)
        
        assert "Invalid 'access_token' field type" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_response_from_dict_numeric_string_expires_in(self):
        """Test AuthResponse handles numeric string for expires_in."""
        data = {
            'access_token': 'token123',
            'expires_in': '3600'  # String that can be converted to int
        }
        
        auth_resp = AuthResponse.from_dict(data)
        assert auth_resp.expires_in == 3600
        assert isinstance(auth_resp.expires_in, int)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_response_to_dict(self, valid_auth_response_data):
        """Test converting AuthResponse to dictionary."""
        auth_resp = AuthResponse.from_dict(valid_auth_response_data)
        result = auth_resp.to_dict()
        
        assert isinstance(result, dict)
        assert result == valid_auth_response_data
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_response_is_expired_fresh_token(self, valid_auth_response_data):
        """Test is_expired with fresh token."""
        auth_resp = AuthResponse.from_dict(valid_auth_response_data)
        
        assert not auth_resp.is_expired()
        assert not auth_resp.is_expired(buffer_seconds=60)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_response_is_expired_with_buffer(self):
        """Test is_expired with buffer seconds."""
        data = {
            'access_token': 'token123',
            'expires_in': 30  # Short expiration
        }
        auth_resp = AuthResponse.from_dict(data)
        
        # Should not be expired without buffer
        assert not auth_resp.is_expired(buffer_seconds=0)
        
        # Should be expired with large buffer
        assert auth_resp.is_expired(buffer_seconds=60)
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_response_time_until_expiry(self, valid_auth_response_data):
        """Test time_until_expiry calculation."""
        auth_resp = AuthResponse.from_dict(valid_auth_response_data)
        
        time_left = auth_resp.time_until_expiry()
        
        # Should be close to expires_in (allowing for small time differences)
        assert 3590 <= time_left <= 3599
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_response_get_authorization_header(self, valid_auth_response_data):
        """Test authorization header generation."""
        auth_resp = AuthResponse.from_dict(valid_auth_response_data)
        header = auth_resp.get_authorization_header()
        
        expected = f"Bearer {valid_auth_response_data['access_token']}"
        assert header == expected
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_response_str_representation(self, valid_auth_response_data):
        """Test AuthResponse string representation."""
        auth_resp = AuthResponse.from_dict(valid_auth_response_data)
        str_repr = str(auth_resp)
        
        # Should show token preview but not full token
        assert "eyJhbGci..." in str_repr
        assert "expires_in=3599s" in str_repr
        assert "remaining=" in str_repr
        # Should not show full token for security
        assert valid_auth_response_data['access_token'] not in str_repr
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_auth_response_invalid_input_types(self):
        """Test AuthResponse creation with invalid input types."""
        invalid_inputs = [
            None,
            "not a dict",
            123,
            [],
            set()
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises(APIResponseError) as exc_info:
                AuthResponse.from_dict(invalid_input)
            
            assert "Invalid response format" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    @pytest.mark.parametrize("invalid_expires_in", [
        0,
        -1,
        -3600
    ])
    def test_auth_response_invalid_expires_in_values(self, invalid_expires_in):
        """Test AuthResponse with invalid expires_in values."""
        data = {
            'access_token': 'token123',
            'expires_in': invalid_expires_in
        }
        
        with pytest.raises(APIResponseError) as exc_info:
            AuthResponse.from_dict(data)
        
        assert "Invalid expires_in value" in str(exc_info.value)


class TestAPIClientAuthentication:
    """Test suite for APIClient authentication functionality."""
    
    @pytest.fixture
    def api_client(self):
        """Fixture providing APIClient instance."""
        return APIClient()
    
    @pytest.fixture
    def mock_config(self):
        """Fixture providing mock config."""
        mock_config = Mock()
        mock_config.load_config.return_value = {
            'CLIENT_ID': 'test_client_123',
            'CLIENT_SECRET': 'test_secret_456',
            'RAG_FOLDER': '/path/to/rag'
        }
        return mock_config
    
    @pytest.fixture
    def mock_auth_response_success(self):
        """Fixture providing successful authentication response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token',
            'expires_in': 3599
        }
        mock_response.text = json.dumps({
            'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token',
            'expires_in': 3599
        })
        return mock_response
    
    @pytest.fixture
    def mock_auth_response_error(self):
        """Fixture providing authentication error response."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        return mock_response
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_api_client_init_with_config(self, mock_config):
        """Test APIClient initialization with config."""
        client = APIClient(config=mock_config)
        
        assert client.config is mock_config
        assert client._auth_response is None
        assert not client.is_authenticated()
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.flowApi.client.requests.Session.request')
    def test_authenticate_success(self, mock_request, mock_config, mock_auth_response_success):
        """Test successful authentication."""
        mock_request.return_value = mock_auth_response_success
        
        client = APIClient(config=mock_config)
        auth_response = client.authenticate()
        
        # Verify authentication response
        assert isinstance(auth_response, AuthResponse)
        assert auth_response.access_token == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token'
        assert auth_response.expires_in == 3599
        
        # Verify client state
        assert client.is_authenticated()
        assert client.get_auth_info() is not None
        
        # Verify session headers
        assert 'Authorization' in client.session.headers
        assert client.session.headers['Authorization'].startswith('Bearer ')
        
        # Verify the request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert args[0] == 'POST'
        assert '/auth-engine-api/v1/api-key/token' in args[1]
        
        # Verify request body
        request_data = json.loads(kwargs['data'])
        assert request_data['clientId'] == 'test_client_123'
        assert request_data['clientSecret'] == 'test_secret_456'
        assert request_data['appToAccess'] == 'llm-api'
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.flowApi.client.requests.Session.request')
    def test_authenticate_http_error(self, mock_request, mock_config, mock_auth_response_error):
        """Test authentication with HTTP error."""
        mock_request.return_value = mock_auth_response_error
        
        client = APIClient(config=mock_config)
        
        with pytest.raises(APIAuthenticationError) as exc_info:
            client.authenticate()
        
        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value)
        
        # Verify client state is cleared
        assert not client.is_authenticated()
        assert client.get_auth_info() is None
        assert 'Authorization' not in client.session.headers
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_authenticate_config_error(self):
        """Test authentication with configuration error."""
        # Mock config that raises an error
        mock_config = Mock()
        mock_config.load_config.side_effect = EnvironmentError("Missing CLIENT_ID")
        
        client = APIClient(config=mock_config)
        
        with pytest.raises(APIConfigurationError) as exc_info:
            client.authenticate()
        
        assert "Failed to load configuration values" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.flowApi.client.APIClient._load_config')
    def test_authenticate_no_config(self, mock_load_config):
        """Test authentication without config (should auto-load)."""
        # Mock the _load_config method to raise an error
        mock_load_config.side_effect = APIConfigurationError("No config available")
        
        client = APIClient()
        
        # Should try to load config automatically and fail
        with pytest.raises(APIConfigurationError):
            client.authenticate()
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.flowApi.client.requests.Session.request')
    def test_authenticate_invalid_json_response(self, mock_request, mock_config):
        """Test authentication with invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Invalid JSON response"
        mock_request.return_value = mock_response
        
        client = APIClient(config=mock_config)
        
        with pytest.raises(APIResponseError) as exc_info:
            client.authenticate()
        
        assert "Invalid JSON response from authentication endpoint" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.flowApi.client.requests.Session.request')
    def test_authenticate_connection_error(self, mock_request, mock_config):
        """Test authentication with connection error."""
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        client = APIClient(config=mock_config)
        
        with pytest.raises(APIConnectionError):
            client.authenticate()
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_is_authenticated_no_token(self):
        """Test is_authenticated with no token."""
        client = APIClient()
        assert not client.is_authenticated()
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_is_authenticated_expired_token(self):
        """Test is_authenticated with expired token."""
        client = APIClient()
        
        # Create expired auth response
        expired_auth = AuthResponse(
            access_token='expired_token',
            expires_in=1,
            _created_at=time.time() - 10  # 10 seconds ago, but expires in 1 second
        )
        client._auth_response = expired_auth
        
        assert not client.is_authenticated()
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_get_auth_info(self, mock_config, mock_auth_response_success):
        """Test get_auth_info method."""
        with patch('src.flowApi.client.requests.Session.request') as mock_request:
            mock_request.return_value = mock_auth_response_success
            
            client = APIClient(config=mock_config)
            
            # No auth info initially
            assert client.get_auth_info() is None
            
            # Authenticate and check auth info
            auth_response = client.authenticate()
            auth_info = client.get_auth_info()
            
            assert auth_info is not None
            assert auth_info.access_token == auth_response.access_token
    
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.flowApi.client.requests.Session.request')
    def test_make_authenticated_request_auto_auth(self, mock_request, mock_config):
        """Test _make_authenticated_request with automatic authentication."""
        # Mock successful auth response
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {
            'access_token': 'token123',
            'expires_in': 3600
        }
        
        # Mock successful API response
        api_response = Mock()
        api_response.status_code = 200
        
        # Return auth response first, then API response
        mock_request.side_effect = [auth_response, api_response]
        
        client = APIClient(config=mock_config)
        
        # Should automatically authenticate
        response = client._make_authenticated_request('GET', '/test')
        
        assert response is api_response
        assert mock_request.call_count == 2  # Auth + API call
        assert client.is_authenticated()
    
    @pytest.mark.unit
    @pytest.mark.api
    def test_clear_auth(self):
        """Test _clear_auth method."""
        client = APIClient()
        
        # Set up some auth state
        client._auth_response = Mock()
        client.session.headers['Authorization'] = 'Bearer token123'
        
        # Clear auth
        client._clear_auth()
        
        assert client._auth_response is None
        assert 'Authorization' not in client.session.headers
    


class TestAPIClientAuthenticationIntegration:
    """Integration tests for authentication workflow."""
    
    @pytest.mark.integration
    @pytest.mark.api
    @patch('src.flowApi.client.requests.Session.request')
    def test_complete_authentication_workflow(self, mock_request):
        """Integration test for complete authentication workflow."""
        # Mock config
        mock_config = Mock()
        mock_config.load_config.return_value = {
            'CLIENT_ID': 'integration_client',
            'CLIENT_SECRET': 'integration_secret',
            'RAG_FOLDER': '/path/to/rag'
        }
        
        # Mock successful auth response
        auth_response = Mock()
        auth_response.status_code = 200
        auth_response.json.return_value = {
            'access_token': 'integration_token_12345',
            'expires_in': 7200
        }
        mock_request.return_value = auth_response
        
        # Test complete workflow
        with APIClient(config=mock_config) as client:
            # Authenticate
            auth = client.authenticate()
            
            # Verify authentication
            assert isinstance(auth, AuthResponse)
            assert auth.access_token == 'integration_token_12345'
            assert auth.expires_in == 7200
            
            # Verify client state
            assert client.is_authenticated()
            
            # Verify auth info
            auth_info = client.get_auth_info()
            assert auth_info is not None
            assert auth_info.access_token == auth.access_token
            
            # Verify authorization header
            expected_header = f"Bearer {auth.access_token}"
            assert client.session.headers['Authorization'] == expected_header


# Parametrized tests for different authentication scenarios
class TestAPIClientAuthenticationParametrized:
    """Parametrized tests for different authentication scenarios."""
    
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
    @patch('src.flowApi.client.requests.Session.request')
    def test_authenticate_http_error_status_codes(self, mock_request, status_code, expected_exception):
        """Test authentication with different HTTP error status codes."""
        mock_config = Mock()
        mock_config.load_config.return_value = {
            'CLIENT_ID': 'client',
            'CLIENT_SECRET': 'secret',
            'RAG_FOLDER': '/path'
        }
        
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = f"Error {status_code}"
        mock_request.return_value = mock_response
        
        client = APIClient(config=mock_config)
        
        with pytest.raises(expected_exception) as exc_info:
            client.authenticate()
        
        assert exc_info.value.status_code == status_code
    
    @pytest.mark.parametrize("missing_key", [
        "CLIENT_ID",
        "CLIENT_SECRET",
    ])
    @pytest.mark.unit
    @pytest.mark.api
    def test_authenticate_missing_config_keys(self, missing_key):
        """Test authentication with missing configuration keys."""
        config_data = {
            'CLIENT_ID': 'client',
            'CLIENT_SECRET': 'secret',
            'RAG_FOLDER': '/path'
        }
        del config_data[missing_key]
        
        mock_config = Mock()
        mock_config.load_config.return_value = config_data
        
        client = APIClient(config=mock_config)
        
        with pytest.raises(APIConfigurationError) as exc_info:
            client.authenticate()
        
        assert missing_key in str(exc_info.value)
    
    @pytest.mark.parametrize("exception_class,expected_api_exception", [
        (requests.exceptions.ConnectionError, APIConnectionError),
        (requests.exceptions.Timeout, APITimeoutError),
        (requests.exceptions.RequestException, APIConnectionError),
    ])
    @pytest.mark.unit
    @pytest.mark.api
    @patch('src.flowApi.client.requests.Session.request')
    def test_authenticate_requests_exception_mapping(self, mock_request, exception_class, expected_api_exception):
        """Test mapping of requests exceptions to API exceptions during authentication."""
        mock_config = Mock()
        mock_config.load_config.return_value = {
            'CLIENT_ID': 'client',
            'CLIENT_SECRET': 'secret',
            'RAG_FOLDER': '/path'
        }
        
        mock_request.side_effect = exception_class("Test error")
        
        client = APIClient(config=mock_config)
        
        with pytest.raises(expected_api_exception):
            client.authenticate()