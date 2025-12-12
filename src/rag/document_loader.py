"""
Document loader for RAG processing.

This module provides functionality to load documents from a specified folder,
supporting text files (.txt, .md) and PDF files (.pdf).
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass
from datetime import datetime

from .exceptions import DocumentLoadError, UnsupportedFileTypeError, FileAccessError


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """Metadata for a loaded document."""
    file_path: str
    file_name: str
    file_size: int
    file_extension: str
    modified_date: datetime
    relative_path: str


class DocumentLoader:
    """
    Loads documents from a specified folder for RAG processing.
    
    Supports recursive folder scanning and filtering by file type.
    Only loads text files (.txt, .md) and PDF files (.pdf).
    """
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.pdf'}
    
    def __init__(self, documents_folder: str):
        """
        Initialize the document loader.
        
        Args:
            documents_folder: Path to the folder containing documents
            
        Raises:
            DocumentLoadError: If the documents folder is invalid
        """
        self.documents_folder = Path(documents_folder)
        self._validate_folder()
    
    def _validate_folder(self) -> None:
        """
        Validate that the documents folder exists and is accessible.
        
        Raises:
            DocumentLoadError: If folder validation fails
        """
        if not self.documents_folder.exists():
            raise DocumentLoadError(
                f"Documents folder does not exist: {self.documents_folder}"
            )
        
        if not self.documents_folder.is_dir():
            raise DocumentLoadError(
                f"Documents path is not a directory: {self.documents_folder}"
            )
        
        if not os.access(self.documents_folder, os.R_OK):
            raise FileAccessError(str(self.documents_folder), "read")
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """
        Check if a file is supported based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is supported, False otherwise
        """
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """
        Check if a file should be skipped (hidden files, system files, etc.).
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be skipped, False otherwise
        """
        # Skip hidden files (starting with .)
        if file_path.name.startswith('.'):
            return True
        
        # Skip system files and directories
        system_patterns = {'__pycache__', '.git', '.svn', 'node_modules', '.DS_Store'}
        if file_path.name in system_patterns:
            return True
        
        return False
    
    def _create_document_metadata(self, file_path: Path) -> DocumentMetadata:
        """
        Create metadata for a document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            DocumentMetadata object
            
        Raises:
            DocumentLoadError: If metadata creation fails
        """
        try:
            stat = file_path.stat()
            relative_path = str(file_path.relative_to(self.documents_folder))
            
            return DocumentMetadata(
                file_path=str(file_path),
                file_name=file_path.name,
                file_size=stat.st_size,
                file_extension=file_path.suffix.lower(),
                modified_date=datetime.fromtimestamp(stat.st_mtime),
                relative_path=relative_path
            )
        except (OSError, ValueError) as e:
            raise DocumentLoadError(
                f"Failed to create metadata for file: {e}",
                str(file_path)
            )
    
    def scan_documents(self, recursive: bool = True) -> Generator[DocumentMetadata, None, None]:
        """
        Scan the documents folder and yield document metadata.
        
        Args:
            recursive: Whether to scan subdirectories recursively
            
        Yields:
            DocumentMetadata for each supported document found
            
        Raises:
            DocumentLoadError: If scanning fails
        """
        try:
            if recursive:
                pattern = "**/*"
            else:
                pattern = "*"
            
            for file_path in self.documents_folder.glob(pattern):
                # Skip directories
                if file_path.is_dir():
                    continue
                
                # Skip files that should be ignored
                if self._should_skip_file(file_path):
                    logger.debug(f"Skipping file: {file_path}")
                    continue
                
                # Check if file is supported
                if not self._is_supported_file(file_path):
                    logger.debug(f"Unsupported file type: {file_path}")
                    continue
                
                # Check file accessibility
                if not os.access(file_path, os.R_OK):
                    logger.warning(f"Cannot read file (permission denied): {file_path}")
                    continue
                
                try:
                    yield self._create_document_metadata(file_path)
                except DocumentLoadError as e:
                    logger.error(f"Failed to process file {file_path}: {e}")
                    continue
                    
        except Exception as e:
            raise DocumentLoadError(f"Failed to scan documents folder: {e}")
    
    def load_documents(self, recursive: bool = True) -> List[DocumentMetadata]:
        """
        Load all supported documents from the folder.
        
        Args:
            recursive: Whether to scan subdirectories recursively
            
        Returns:
            List of DocumentMetadata for all supported documents
            
        Raises:
            DocumentLoadError: If loading fails
        """
        documents = []
        
        try:
            for doc_metadata in self.scan_documents(recursive=recursive):
                documents.append(doc_metadata)
                logger.debug(f"Loaded document: {doc_metadata.relative_path}")
            
            logger.info(f"Successfully loaded {len(documents)} documents from {self.documents_folder}")
            return documents
            
        except Exception as e:
            raise DocumentLoadError(f"Failed to load documents: {e}")
    
    def get_document_stats(self, recursive: bool = True) -> Dict[str, int]:
        """
        Get statistics about documents in the folder.
        
        Args:
            recursive: Whether to scan subdirectories recursively
            
        Returns:
            Dictionary with document statistics
        """
        stats = {
            'total_documents': 0,
            'txt_files': 0,
            'md_files': 0,
            'pdf_files': 0,
            'total_size_bytes': 0
        }
        
        try:
            for doc_metadata in self.scan_documents(recursive=recursive):
                stats['total_documents'] += 1
                stats['total_size_bytes'] += doc_metadata.file_size
                
                if doc_metadata.file_extension == '.txt':
                    stats['txt_files'] += 1
                elif doc_metadata.file_extension == '.md':
                    stats['md_files'] += 1
                elif doc_metadata.file_extension == '.pdf':
                    stats['pdf_files'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get document statistics: {e}")
            return stats
    
    def validate_document_file(self, file_path: str) -> bool:
        """
        Validate that a specific document file can be loaded.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            True if the file is valid and can be loaded, False otherwise
        """
        try:
            path = Path(file_path)
            
            # Check if file exists
            if not path.exists():
                return False
            
            # Check if it's a file (not directory)
            if not path.is_file():
                return False
            
            # Check if file type is supported
            if not self._is_supported_file(path):
                return False
            
            # Check if file is readable
            if not os.access(path, os.R_OK):
                return False
            
            return True
            
        except Exception:
            return False