"""
Upload routes for chat + document RAG integration.

Provides a combined endpoint to receive chat messages with optional file uploads
and applies RAG using both pre-loaded and newly uploaded documents.
"""

import io
import json
import logging
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ...flowApi.client import APIClient
from ...flowApi.models import ChatMessage, ChatCompletionRequest
from ...flowApi.exceptions import (
    APIConnectionError, APITimeoutError, APIHTTPError,
    APIResponseError, APIAuthenticationError, APIConfigurationError,
)
from ..clientManager import ClientManager
from ..rag_dependency import get_rag_manager_optional
from ...rag.rag_manager import RAGManager
from .chat import ChatMessageModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


async def get_api_client() -> APIClient:
    return await ClientManager.get_client()


def _validate_file(file: UploadFile) -> None:
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
    if temp_dir and temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            logger.warning("Failed to remove temp dir: %s", temp_dir)


@router.post("/uploaded")
async def chat_with_uploads(
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
    Combined chat + upload endpoint. Enhances last user message with context from
    both pre-indexed and newly uploaded documents using RAG.
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

        # Determine last user message index
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

        # Enhance last user message content using RAG
        rag_metadata: Dict[str, Any] = {
            "rag_enabled": False,
            "sources_used": 0,
            "context_provided": False,
        }

        if rag_manager is not None and rag_manager.is_ready:
            try:
                original = chat_messages[last_user_idx].content
                if uploaded_infos:
                    enhanced, context_chunks = await rag_manager.process_uploaded_documents_with_context(
                        original, uploaded_infos
                    )
                else:
                    enhanced, context_chunks = await rag_manager.enhance_query_with_context(original)

                chat_messages[last_user_idx] = ChatMessage(role="user", content=enhanced)

                # build metadata
                rag_metadata.update(
                    {
                        "rag_enabled": True,
                        "sources_used": len(context_chunks),
                        "context_provided": len(context_chunks) > 0,
                        "similarity_threshold": rag_manager.config.similarity_threshold,
                        "sources": [c.get("source_file", "Unknown") for c in context_chunks],
                        "similarity_scores": [c.get("similarity_score", 0.0) for c in context_chunks],
                        "uploaded_documents": [info[2] for info in uploaded_infos],
                    }
                )
            except Exception as e:
                logger.warning("RAG enhancement failed: %s", e)
                # fallback to original message
        # else: no RAG; proceed as-is

        # Build request
        models = [m.strip() for m in (allowed_models or "gpt-4o-mini").split(",") if m.strip()]
        chat_request = ChatCompletionRequest(
            messages=chat_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            allowed_models=models,
        )

        # Send to CI&T Flow
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
        raise HTTPException(status_code=500, detail={"status": "error", "message": "Configuration error", "error": str(e)})
    except APIAuthenticationError as e:
        raise HTTPException(status_code=401, detail={"status": "error", "message": "Authentication failed", "error": str(e)})
    except (APIConnectionError, APITimeoutError) as e:
        raise HTTPException(status_code=503, detail={"status": "error", "message": "External API is unreachable", "error": str(e)})
    except (APIHTTPError, APIResponseError) as e:
        raise HTTPException(status_code=502, detail={"status": "error", "message": "External API returned an error", "error": str(e)})
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in chat_with_uploads: %s", e)
        raise HTTPException(status_code=500, detail={"status": "error", "message": "Unexpected error during chat with uploads", "error": str(e)})
    finally:
        _cleanup_temp_dir(temp_dir)
        # Close file streams
        for f in files or []:
            try:
                f.file.close()
            except Exception:
                pass
