"""
API module for external service communication.

This module provides a clean interface for making HTTP requests to external APIs
with proper error handling, type safety, and response validation.

Example usage:
    from api import APIClient, HealthResponse
    
    # Create client and check health
    client = APIClient()
    health = client.health_check()
    print(f"API Health: {health.result} at {health.timestamp}")
    
    # Using context manager for automatic cleanup
    with APIClient() as client:
        health = client.health_check()
        print(f"Service is {'healthy' if health.result else 'unhealthy'}")
"""

from .client import APIClient
from .models import HealthResponse
from .exceptions import (
    APIError,
    APIConnectionError,
    APITimeoutError,
    APIHTTPError,
    APIResponseError
)

__all__ = [
    'APIClient',
    'HealthResponse',
    'APIError',
    'APIConnectionError',
    'APITimeoutError',
    'APIHTTPError',
    'APIResponseError'
]

__version__ = '1.0.0'