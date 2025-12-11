"""
Data models for API responses and requests.

This module provides type-safe data models for handling API responses
and requests, ensuring proper validation and structure.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import time
from .exceptions import APIResponseError


@dataclass
class HealthResponse:
    """
    Data model for health check API response.
    
    Represents the response from the /ai-orchestration-api/v1/health endpoint
    with proper validation and type safety.
    """
    
    result: bool
    timestamp: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthResponse':
        """
        Create HealthResponse instance from dictionary data.
        
        Args:
            data: Dictionary containing response data from API
            
        Returns:
            HealthResponse instance with validated data
            
        Raises:
            APIResponseError: If required fields are missing or invalid
        """
        if not isinstance(data, dict):
            raise APIResponseError(
                "Invalid response format: expected dictionary",
                response_data=str(data)
            )
        
        # Validate required fields
        required_fields = ['result', 'timestamp']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise APIResponseError(
                f"Missing required fields in response: {', '.join(missing_fields)}",
                response_data=str(data)
            )
        
        # Validate field types
        result = data['result']
        timestamp = data['timestamp']
        
        if not isinstance(result, bool):
            raise APIResponseError(
                f"Invalid 'result' field type: expected bool, got {type(result).__name__}",
                response_data=str(data)
            )
        
        if not isinstance(timestamp, str):
            raise APIResponseError(
                f"Invalid 'timestamp' field type: expected str, got {type(timestamp).__name__}",
                response_data=str(data)
            )
        
        # Validate timestamp format (basic check for ISO format)
        if not timestamp or len(timestamp.strip()) == 0:
            raise APIResponseError(
                "Invalid timestamp: empty or whitespace-only string",
                response_data=str(data)
            )
        
        return cls(result=result, timestamp=timestamp.strip())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert HealthResponse instance to dictionary.
        
        Returns:
            Dictionary representation of the health response
        """
        return {
            'result': self.result,
            'timestamp': self.timestamp
        }
    
    def __str__(self) -> str:
        """Return string representation of the health response."""
        status = "healthy" if self.result else "unhealthy"
        return f"Health Status: {status} (timestamp: {self.timestamp})"


@dataclass
class AuthRequest:
    """
    Data model for authentication request.
    
    Represents the request body for the /auth-engine-api/v1/api-key/token endpoint
    with proper validation and serialization.
    """
    
    client_id: str
    client_secret: str
    app_to_access: str = "llm-api"
    
    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.client_id or not self.client_id.strip():
            raise ValueError("client_id cannot be empty or whitespace-only")
        
        if not self.client_secret or not self.client_secret.strip():
            raise ValueError("client_secret cannot be empty or whitespace-only")
        
        if not self.app_to_access or not self.app_to_access.strip():
            raise ValueError("app_to_access cannot be empty or whitespace-only")
        
        # Strip whitespace from all fields
        self.client_id = self.client_id.strip()
        self.client_secret = self.client_secret.strip()
        self.app_to_access = self.app_to_access.strip()
    
    def to_dict(self) -> Dict[str, str]:
        """
        Convert AuthRequest to dictionary for API request.
        
        Returns:
            Dictionary with camelCase keys as expected by the API
        """
        return {
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
            "appToAccess": self.app_to_access
        }
    
    def __str__(self) -> str:
        """Return string representation (without exposing secret)."""
        return f"AuthRequest(client_id='{self.client_id}', app_to_access='{self.app_to_access}')"


@dataclass
class AuthResponse:
    """
    Data model for authentication response.
    
    Represents the response from the /auth-engine-api/v1/api-key/token endpoint
    with proper validation and token management utilities.
    """
    
    access_token: str
    expires_in: int
    _created_at: Optional[float] = None
    
    def __post_init__(self):
        """Set creation timestamp for expiration tracking."""
        if self._created_at is None:
            self._created_at = time.time()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthResponse':
        """
        Create AuthResponse instance from dictionary data.
        
        Args:
            data: Dictionary containing response data from API
            
        Returns:
            AuthResponse instance with validated data
            
        Raises:
            APIResponseError: If required fields are missing or invalid
        """
        if not isinstance(data, dict):
            raise APIResponseError(
                "Invalid response format: expected dictionary",
                response_data=str(data)
            )
        
        # Validate required fields
        required_fields = ['access_token', 'expires_in']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise APIResponseError(
                f"Missing required fields in response: {', '.join(missing_fields)}",
                response_data=str(data)
            )
        
        # Validate field types and values
        access_token = data['access_token']
        expires_in = data['expires_in']
        
        if not isinstance(access_token, str):
            raise APIResponseError(
                f"Invalid 'access_token' field type: expected str, got {type(access_token).__name__}",
                response_data=str(data)
            )
        
        if not access_token or len(access_token.strip()) == 0:
            raise APIResponseError(
                "Invalid access_token: empty or whitespace-only string",
                response_data=str(data)
            )
        
        if not isinstance(expires_in, int):
            # Try to convert if it's a numeric string
            try:
                expires_in = int(expires_in)
            except (ValueError, TypeError):
                raise APIResponseError(
                    f"Invalid 'expires_in' field type: expected int, got {type(expires_in).__name__}",
                    response_data=str(data)
                )
        
        if expires_in <= 0:
            raise APIResponseError(
                f"Invalid expires_in value: must be positive, got {expires_in}",
                response_data=str(data)
            )
        
        return cls(access_token=access_token.strip(), expires_in=expires_in)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert AuthResponse instance to dictionary.
        
        Returns:
            Dictionary representation of the auth response
        """
        return {
            'access_token': self.access_token,
            'expires_in': self.expires_in
        }
    
    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """
        Check if the token is expired or will expire soon.
        
        Args:
            buffer_seconds: Number of seconds before actual expiration to consider expired
            
        Returns:
            True if token is expired or will expire within buffer_seconds
        """
        if self._created_at is None:
            return True
        
        elapsed = time.time() - self._created_at
        return elapsed >= (self.expires_in - buffer_seconds)
    
    def time_until_expiry(self) -> float:
        """
        Get the number of seconds until token expires.
        
        Returns:
            Seconds until expiration (negative if already expired)
        """
        if self._created_at is None:
            return 0.0
        
        elapsed = time.time() - self._created_at
        return self.expires_in - elapsed
    
    def get_authorization_header(self) -> str:
        """
        Get the Authorization header value for HTTP requests.
        
        Returns:
            Authorization header value in format "Bearer <token>"
        """
        return f"Bearer {self.access_token}"
    
    def __str__(self) -> str:
        """Return string representation (without exposing full token)."""
        token_preview = self.access_token[:8] + "..." if len(self.access_token) > 8 else self.access_token
        remaining = self.time_until_expiry()
        return f"AuthResponse(token='{token_preview}', expires_in={self.expires_in}s, remaining={remaining:.1f}s)"