"""
OpenAI LLM Provider implementation (example).

This shows how to implement a new provider. To use this:
1. Install: pip install openai
2. Set your API key: export OPENAI_API_KEY=your_key
3. Use OpenAIProvider instead of FlowProvider
"""

import os
import logging
from typing import List

from .base import LLMProvider, LLMRequest, LLMResponse, LLMMessage, LLMChoice, LLMUsage
from .exceptions import LLMProviderError

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed. Run: pip install openai")


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM Provider.
    
    Example implementation showing how to add a new provider.
    
    Usage:
        provider = OpenAIProvider(api_key="your_key")
        # or
        provider = OpenAIProvider()  # uses OPENAI_API_KEY env var
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key. If None, uses OPENAI_API_KEY env var.
        """
        if not OPENAI_AVAILABLE:
            raise LLMProviderError("OpenAI package not installed. Run: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise LLMProviderError("OpenAI API key not provided")
        
        self.client = openai.OpenAI(api_key=self.api_key)
    
    async def chat_completion(self, request: LLMRequest) -> LLMResponse:
        """Generate a chat completion using OpenAI API."""
        try:
            # Convert to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]
            
            # Make the API call
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=openai_messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            # Convert back to our format
            choices = [
                LLMChoice(
                    message=LLMMessage(
                        role=choice.message.role,
                        content=choice.message.content
                    ),
                    finish_reason=choice.finish_reason
                )
                for choice in response.choices
            ]
            
            usage = LLMUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
            
            return LLMResponse(
                id=response.id,
                model=response.model,
                choices=choices,
                usage=usage
            )
            
        except Exception as e:
            raise LLMProviderError(f"OpenAI API error: {str(e)}") from e
    
    async def health_check(self) -> bool:
        """Check if the OpenAI API is accessible."""
        try:
            # Simple test call
            self.client.models.list()
            return True
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False