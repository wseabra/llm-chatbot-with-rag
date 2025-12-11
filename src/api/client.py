"""
HTTP API client for external service communication.

This module provides the APIClient class for making HTTP requests to external
APIs using the requests library, with proper error handling, type safety,
and authentication support.
"""

import requests
import json
from typing import Optional
from urllib.parse import urljoin

from .models import HealthResponse, AuthRequest, AuthResponse
from .exceptions import (
    APIConnectionError,
    APITimeoutError,
    APIHTTPError,
    APIResponseError,
    APIAuthenticationError,
    APIConfigurationError
)


class APIClient:
    """
    HTTP client for making requests to external APIs.
    
    Provides a clean interface for API communication with proper error handling,
    timeout management, response validation, and authentication support.
    """
    
    def __init__(self, base_url: str = "https://flow.ciandt.com", timeout: int = 30, config=None):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the API service
            timeout: Request timeout in seconds
            config: Optional Config instance for authentication credentials
        """
        self.base_url = base_url.rstrip('/')  # Remove trailing slash
        self.timeout = timeout
        self.config = config
        
        # Authentication state
        self._auth_response: Optional[AuthResponse] = None
        
        # Create a session for connection pooling and performance
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'APIClient/1.0.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an HTTP request with proper error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object from requests
            
        Raises:
            APIConnectionError: For network connectivity issues
            APITimeoutError: For request timeouts
            APIHTTPError: For HTTP error status codes
        """
        # Construct full URL
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        # Set timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Check for HTTP errors
            if response.status_code >= 400:
                error_message = f"HTTP {response.status_code} error for {method} {url}"
                
                # Special handling for authentication errors
                if response.status_code == 401:
                    raise APIAuthenticationError(
                        message=f"Authentication failed: {error_message}",
                        status_code=response.status_code,
                        auth_type="token"
                    )
                elif response.status_code == 403:
                    raise APIAuthenticationError(
                        message=f"Access forbidden: {error_message}",
                        status_code=response.status_code,
                        auth_type="authorization"
                    )
                else:
                    raise APIHTTPError(
                        message=error_message,
                        status_code=response.status_code,
                        response_text=response.text
                    )
            
            return response
            
        except requests.exceptions.Timeout as e:
            raise APITimeoutError(
                message=f"Request to {url} timed out after {kwargs.get('timeout', self.timeout)} seconds",
                timeout=kwargs.get('timeout', self.timeout)
            ) from e
            
        except requests.exceptions.ConnectionError as e:
            raise APIConnectionError(
                message=f"Failed to connect to {url}: {str(e)}"
            ) from e
            
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(
                message=f"Request failed for {url}: {str(e)}"
            ) from e
    
    def _load_config(self):
        """
        Load configuration if not already provided.
        
        Returns:
            Dictionary containing configuration values
            
        Raises:
            APIConfigurationError: If config cannot be loaded
        """
        if self.config is None:
            try:
                # Import here to avoid circular imports
                from ..config import Config
                self.config = Config()
            except Exception as e:
                raise APIConfigurationError(
                    message=f"Failed to load configuration: {str(e)}"
                ) from e
        
        try:
            return self.config.load_config()
        except Exception as e:
            raise APIConfigurationError(
                message=f"Failed to load configuration values: {str(e)}"
            ) from e
    
    def authenticate(self) -> AuthResponse:
        """
        Authenticate with the API using client credentials.
        
        Uses CLIENT_ID and CLIENT_SECRET from config to obtain access token.
        The token is automatically stored and used for subsequent requests.
        
        Returns:
            AuthResponse object containing access token and expiration info
            
        Raises:
            APIConfigurationError: If configuration cannot be loaded
            APIAuthenticationError: If authentication fails
            APIConnectionError: For network connectivity issues
            APITimeoutError: For request timeouts
            APIResponseError: For invalid response format
        """
        # Load configuration
        try:
            config_data = self._load_config()
        except APIConfigurationError:
            raise
        except Exception as e:
            raise APIConfigurationError(
                message=f"Unexpected error loading configuration: {str(e)}"
            ) from e
        
        # Extract credentials
        try:
            client_id = config_data['CLIENT_ID']
            client_secret = config_data['CLIENT_SECRET']
        except KeyError as e:
            raise APIConfigurationError(
                message=f"Missing required configuration key: {str(e)}",
                config_key=str(e)
            ) from e
        
        # Create authentication request
        try:
            auth_request = AuthRequest(
                client_id=client_id,
                client_secret=client_secret,
                app_to_access="llm-api"
            )
        except ValueError as e:
            raise APIConfigurationError(
                message=f"Invalid configuration values: {str(e)}"
            ) from e
        
        # Make authentication request
        endpoint = '/auth-engine-api/v1/api-key/token'
        
        try:
            response = self._make_request(
                'POST', 
                endpoint, 
                data=json.dumps(auth_request.to_dict())
            )
            
            # Parse JSON response
            try:
                response_data = response.json()
            except ValueError as e:
                raise APIResponseError(
                    message=f"Invalid JSON response from authentication endpoint: {str(e)}",
                    response_data=response.text
                ) from e
            
            # Create and validate AuthResponse
            auth_response = AuthResponse.from_dict(response_data)
            
            # Store authentication response and update session headers
            self._auth_response = auth_response
            self._add_auth_header()
            
            return auth_response
            
        except APIAuthenticationError:
            # Clear any stored authentication on auth failure
            self._clear_auth()
            raise
        except (APIConnectionError, APITimeoutError, APIHTTPError, APIResponseError):
            # Re-raise API exceptions as-is
            raise
        except Exception as e:
            # Catch any unexpected errors
            raise APIResponseError(
                message=f"Unexpected error during authentication: {str(e)}"
            ) from e
    
    def _add_auth_header(self) -> None:
        """Add authentication header to session if token is available."""
        if self._auth_response and not self._auth_response.is_expired():
            self.session.headers['Authorization'] = self._auth_response.get_authorization_header()
        else:
            # Remove authorization header if token is expired or not available
            self.session.headers.pop('Authorization', None)
    
    def _clear_auth(self) -> None:
        """Clear stored authentication data and remove auth headers."""
        self._auth_response = None
        self.session.headers.pop('Authorization', None)
    
    def is_authenticated(self) -> bool:
        """
        Check if client is currently authenticated with a valid token.
        
        Returns:
            True if authenticated with a non-expired token, False otherwise
        """
        return (self._auth_response is not None and 
                not self._auth_response.is_expired())
    
    def get_auth_info(self) -> Optional[AuthResponse]:
        """
        Get current authentication information.
        
        Returns:
            AuthResponse object if authenticated, None otherwise
        """
        if self.is_authenticated():
            return self._auth_response
        return None
    
    def _make_authenticated_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an authenticated HTTP request.
        
        Automatically handles authentication and token refresh if needed.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object from requests
            
        Raises:
            APIAuthenticationError: If authentication fails
            Other API exceptions as per _make_request
        """
        # Ensure we have a valid token
        if not self.is_authenticated():
            try:
                self.authenticate()
            except Exception as e:
                raise APIAuthenticationError(
                    message=f"Failed to authenticate before making request: {str(e)}",
                    auth_type="auto"
                ) from e
        
        # Update auth header in case token was refreshed
        self._add_auth_header()
        
        try:
            return self._make_request(method, endpoint, **kwargs)
        except APIAuthenticationError as e:
            # If we get an auth error, clear stored auth and re-raise
            self._clear_auth()
            raise e
    
    def health_check(self, authenticated: bool = False) -> HealthResponse:
        """
        Perform health check on the API service.
        
        Makes a GET request to /ai-orchestration-api/v1/health and returns
        the parsed response.
        
        Args:
            authenticated: Whether to make an authenticated request
        
        Returns:
            HealthResponse object containing result and timestamp
            
        Raises:
            APIConnectionError: For network connectivity issues
            APITimeoutError: For request timeouts
            APIHTTPError: For HTTP error status codes
            APIResponseError: For invalid response format
            APIAuthenticationError: If authenticated=True and auth fails
        """
        endpoint = '/ai-orchestration-api/v1/health'
        
        try:
            if authenticated:
                response = self._make_authenticated_request('GET', endpoint)
            else:
                response = self._make_request('GET', endpoint)
            
            # Parse JSON response
            try:
                response_data = response.json()
            except ValueError as e:
                raise APIResponseError(
                    message=f"Invalid JSON response from health endpoint: {str(e)}",
                    response_data=response.text
                ) from e
            
            # Create and validate HealthResponse
            return HealthResponse.from_dict(response_data)
            
        except (APIConnectionError, APITimeoutError, APIHTTPError, 
                APIResponseError, APIAuthenticationError):
            # Re-raise API exceptions as-is
            raise
        except Exception as e:
            # Catch any unexpected errors
            raise APIResponseError(
                message=f"Unexpected error during health check: {str(e)}"
            ) from e
    
    def close(self) -> None:
        """
        Close the HTTP session and clean up resources.
        
        Should be called when the client is no longer needed to properly
        close connections and free resources.
        """
        # Clear authentication data
        self._clear_auth()
        
        # Close session
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.close()
    
    def __del__(self):
        """Destructor to ensure session cleanup."""
        self.close()