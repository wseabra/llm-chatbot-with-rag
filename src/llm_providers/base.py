"""
Simple base classes for LLM providers.

To add your own provider:
1. Inherit from LLMProvider
2. Implement the required methods
3. Use it in your application
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List
from .exceptions import LLMProviderError


@dataclass
class LLMMessage:
    """A single chat message."""
    role: str  # "system", "user", or "assistant"
    content: str
    
    def __post_init__(self):
        if self.role not in ["system", "user", "assistant"]:
            raise ValueError(f"Invalid role: {self.role}")
        if not self.content.strip():
            raise ValueError("Content cannot be empty")


@dataclass
class LLMUsage:
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class LLMChoice:
    """A single completion choice."""
    message: LLMMessage
    finish_reason: str


@dataclass
class LLMRequest:
    """Request to an LLM provider."""
    messages: List[LLMMessage]
    max_tokens: int = 4096
    temperature: float = 0.7
    
    def __post_init__(self):
        if not self.messages:
            raise ValueError("Messages cannot be empty")


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    id: str
    model: str
    choices: List[LLMChoice]
    usage: LLMUsage
    
    def get_content(self) -> str:
        """Get the content of the first choice."""
        if self.choices:
            return self.choices[0].message.content
        return ""


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    To implement your own provider:
    1. Inherit from this class
    2. Implement the abstract methods
    3. Add your configuration in __init__
    
    Example:
        class MyProvider(LLMProvider):
            def __init__(self, api_key: str):
                self.api_key = api_key
            
            async def chat_completion(self, request: LLMRequest) -> LLMResponse:
                # Your implementation here
                pass
            
            async def health_check(self) -> bool:
                # Your health check here
                pass
    """
    
    @abstractmethod
    async def chat_completion(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a chat completion.
        
        Args:
            request: The chat request
            
        Returns:
            The chat response
            
        Raises:
            LLMProviderError: If the request fails
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        pass