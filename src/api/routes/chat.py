"""
Unified chat endpoint with RAG and file upload support.

This module provides a single chat endpoint that handles both regular chat
and chat with file uploads, using RAG for context enhancement.
"""

import json
import logging
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field, field_validator

from ...flowApi.client import APIClient
from ...flowApi.models import ChatMessage, ChatCompletionRequest
from ...flowApi.exceptions import (
    APIConnectionError, APITimeoutError, APIHTTPError,
    APIResponseError, APIAuthenticationError, APIConfigurationError,
)
from ..clientManager import ClientManager
from ..rag_dependency import get_rag_manager_optional
from ...rag.rag_manager import RAGManager
from ...rag.exceptions import RAGError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


# Pydantic models for request validation
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


async def get_api_client() -> APIClient:
    """
    Dependency to get the shared APIClient instance.
    
    Returns:
        APIClient: Shared API client instance from ClientManager
    """
    return await ClientManager.get_client()


def _validate_file(file: UploadFile) -> None:
    """Validate uploaded file type and constraints."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": f"Unsupported file type: {suffix}. Allowed: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
            },
        )


def _save_uploads_to_temp(files: List[UploadFile]) -> Tuple[Path, List[Tuple[str, str, str]]]:
    """
    Save uploaded files to a temporary folder and enforce size limit.

    Returns a tuple of (temp_dir, uploaded_files_info)
    where uploaded_files_info is a list of (file_path, document_id, original_filename).
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="uploads_"))
    saved: List[Tuple[str, str, str]] = []

    for f in files:
        _validate_file(f)
        original = f.filename or f"upload_{uuid.uuid4().hex}"
        safe_name = os.path.basename(original)
        dest_path = temp_dir / safe_name

        size = 0
        with dest_path.open("wb") as out:
            while True:
                chunk = f.file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_FILE_SIZE_BYTES:
                    try:
                        f.file.close()
                    except Exception:
                        pass
                    # cleanup partial file
                    try:
                        out.flush()
                        out.close()
                    except Exception:
                        pass
                    if dest_path.exists():
                        dest_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "status": "error",
                            "message": f"File '{safe_name}' exceeds 10MB limit",
                        },
                    )
                out.write(chunk)
        document_id = uuid.uuid4().hex
        saved.append((str(dest_path), document_id, safe_name))

    return temp_dir, saved


def _cleanup_temp_dir(temp_dir: Optional[Path]) -> None:
    """Clean up temporary directory."""
    if temp_dir and temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            logger.warning("Failed to remove temp dir: %s", temp_dir)


async def _enhance_message_with_rag(
    user_message: str, 
    rag_manager: Optional[RAGManager],
    uploaded_infos: Optional[List[Tuple[str, str, str]]] = None
) -> Tuple[str, Dict[str, Any]]:
    """
    Enhance a user message with RAG context if available.
    
    Args:
        user_message: Original user message
        rag_manager: RAG manager instance (optional)
        uploaded_infos: List of uploaded file info (optional)
        
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
        if uploaded_infos:
            enhanced_message, context_chunks = await rag_manager.process_uploaded_documents_with_context(
                user_message, uploaded_infos
            )
        else:
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
            
            if uploaded_infos:
                rag_metadata["uploaded_documents"] = [info[2] for info in uploaded_infos]
            
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


@router.post("/chat")
async def chat_completion(
    messages: str = Form(..., description="JSON array of messages [{role, content}...]"),
    client: APIClient = Depends(get_api_client),
    rag_manager: Optional[RAGManager] = Depends(get_rag_manager_optional),
    files: List[UploadFile] = File(default_factory=list),
    max_tokens: int = Form(4096),
    temperature: float = Form(0.7),
    stream: bool = Form(False),
    allowed_models: Optional[str] = Form(None, description="Comma-separated allowed models"),
):
    """
    Unified chat endpoint that supports both regular chat and chat with file uploads.
    
    Automatically enhances user queries with relevant context from indexed documents
    and/or newly uploaded files using RAG (Retrieval-Augmented Generation).
    
    Args:
        messages: JSON string of chat messages
        client: APIClient dependency
        rag_manager: RAG manager dependency (optional)
        files: Optional list of uploaded files
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        stream: Whether to stream the response
        allowed_models: Comma-separated list of allowed models
        
    Returns:
        dict: Chat completion response with RAG metadata
        
    Raises:
        HTTPException: If chat completion fails
    """
    temp_dir: Optional[Path] = None

    try:
        # Parse and validate messages
        try:
            raw = json.loads(messages)
            if not isinstance(raw, list) or not raw:
                raise ValueError("messages must be a non-empty JSON array")
            parsed_models = [ChatMessageModel(**m) for m in raw]
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "Invalid messages payload",
                    "error": str(e),
                },
            )

        # Convert to flowApi ChatMessage objects
        chat_messages: List[ChatMessage] = [
            ChatMessage(role=m.role, content=m.content) for m in parsed_models
        ]

        # Find the last user message to enhance
        last_user_idx = None
        for i in range(len(chat_messages) - 1, -1, -1):
            if chat_messages[i].role == "user":
                last_user_idx = i
                break

        if last_user_idx is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "At least one user message is required",
                },
            )

        # Handle uploads (if any)
        uploaded_infos: List[Tuple[str, str, str]] = []
        if files:
            if rag_manager is None or not rag_manager.is_ready:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "status": "error",
                        "message": "RAG system not available to process uploads",
                    },
                )
            temp_dir, uploaded_infos = _save_uploads_to_temp(files)

        # Enhance last user message with RAG context
        original_content = chat_messages[last_user_idx].content
        enhanced_content, rag_metadata = await _enhance_message_with_rag(
            original_content, rag_manager, uploaded_infos
        )
        
        # Update the message with enhanced content
        chat_messages[last_user_idx] = ChatMessage(role="user", content=enhanced_content)

        # Build request
        models = [m.strip() for m in (allowed_models or "gpt-4o-mini").split(",") if m.strip()]
        chat_request = ChatCompletionRequest(
            messages=chat_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            allowed_models=models,
        )

        # Send to CI&T Flow API
        response = client.send_chat_request(chat_request)
        response_dict = response.to_dict()
        response_dict["rag_metadata"] = rag_metadata
        
        return response_dict

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Invalid request parameters", "error": str(e)},
        )
    except APIConfigurationError as e:
        raise HTTPException(
            status_code=500, 
            detail={"status": "error", "message": "Configuration error", "error": str(e)}
        )
    except APIAuthenticationError as e:
        raise HTTPException(
            status_code=401, 
            detail={"status": "error", "message": "Authentication failed", "error": str(e)}
        )
    except (APIConnectionError, APITimeoutError) as e:
        raise HTTPException(
            status_code=503, 
            detail={"status": "error", "message": "External API is unreachable", "error": str(e)}
        )
    except (APIHTTPError, APIResponseError) as e:
        raise HTTPException(
            status_code=502, 
            detail={"status": "error", "message": "External API returned an error", "error": str(e)}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in chat completion: %s", e)
        raise HTTPException(
            status_code=500, 
            detail={"status": "error", "message": "Unexpected error during chat completion", "error": str(e)}
        )
    finally:
        _cleanup_temp_dir(temp_dir)
        # Close file streams
        for f in files or []:
            try:
                f.file.close()
            except Exception:
                pass