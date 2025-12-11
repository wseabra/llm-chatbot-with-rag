"""
API module for external service communication.

This module provides a clean interface for making HTTP requests to external APIs
with proper error handling, type safety, response validation, and authentication support.

Example usage:
    from api import APIClient, HealthResponse, AuthResponse
    
    # Create client and authenticate
    client = APIClient()
    auth = client.authenticate()
    print(f"Token expires in {auth.expires_in} seconds")
    
    # Check health with authentication
    health = client.health_check(authenticated=True)
    print(f"API Health: {health.result} at {health.timestamp}")
    
    # Using context manager for automatic cleanup
    with APIClient() as client:
        auth = client.authenticate()
        health = client.health_check(authenticated=True)
        print(f"Service is {'healthy' if health.result else 'unhealthy'}")
"""

from .client import APIClient
from .models import HealthResponse, AuthRequest, AuthResponse
from .exceptions import (
    APIError,
    APIConnectionError,
    APITimeoutError,
    APIHTTPError,
    APIResponseError,
    APIAuthenticationError,
    APIConfigurationError
)

__all__ = [
    'APIClient',
    'HealthResponse',
    'AuthRequest',
    'AuthResponse',
    'APIError',
    'APIConnectionError',
    'APITimeoutError',
    'APIHTTPError',
    'APIResponseError',
    'APIAuthenticationError',
    'APIConfigurationError'
]

__version__ = '1.1.0'