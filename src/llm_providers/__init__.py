"""
Simple LLM Provider abstraction for easy extensibility.

This module provides a clean interface for implementing different LLM providers.
Clone this code and implement your own provider by extending the LLMProvider class.
"""

from .base import LLMProvider, LLMRequest, LLMResponse, LLMMessage, LLMChoice, LLMUsage
from .exceptions import LLMProviderError

__all__ = [
    "LLMProvider",
    "LLMRequest", 
    "LLMResponse",
    "LLMMessage",
    "LLMChoice",
    "LLMUsage",
    "LLMProviderError",
]