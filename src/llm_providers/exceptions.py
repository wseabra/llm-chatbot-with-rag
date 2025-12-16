"""
Simple exceptions for LLM provider operations.
"""


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message