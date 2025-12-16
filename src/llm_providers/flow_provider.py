"""
CI&T Flow LLM Provider implementation.

This is the default provider that uses the existing flowApi client.
"""

import logging
from typing import List

from .base import LLMProvider, LLMRequest, LLMResponse, LLMMessage, LLMChoice, LLMUsage
from .exceptions import LLMProviderError

# Import flowApi with absolute imports to avoid relative import issues
try:
    from src.flowApi.client import APIClient
    from src.flowApi.models import ChatMessage, ChatCompletionRequest
    from src.flowApi.exceptions import APIError
except ImportError:
    # Fallback for when running from different contexts
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from flowApi.client import APIClient
        from flowApi.models import ChatMessage, ChatCompletionRequest
        from flowApi.exceptions import APIError
    except ImportError as e:
        raise ImportError(f"Could not import flowApi: {e}. Make sure flowApi is available.")

logger = logging.getLogger(__name__)


class FlowProvider(LLMProvider):
    """
    CI&T Flow LLM Provider.
    
    Uses the existing flowApi client to communicate with CI&T Flow API.
    """
    
    def __init__(self):
        """Initialize the Flow provider with existing configuration."""
        self.client = APIClient()
    
    async def chat_completion(self, request: LLMRequest) -> LLMResponse:
        """Generate a chat completion using CI&T Flow API."""
        try:
            # Convert to Flow API format
            flow_messages = [
                ChatMessage(role=msg.role, content=msg.content) 
                for msg in request.messages
            ]
            
            flow_request = ChatCompletionRequest(
                messages=flow_messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            # Make the API call
            flow_response = self.client.send_chat_request(flow_request)
            
            # Convert back to our format
            choices = [
                LLMChoice(
                    message=LLMMessage(
                        role=choice.message.role,
                        content=choice.message.content
                    ),
                    finish_reason=choice.finish_reason
                )
                for choice in flow_response.choices
            ]
            
            usage = LLMUsage(
                prompt_tokens=flow_response.usage.prompt_tokens,
                completion_tokens=flow_response.usage.completion_tokens,
                total_tokens=flow_response.usage.total_tokens
            )
            
            return LLMResponse(
                id=flow_response.id,
                model=flow_response.model,
                choices=choices,
                usage=usage
            )
            
        except APIError as e:
            raise LLMProviderError(f"Flow API error: {str(e)}") from e
        except Exception as e:
            raise LLMProviderError(f"Unexpected error: {str(e)}") from e
    
    async def health_check(self) -> bool:
        """Check if the Flow API is healthy."""
        try:
            health_response = self.client.health_check()
            return health_response.result
        except Exception as e:
            logger.warning(f"Flow health check failed: {e}")
            return False