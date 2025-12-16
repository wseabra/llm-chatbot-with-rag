"""
Simple FastAPI dependency for LLM provider.
"""

from fastapi import HTTPException
from .provider_config import get_llm_provider
from .base import LLMProvider
from .exceptions import LLMProviderError


async def get_llm_provider_dependency() -> LLMProvider:
    """
    FastAPI dependency to get the configured LLM provider.
    
    Returns:
        LLMProvider: The configured provider instance
        
    Raises:
        HTTPException: If provider initialization fails
    """
    try:
        return get_llm_provider()
    except LLMProviderError as e:
        raise HTTPException(
            status_code=503,
            detail=f"LLM provider error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize LLM provider: {str(e)}"
        )