"""
RAG-enhanced chat completion endpoint routes.

This module contains chat completion endpoints that use RAG for context retrieval
and the flowApi client to interact with the external AI service.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any

from ...flowApi.client import APIClient
from ...flowApi.models import ChatMessage, ChatCompletionRequest
from ...flowApi.exceptions import (
    APIConnectionError, APITimeoutError, APIHTTPError, 
    APIResponseError, APIAuthenticationError, APIConfigurationError
)
from ...rag.rag_manager import RAGManager
from ...rag.exceptions import RAGError
from ..clientManager import ClientManager
from ..rag_dependency import get_rag_manager_optional


# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


# Pydantic models for request/response validation
class ChatMessageModel(BaseModel):
    """Pydantic model for chat message validation."""
    role: str = Field(..., description="Message role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        """Validate message role."""
        if v not in ['system', 'user', 'assistant']:
            raise ValueError(f"Invalid role: {v}. Must be 'system', 'user', or 'assistant'")
        return v
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Validate message content is not empty."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class SimpleChatRequest(BaseModel):
    """Pydantic model for simple chat completion request."""
    message: str = Field(..., description="User message content")
    max_tokens: int = Field(default=4096, ge=1, le=8192, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        """Validate message is not empty."""
        if not v or not v.strip():
            raise ValueError("user_message cannot be empty")
        return v.strip()


class AdvancedChatRequest(BaseModel):
    """Pydantic model for advanced chat completion request."""
    messages: List[ChatMessageModel] = Field(..., description="List of chat messages")
    max_tokens: int = Field(default=4096, ge=1, le=8192, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    stream: bool = Field(default=False, description="Whether to stream the response")
    allowed_models: List[str] = Field(default=["gpt-4o-mini"], description="List of allowed models")
    
    @field_validator('messages')
    @classmethod
    def validate_messages(cls, v):
        """Validate messages list is not empty."""
        if not v:
            raise ValueError("messages cannot be empty")
        return v


async def get_api_client() -> APIClient:
    """
    Dependency to get the shared APIClient instance.
    
    Returns:
        APIClient: Shared API client instance from ClientManager
    """
    return await ClientManager.get_client()


async def enhance_message_with_rag(
    user_message: str, 
    rag_manager: Optional[RAGManager]
) -> tuple[str, Dict[str, Any]]:
    """
    Enhance a user message with RAG context if available.
    
    Args:
        user_message: Original user message
        rag_manager: RAG manager instance (optional)
        
    Returns:
        Tuple of (enhanced_message, rag_metadata)
    """
    rag_metadata = {
        "rag_enabled": False,
        "sources_used": 0,
        "context_provided": False
    }
    
    if rag_manager is None or not rag_manager.is_ready:
        logger.debug("RAG not available, using original message")
        return user_message, rag_metadata
    
    try:
        # Enhance query with RAG context
        enhanced_message, context_chunks = await rag_manager.enhance_query_with_context(user_message)
        
        # Update metadata
        rag_metadata.update({
            "rag_enabled": True,
            "sources_used": len(context_chunks),
            "context_provided": len(context_chunks) > 0,
            "similarity_threshold": rag_manager.config.similarity_threshold
        })
        
        if context_chunks:
            # Add source information
            sources = []
            similarity_scores = []
            
            for chunk in context_chunks:
                sources.append(chunk.get('source_file', 'Unknown'))
                similarity_scores.append(chunk.get('similarity_score', 0.0))
            
            rag_metadata.update({
                "sources": sources,
                "similarity_scores": similarity_scores
            })
            
            logger.debug(f"Enhanced message with {len(context_chunks)} context chunks")
        else:
            logger.debug("No relevant context found for query")
        
        return enhanced_message, rag_metadata
        
    except RAGError as e:
        logger.warning(f"RAG enhancement failed: {e}")
        # Return original message as fallback
        return user_message, rag_metadata
    except Exception as e:
        logger.error(f"Unexpected error in RAG enhancement: {e}")
        # Return original message as fallback
        return user_message, rag_metadata


async def enhance_conversation_with_rag(
    messages: List[ChatMessageModel],
    rag_manager: Optional[RAGManager]
) -> tuple[List[ChatMessage], Dict[str, Any]]:
    """
    Enhance a conversation with RAG context by processing the last user message.
    
    Args:
        messages: List of conversation messages
        rag_manager: RAG manager instance (optional)
        
    Returns:
        Tuple of (enhanced_messages, rag_metadata)
    """
    rag_metadata = {
        "rag_enabled": False,
        "sources_used": 0,
        "context_provided": False
    }
    
    # Convert to ChatMessage objects
    chat_messages = []
    for msg in messages:
        chat_messages.append(ChatMessage(role=msg.role, content=msg.content))
    
    # Find the last user message to enhance
    last_user_message_idx = None
    for i in range(len(chat_messages) - 1, -1, -1):
        if chat_messages[i].role == 'user':
            last_user_message_idx = i
            break
    
    if last_user_message_idx is None:
        logger.debug("No user message found to enhance")
        return chat_messages, rag_metadata
    
    # Enhance the last user message
    original_content = chat_messages[last_user_message_idx].content
    enhanced_content, rag_metadata = await enhance_message_with_rag(original_content, rag_manager)
    
    # Update the message with enhanced content
    chat_messages[last_user_message_idx] = ChatMessage(
        role='user',
        content=enhanced_content
    )
    
    return chat_messages, rag_metadata


@router.post("/completion")
async def chat_completion(
    request: SimpleChatRequest,
    client: APIClient = Depends(get_api_client),
    rag_manager: Optional[RAGManager] = Depends(get_rag_manager_optional)
):
    """
    RAG-enhanced simple chat completion endpoint for single-turn conversations.
    
    This endpoint automatically enhances user queries with relevant context
    from indexed documents using RAG (Retrieval-Augmented Generation).
    
    Args:
        request: Simple chat completion request
        client: APIClient dependency
        rag_manager: RAG manager dependency (optional)
        
    Returns:
        dict: Chat completion response with generated content and RAG metadata
        
    Raises:
        HTTPException: If chat completion fails
    """
    try:
        # Enhance message with RAG context
        enhanced_message, rag_metadata = await enhance_message_with_rag(
            request.message, rag_manager
        )
        
        # Use the simple chat_completion method with enhanced message
        response = client.chat_completion(
            user_message=enhanced_message,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Prepare response with RAG metadata
        response_data = {
            "id": response.id,
            "model": response.model,
            "content": response.get_first_choice_content(),
            "finish_reason": response.choices[0].finish_reason if response.choices else None,
            "usage": response.usage.to_dict(),
            "created": response.created,
            "rag_metadata": rag_metadata
        }
        
        return response_data
        
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
        logger.error(f"Unexpected error in chat completion: {e}")
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
    client: APIClient = Depends(get_api_client),
    rag_manager: Optional[RAGManager] = Depends(get_rag_manager_optional)
):
    """
    RAG-enhanced advanced chat completion endpoint for multi-turn conversations.
    
    This endpoint automatically enhances the last user message in the conversation
    with relevant context from indexed documents using RAG.
    
    Args:
        request: Advanced chat completion request
        client: APIClient dependency
        rag_manager: RAG manager dependency (optional)
        
    Returns:
        dict: Complete chat completion response with RAG metadata
        
    Raises:
        HTTPException: If chat completion fails
    """
    try:
        # Enhance conversation with RAG context
        enhanced_messages, rag_metadata = await enhance_conversation_with_rag(
            request.messages, rag_manager
        )
        
        # Create ChatCompletionRequest with enhanced messages
        chat_request = ChatCompletionRequest(
            messages=enhanced_messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=request.stream,
            allowed_models=request.allowed_models
        )
        
        # Send the request
        response = client.send_chat_request(chat_request)
        
        # Add RAG metadata to response
        response_dict = response.to_dict()
        response_dict["rag_metadata"] = rag_metadata
        
        return response_dict
        
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
        logger.error(f"Unexpected error in advanced chat completion: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Unexpected error during chat completion",
                "error": str(e)
            }
        )