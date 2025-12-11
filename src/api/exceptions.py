"""
Custom exceptions for API operations.

This module provides specialized exception classes for handling different types
of API errors that can occur during HTTP requests to external services.
"""


class APIError(Exception):
    """
    Base exception class for all API-related errors.
    
    This is the parent class for all API exceptions and provides
    a common interface for error handling.
    """
    
    def __init__(self, message: str, status_code: int = None):
        """
        Initialize the APIError.
        
        Args:
            message: Human-readable error description
            status_code: Optional HTTP status code associated with the error
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.status_code:
            return f"API Error {self.status_code}: {self.message}"
        return f"API Error: {self.message}"


class APIConnectionError(APIError):
    """
    Exception raised when there are network connectivity issues.
    
    This includes DNS resolution failures, connection timeouts,
    and other network-level problems.
    """
    
    def __init__(self, message: str = "Failed to connect to API"):
        """
        Initialize the APIConnectionError.
        
        Args:
            message: Human-readable error description
        """
        super().__init__(message)


class APITimeoutError(APIError):
    """
    Exception raised when API requests exceed the configured timeout.
    
    This occurs when the server takes too long to respond or
    the connection hangs.
    """
    
    def __init__(self, message: str = "API request timed out", timeout: float = None):
        """
        Initialize the APITimeoutError.
        
        Args:
            message: Human-readable error description
            timeout: The timeout value that was exceeded
        """
        super().__init__(message)
        self.timeout = timeout
    
    def __str__(self) -> str:
        """Return string representation of the timeout error."""
        if self.timeout:
            return f"API Timeout Error ({self.timeout}s): {self.message}"
        return f"API Timeout Error: {self.message}"


class APIHTTPError(APIError):
    """
    Exception raised for HTTP error status codes (4xx, 5xx).
    
    This includes client errors (400-499) and server errors (500-599).
    """
    
    def __init__(self, message: str, status_code: int, response_text: str = None):
        """
        Initialize the APIHTTPError.
        
        Args:
            message: Human-readable error description
            status_code: HTTP status code that caused the error
            response_text: Optional response body text for debugging
        """
        super().__init__(message, status_code)
        self.response_text = response_text
    
    def __str__(self) -> str:
        """Return string representation of the HTTP error."""
        return f"API HTTP Error {self.status_code}: {self.message}"


class APIResponseError(APIError):
    """
    Exception raised when API response format is invalid or unexpected.
    
    This includes JSON parsing errors, missing required fields,
    and schema validation failures.
    """
    
    def __init__(self, message: str, response_data: str = None):
        """
        Initialize the APIResponseError.
        
        Args:
            message: Human-readable error description
            response_data: Optional raw response data for debugging
        """
        super().__init__(message)
        self.response_data = response_data
    
    def __str__(self) -> str:
        """Return string representation of the response error."""
        return f"API Response Error: {self.message}"


class APIAuthenticationError(APIError):
    """
    Exception raised when authentication fails.
    
    This includes invalid credentials, expired tokens,
    and authentication service errors.
    """
    
    def __init__(self, message: str, status_code: int = None, auth_type: str = None):
        """
        Initialize the APIAuthenticationError.
        
        Args:
            message: Human-readable error description
            status_code: Optional HTTP status code associated with the error
            auth_type: Type of authentication that failed (e.g., 'credentials', 'token')
        """
        super().__init__(message, status_code)
        self.auth_type = auth_type
    
    def __str__(self) -> str:
        """Return string representation of the authentication error."""
        auth_info = f" ({self.auth_type})" if self.auth_type else ""
        if self.status_code:
            return f"API Authentication Error {self.status_code}{auth_info}: {self.message}"
        return f"API Authentication Error{auth_info}: {self.message}"


class APIConfigurationError(APIError):
    """
    Exception raised when there are configuration-related issues.
    
    This includes missing configuration values, invalid settings,
    and configuration loading errors.
    """
    
    def __init__(self, message: str, config_key: str = None):
        """
        Initialize the APIConfigurationError.
        
        Args:
            message: Human-readable error description
            config_key: The configuration key that caused the error
        """
        super().__init__(message)
        self.config_key = config_key
    
    def __str__(self) -> str:
        """Return string representation of the configuration error."""
        key_info = f" (key: {self.config_key})" if self.config_key else ""
        return f"API Configuration Error{key_info}: {self.message}"