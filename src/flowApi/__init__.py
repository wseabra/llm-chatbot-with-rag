"""
API module for external service communication.

This module provides a clean interface for making HTTP requests to external APIs
with proper error handling, type safety, response validation, and authentication support.

Example usage:
    from flowApi import APIClient, HealthResponse, AuthResponse
    
    # Create client and authenticate
    client = APIClient()
    auth = client.authenticate()
    print(f"Token expires in {auth.expires_in} seconds")
    
    # Check health with authentication
    health = client.health_check(authenticated=True)
    print(f"API Health: {health.result} at {health.timestamp}")
    
    # Simple chat completion
    response = client.chat_completion("What is the capital of France?")
    print(f"AI Response: {response.get_first_choice_content()}")
    
    # Advanced chat completion with custom parameters
    response = client.chat_completion(
        "Explain quantum computing in simple terms.",
        max_tokens=500,
        temperature=0.5
    )
    print(f"AI Response: {response.get_first_choice_content()}")
    
    # Multi-turn conversation
    messages = [
        ChatMessage(role="user", content="What is the capital of France?"),
        ChatMessage(role="assistant", content="The capital of France is Paris."),
        ChatMessage(role="user", content="What is its population?")
    ]
    full_request = ChatCompletionRequest(messages=messages)
    response = client.send_chat_request(full_request)
    print(f"AI Response: {response.get_first_choice_content()}")
    
    # Using context manager for automatic cleanup
    with APIClient() as client:
        auth = client.authenticate()
        health = client.health_check(authenticated=True)
        print(f"Service is {'healthy' if health.result else 'unhealthy'}")
        
        response = client.chat_completion("Hello, how are you?")
        print(f"AI says: {response.get_first_choice_content()}")
"""

from .client import APIClient
from .models import (
    HealthResponse, AuthRequest, AuthResponse,
    ChatMessage, ChatCompletionRequest, ChatCompletionResponse,
    ChatCompletionChoice, ChatCompletionUsage
)
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
    'ChatMessage',
    'ChatCompletionRequest',
    'ChatCompletionResponse',
    'ChatCompletionChoice',
    'ChatCompletionUsage',
    'APIError',
    'APIConnectionError',
    'APITimeoutError',
    'APIHTTPError',
    'APIResponseError',
    'APIAuthenticationError',
    'APIConfigurationError'
]

__version__ = '1.2.0'