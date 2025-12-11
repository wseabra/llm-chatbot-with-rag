"""
Chat completion endpoint routes.

This module contains chat completion endpoints that use the flowApi client
to interact with the external AI service.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

from ...flowApi.client import APIClient
from ...flowApi.models import ChatMessage, ChatCompletionRequest
from ...flowApi.exceptions import (
    APIConnectionError, APITimeoutError, APIHTTPError, 
    APIResponseError, APIAuthenticationError, APIConfigurationError
)
from ..clientManager import ClientManager

router = APIRouter(prefix="/chat", tags=["chat"])


# Pydantic models for request/response validation
class ChatMessageModel(BaseModel):
    """Pydantic model for chat message validation."""
    role: str = Field(..., description="Message role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")


class SimpleChatRequest(BaseModel):
    """Pydantic model for simple chat completion request."""
    message: str = Field(..., description="User message content")
    max_tokens: int = Field(default=4096, ge=1, le=8192, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")


class AdvancedChatRequest(BaseModel):
    """Pydantic model for advanced chat completion request."""
    messages: List[ChatMessageModel] = Field(..., description="List of chat messages")
    max_tokens: int = Field(default=4096, ge=1, le=8192, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    stream: bool = Field(default=False, description="Whether to stream the response")
    allowed_models: List[str] = Field(default=["gpt-4o-mini"], description="List of allowed models")


async def get_api_client() -> APIClient:
    """
    Dependency to get the shared APIClient instance.
    
    Returns:
        APIClient: Shared API client instance from ClientManager
    """
    return await ClientManager.get_client()


@router.post("/completion")
async def chat_completion(
    request: SimpleChatRequest,
    client: APIClient = Depends(get_api_client)
):
    """
    Simple chat completion endpoint for single-turn conversations.
    
    This endpoint provides a simplified interface for basic chat completions.
    For multi-turn conversations, use the /chat/advanced endpoint.
    
    Args:
        request: Simple chat completion request
        client: APIClient dependency
        
    Returns:
        dict: Chat completion response with generated content
        
    Raises:
        HTTPException: If chat completion fails
    """
    try:
        # Use the simple chat_completion method
        response = client.chat_completion(
            user_message=request.message,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return {
            "id": response.id,
            "model": response.model,
            "content": response.get_first_choice_content(),
            "finish_reason": response.choices[0].finish_reason if response.choices else None,
            "usage": response.usage.to_dict(),
            "created": response.created
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Invalid request parameters",
                "error": str(e)
            }
        )
    except APIConfigurationError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Configuration error",
                "error": str(e)
            }
        )
    except APIAuthenticationError as e:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "message": "Authentication failed",
                "error": str(e)
            }
        )
    except (APIConnectionError, APITimeoutError) as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "message": "External API is unreachable",
                "error": str(e)
            }
        )
    except (APIHTTPError, APIResponseError) as e:
        raise HTTPException(
            status_code=502,
            detail={
                "status": "error",
                "message": "External API returned an error",
                "error": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Unexpected error during chat completion",
                "error": str(e)
            }
        )


@router.post("/advanced")
async def advanced_chat_completion(
    request: AdvancedChatRequest,
    client: APIClient = Depends(get_api_client)
):
    """
    Advanced chat completion endpoint for multi-turn conversations.
    
    This endpoint provides full control over chat completion parameters
    and supports multi-turn conversations with message history.
    
    Args:
        request: Advanced chat completion request
        client: APIClient dependency
        
    Returns:
        dict: Complete chat completion response
        
    Raises:
        HTTPException: If chat completion fails
    """
    try:
        # Convert Pydantic models to flowApi models
        chat_messages = []
        for msg in request.messages:
            chat_messages.append(ChatMessage(role=msg.role, content=msg.content))
        
        # Create ChatCompletionRequest
        chat_request = ChatCompletionRequest(
            messages=chat_messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=request.stream,
            allowed_models=request.allowed_models
        )
        
        # Send the request
        response = client.send_chat_request(chat_request)
        
        # Return the complete response
        return response.to_dict()
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Invalid request parameters",
                "error": str(e)
            }
        )
    except APIConfigurationError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Configuration error",
                "error": str(e)
            }
        )
    except APIAuthenticationError as e:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "message": "Authentication failed",
                "error": str(e)
            }
        )
    except (APIConnectionError, APITimeoutError) as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "message": "External API is unreachable",
                "error": str(e)
            }
        )
    except (APIHTTPError, APIResponseError) as e:
        raise HTTPException(
            status_code=502,
            detail={
                "status": "error",
                "message": "External API returned an error",
                "error": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Unexpected error during chat completion",
                "error": str(e)
            }
        )