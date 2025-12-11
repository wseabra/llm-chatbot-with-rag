"""
HTTP API client for external service communication.

This module provides the APIClient class for making HTTP requests to external
APIs using the requests library, with proper error handling and type safety.
"""

import requests
from typing import Optional
from urllib.parse import urljoin

from .models import HealthResponse
from .exceptions import (
    APIConnectionError,
    APITimeoutError,
    APIHTTPError,
    APIResponseError
)


class APIClient:
    """
    HTTP client for making requests to external APIs.
    
    Provides a clean interface for API communication with proper error handling,
    timeout management, and response validation.
    """
    
    def __init__(self, base_url: str = "https://flow.ciandt.com", timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the API service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')  # Remove trailing slash
        self.timeout = timeout
        
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
    
    def health_check(self) -> HealthResponse:
        """
        Perform health check on the API service.
        
        Makes a GET request to /ai-orchestration-api/v1/health and returns
        the parsed response.
        
        Returns:
            HealthResponse object containing result and timestamp
            
        Raises:
            APIConnectionError: For network connectivity issues
            APITimeoutError: For request timeouts
            APIHTTPError: For HTTP error status codes
            APIResponseError: For invalid response format
        """
        endpoint = '/ai-orchestration-api/v1/health'
        
        try:
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
            
        except (APIConnectionError, APITimeoutError, APIHTTPError, APIResponseError):
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