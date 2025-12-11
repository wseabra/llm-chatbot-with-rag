"""
Data models for API responses and requests.

This module provides type-safe data models for handling API responses
and requests, ensuring proper validation and structure.
"""

from dataclasses import dataclass
from typing import Dict, Any
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