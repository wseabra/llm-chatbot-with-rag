"""
Data models for API responses and requests.

This module provides type-safe data models for handling API responses
and requests, ensuring proper validation and structure.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
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


# Chat Completion Models

@dataclass
class ChatMessage:
    """
    Data model for a single chat message.
    
    Represents a message in a conversation with role and content.
    Compatible with Azure OpenAI chat completion format.
    """
    
    role: str
    content: str
    
    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.role or not self.role.strip():
            raise ValueError("role cannot be empty or whitespace-only")
        
        if not self.content or not self.content.strip():
            raise ValueError("content cannot be empty or whitespace-only")
        
        # Validate role is one of the allowed values
        allowed_roles = {"system", "user", "assistant"}
        if self.role.strip().lower() not in allowed_roles:
            raise ValueError(f"role must be one of {allowed_roles}, got '{self.role}'")
        
        # Strip whitespace and normalize role
        self.role = self.role.strip().lower()
        self.content = self.content.strip()
    
    def to_dict(self) -> Dict[str, str]:
        """
        Convert ChatMessage to dictionary for API request.
        
        Returns:
            Dictionary representation of the message
        """
        return {
            "role": self.role,
            "content": self.content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """
        Create ChatMessage instance from dictionary data.
        
        Args:
            data: Dictionary containing message data
            
        Returns:
            ChatMessage instance with validated data
            
        Raises:
            APIResponseError: If required fields are missing or invalid
        """
        if not isinstance(data, dict):
            raise APIResponseError(
                "Invalid message format: expected dictionary",
                response_data=str(data)
            )
        
        # Validate required fields
        required_fields = ['role', 'content']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise APIResponseError(
                f"Missing required fields in message: {', '.join(missing_fields)}",
                response_data=str(data)
            )
        
        try:
            return cls(role=data['role'], content=data['content'])
        except ValueError as e:
            raise APIResponseError(
                f"Invalid message data: {str(e)}",
                response_data=str(data)
            ) from e
    
    def __str__(self) -> str:
        """Return string representation of the message."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"ChatMessage(role='{self.role}', content='{content_preview}')"


@dataclass
class ChatCompletionRequest:
    """
    Data model for chat completion request.
    
    Represents the request body for the /ai-orchestration-api/v1/openai/chat/completions endpoint
    with proper validation and Azure OpenAI compatibility.
    """
    
    messages: List[ChatMessage]
    stream: bool = False
    max_tokens: int = 4096
    temperature: float = 0.7
    allowed_models: List[str] = field(default_factory=lambda: ["gpt-4o-mini"])
    
    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.messages:
            raise ValueError("messages cannot be empty")
        
        if not isinstance(self.messages, list):
            raise ValueError("messages must be a list")
        
        # Validate each message
        for i, message in enumerate(self.messages):
            if not isinstance(message, ChatMessage):
                raise ValueError(f"messages[{i}] must be a ChatMessage instance")
        
        # Validate max_tokens
        if not isinstance(self.max_tokens, int) or self.max_tokens <= 0:
            raise ValueError("max_tokens must be a positive integer")
        
        # Validate temperature
        if not isinstance(self.temperature, (int, float)) or not (0.0 <= self.temperature <= 2.0):
            raise ValueError("temperature must be a number between 0.0 and 2.0")
        
        # Validate stream
        if not isinstance(self.stream, bool):
            raise ValueError("stream must be a boolean")
        
        # Validate allowed_models
        if not isinstance(self.allowed_models, list) or not self.allowed_models:
            raise ValueError("allowed_models must be a non-empty list")
        
        for i, model in enumerate(self.allowed_models):
            if not isinstance(model, str) or not model.strip():
                raise ValueError(f"allowed_models[{i}] must be a non-empty string")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ChatCompletionRequest to dictionary for API request.
        
        Returns:
            Dictionary representation matching Azure OpenAI format
        """
        return {
            "messages": [message.to_dict() for message in self.messages],
            "stream": self.stream,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "allowedModels": self.allowed_models
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletionRequest':
        """
        Create ChatCompletionRequest instance from dictionary data.
        
        Args:
            data: Dictionary containing request data
            
        Returns:
            ChatCompletionRequest instance with validated data
            
        Raises:
            APIResponseError: If required fields are missing or invalid
        """
        if not isinstance(data, dict):
            raise APIResponseError(
                "Invalid request format: expected dictionary",
                response_data=str(data)
            )
        
        # Validate required fields
        if 'messages' not in data:
            raise APIResponseError(
                "Missing required field: messages",
                response_data=str(data)
            )
        
        try:
            # Parse messages
            messages = [ChatMessage.from_dict(msg) for msg in data['messages']]
            
            # Parse optional fields with defaults
            stream = data.get('stream', False)
            max_tokens = data.get('max_tokens', 4096)
            temperature = data.get('temperature', 0.7)
            allowed_models = data.get('allowedModels', ["gpt-4o-mini"])
            
            return cls(
                messages=messages,
                stream=stream,
                max_tokens=max_tokens,
                temperature=temperature,
                allowed_models=allowed_models
            )
        except (ValueError, TypeError) as e:
            raise APIResponseError(
                f"Invalid request data: {str(e)}",
                response_data=str(data)
            ) from e
    
    def __str__(self) -> str:
        """Return string representation of the request."""
        return (f"ChatCompletionRequest(messages={len(self.messages)}, "
                f"max_tokens={self.max_tokens}, temperature={self.temperature}, "
                f"stream={self.stream})")


@dataclass
class ChatCompletionUsage:
    """
    Data model for token usage information in chat completion response.
    
    Represents the usage statistics returned by the API.
    """
    
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    def __post_init__(self):
        """Validate fields after initialization."""
        if not isinstance(self.prompt_tokens, int) or self.prompt_tokens < 0:
            raise ValueError("prompt_tokens must be a non-negative integer")
        
        if not isinstance(self.completion_tokens, int) or self.completion_tokens < 0:
            raise ValueError("completion_tokens must be a non-negative integer")
        
        if not isinstance(self.total_tokens, int) or self.total_tokens < 0:
            raise ValueError("total_tokens must be a non-negative integer")
        
        # Validate that total equals sum of prompt and completion
        expected_total = self.prompt_tokens + self.completion_tokens
        if self.total_tokens != expected_total:
            raise ValueError(
                f"total_tokens ({self.total_tokens}) must equal "
                f"prompt_tokens + completion_tokens ({expected_total})"
            )
    
    def to_dict(self) -> Dict[str, int]:
        """
        Convert ChatCompletionUsage to dictionary.
        
        Returns:
            Dictionary representation of the usage statistics
        """
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletionUsage':
        """
        Create ChatCompletionUsage instance from dictionary data.
        
        Args:
            data: Dictionary containing usage data
            
        Returns:
            ChatCompletionUsage instance with validated data
            
        Raises:
            APIResponseError: If required fields are missing or invalid
        """
        if not isinstance(data, dict):
            raise APIResponseError(
                "Invalid usage format: expected dictionary",
                response_data=str(data)
            )
        
        # Validate required fields
        required_fields = ['prompt_tokens', 'completion_tokens', 'total_tokens']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise APIResponseError(
                f"Missing required fields in usage: {', '.join(missing_fields)}",
                response_data=str(data)
            )
        
        try:
            return cls(
                prompt_tokens=int(data['prompt_tokens']),
                completion_tokens=int(data['completion_tokens']),
                total_tokens=int(data['total_tokens'])
            )
        except (ValueError, TypeError) as e:
            raise APIResponseError(
                f"Invalid usage data: {str(e)}",
                response_data=str(data)
            ) from e
    
    def __str__(self) -> str:
        """Return string representation of the usage statistics."""
        return (f"Usage(prompt={self.prompt_tokens}, completion={self.completion_tokens}, "
                f"total={self.total_tokens})")


@dataclass
class ChatCompletionChoice:
    """
    Data model for a single choice in chat completion response.
    
    Represents one possible completion returned by the API.
    """
    
    index: int
    message: ChatMessage
    finish_reason: str
    
    def __post_init__(self):
        """Validate fields after initialization."""
        if not isinstance(self.index, int) or self.index < 0:
            raise ValueError("index must be a non-negative integer")
        
        if not isinstance(self.message, ChatMessage):
            raise ValueError("message must be a ChatMessage instance")
        
        if not self.finish_reason or not self.finish_reason.strip():
            raise ValueError("finish_reason cannot be empty or whitespace-only")
        
        # Validate finish_reason is one of the expected values
        allowed_reasons = {"stop", "length", "content_filter", "function_call"}
        if self.finish_reason.strip() not in allowed_reasons:
            # Don't raise error for unknown reasons to maintain forward compatibility
            pass
        
        self.finish_reason = self.finish_reason.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ChatCompletionChoice to dictionary.
        
        Returns:
            Dictionary representation of the choice
        """
        return {
            "index": self.index,
            "message": self.message.to_dict(),
            "finish_reason": self.finish_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletionChoice':
        """
        Create ChatCompletionChoice instance from dictionary data.
        
        Args:
            data: Dictionary containing choice data
            
        Returns:
            ChatCompletionChoice instance with validated data
            
        Raises:
            APIResponseError: If required fields are missing or invalid
        """
        if not isinstance(data, dict):
            raise APIResponseError(
                "Invalid choice format: expected dictionary",
                response_data=str(data)
            )
        
        # Validate required fields
        required_fields = ['index', 'message', 'finish_reason']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise APIResponseError(
                f"Missing required fields in choice: {', '.join(missing_fields)}",
                response_data=str(data)
            )
        
        try:
            message = ChatMessage.from_dict(data['message'])
            return cls(
                index=int(data['index']),
                message=message,
                finish_reason=data['finish_reason']
            )
        except (ValueError, TypeError) as e:
            raise APIResponseError(
                f"Invalid choice data: {str(e)}",
                response_data=str(data)
            ) from e
    
    def __str__(self) -> str:
        """Return string representation of the choice."""
        return f"Choice(index={self.index}, finish_reason='{self.finish_reason}')"


@dataclass
class ChatCompletionResponse:
    """
    Data model for chat completion response.
    
    Represents the complete response from the /ai-orchestration-api/v1/openai/chat/completions endpoint
    with proper validation and Azure OpenAI compatibility.
    """
    
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage
    
    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.id or not self.id.strip():
            raise ValueError("id cannot be empty or whitespace-only")
        
        if not self.object or not self.object.strip():
            raise ValueError("object cannot be empty or whitespace-only")
        
        if not isinstance(self.created, int) or self.created <= 0:
            raise ValueError("created must be a positive integer timestamp")
        
        if not self.model or not self.model.strip():
            raise ValueError("model cannot be empty or whitespace-only")
        
        if not isinstance(self.choices, list) or not self.choices:
            raise ValueError("choices must be a non-empty list")
        
        for i, choice in enumerate(self.choices):
            if not isinstance(choice, ChatCompletionChoice):
                raise ValueError(f"choices[{i}] must be a ChatCompletionChoice instance")
        
        if not isinstance(self.usage, ChatCompletionUsage):
            raise ValueError("usage must be a ChatCompletionUsage instance")
        
        # Strip whitespace from string fields
        self.id = self.id.strip()
        self.object = self.object.strip()
        self.model = self.model.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ChatCompletionResponse to dictionary.
        
        Returns:
            Dictionary representation matching Azure OpenAI format
        """
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [choice.to_dict() for choice in self.choices],
            "usage": self.usage.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletionResponse':
        """
        Create ChatCompletionResponse instance from dictionary data.
        
        Args:
            data: Dictionary containing response data from API
            
        Returns:
            ChatCompletionResponse instance with validated data
            
        Raises:
            APIResponseError: If required fields are missing or invalid
        """
        if not isinstance(data, dict):
            raise APIResponseError(
                "Invalid response format: expected dictionary",
                response_data=str(data)
            )
        
        # Validate required fields
        required_fields = ['id', 'object', 'created', 'model', 'choices', 'usage']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise APIResponseError(
                f"Missing required fields in response: {', '.join(missing_fields)}",
                response_data=str(data)
            )
        
        try:
            # Parse nested objects
            choices = [ChatCompletionChoice.from_dict(choice) for choice in data['choices']]
            usage = ChatCompletionUsage.from_dict(data['usage'])
            
            return cls(
                id=data['id'],
                object=data['object'],
                created=int(data['created']),
                model=data['model'],
                choices=choices,
                usage=usage
            )
        except (ValueError, TypeError) as e:
            raise APIResponseError(
                f"Invalid response data: {str(e)}",
                response_data=str(data)
            ) from e
    
    def get_first_choice_content(self) -> str:
        """
        Get the content of the first choice's message.
        
        Convenience method for accessing the most common use case.
        
        Returns:
            Content string from the first choice's assistant message
        """
        if not self.choices:
            return ""
        return self.choices[0].message.content
    
    def __str__(self) -> str:
        """Return string representation of the response."""
        return (f"ChatCompletionResponse(id='{self.id}', model='{self.model}', "
                f"choices={len(self.choices)}, usage={self.usage})")