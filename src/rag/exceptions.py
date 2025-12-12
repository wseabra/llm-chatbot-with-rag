"""
RAG-specific exceptions.

This module defines custom exceptions for RAG document processing operations,
following the same patterns as the existing flowApi exceptions.
"""


class RAGError(Exception):
    """Base exception for all RAG-related errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"RAG Error: {self.message}"


class DocumentLoadError(RAGError):
    """Exception raised when document loading fails."""
    
    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        super().__init__(message)
    
    def __str__(self) -> str:
        if self.file_path:
            return f"Document Load Error [{self.file_path}]: {self.message}"
        return f"Document Load Error: {self.message}"


class DocumentProcessingError(RAGError):
    """Exception raised when document processing fails."""
    
    def __init__(self, message: str, file_path: str = None, processing_stage: str = None):
        self.file_path = file_path
        self.processing_stage = processing_stage
        super().__init__(message)
    
    def __str__(self) -> str:
        error_parts = ["Document Processing Error"]
        if self.file_path:
            error_parts.append(f"[{self.file_path}]")
        if self.processing_stage:
            error_parts.append(f"({self.processing_stage})")
        error_parts.append(f": {self.message}")
        return "".join(error_parts)


class UnsupportedFileTypeError(DocumentLoadError):
    """Exception raised when attempting to load an unsupported file type."""
    
    def __init__(self, file_path: str, file_extension: str = None):
        self.file_extension = file_extension
        message = f"Unsupported file type"
        if file_extension:
            message += f": {file_extension}"
        super().__init__(message, file_path)


class FileAccessError(DocumentLoadError):
    """Exception raised when file access is denied or file is not found."""
    
    def __init__(self, file_path: str, access_type: str = "read"):
        self.access_type = access_type
        message = f"Cannot {access_type} file: permission denied or file not found"
        super().__init__(message, file_path)


class EmbeddingError(RAGError):
    """Exception raised when embedding operations fail."""
    
    def __init__(self, message: str, model_name: str = None):
        self.model_name = model_name
        super().__init__(message)
    
    def __str__(self) -> str:
        if self.model_name:
            return f"Embedding Error [{self.model_name}]: {self.message}"
        return f"Embedding Error: {self.message}"