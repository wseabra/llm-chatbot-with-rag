"""
Document processor for RAG processing.

This module provides functionality to process documents using LangChain,
including text extraction, chunking, and metadata preservation.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from .document_loader import DocumentMetadata
from .exceptions import DocumentProcessingError, UnsupportedFileTypeError


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ProcessedDocument:
    """Represents a processed document with chunks and metadata."""
    source_metadata: DocumentMetadata
    chunks: List[Document]
    processing_metadata: Dict[str, Any]


@dataclass
class ProcessingConfig:
    """Configuration for document processing."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: Optional[List[str]] = None
    keep_separator: bool = False
    length_function: Optional[callable] = None
    
    def __post_init__(self):
        """Set default separators if not provided."""
        if self.separators is None:
            self.separators = ["\n\n", "\n", " ", ""]


class DocumentProcessor:
    """
    Processes documents for RAG using LangChain.
    
    Handles text extraction from various file types and splits documents
    into chunks suitable for embedding and retrieval.
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        """
        Initialize the document processor.
        
        Args:
            config: Processing configuration. Uses defaults if not provided.
        """
        self.config = config or ProcessingConfig()
        self._text_splitter = self._create_text_splitter()
    
    def _create_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Create a text splitter based on the configuration.
        
        Returns:
            Configured RecursiveCharacterTextSplitter
        """
        return RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=self.config.separators,
            keep_separator=self.config.keep_separator,
            length_function=self.config.length_function or len
        )
    
    def _load_text_document(self, file_path: str) -> List[Document]:
        """
        Load a text document using LangChain TextLoader.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of Document objects
            
        Raises:
            DocumentProcessingError: If loading fails
        """
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            logger.debug(f"Loaded text document: {file_path}")
            return documents
        except UnicodeDecodeError:
            # Try with different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    loader = TextLoader(file_path, encoding=encoding)
                    documents = loader.load()
                    logger.debug(f"Loaded text document with {encoding} encoding: {file_path}")
                    return documents
                except UnicodeDecodeError:
                    continue
            
            raise DocumentProcessingError(
                f"Failed to decode text file with any supported encoding",
                file_path,
                "text_loading"
            )
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to load text document: {e}",
                file_path,
                "text_loading"
            )
    
    def _load_pdf_document(self, file_path: str) -> List[Document]:
        """
        Load a PDF document using LangChain PyPDFLoader.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of Document objects
            
        Raises:
            DocumentProcessingError: If loading fails
        """
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            logger.debug(f"Loaded PDF document: {file_path}")
            return documents
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to load PDF document: {e}",
                file_path,
                "pdf_loading"
            )
    
    def _load_document_by_type(self, doc_metadata: DocumentMetadata) -> List[Document]:
        """
        Load a document based on its file type.
        
        Args:
            doc_metadata: Document metadata
            
        Returns:
            List of Document objects
            
        Raises:
            UnsupportedFileTypeError: If file type is not supported
            DocumentProcessingError: If loading fails
        """
        file_extension = doc_metadata.file_extension.lower()
        
        if file_extension in ['.txt', '.md']:
            return self._load_text_document(doc_metadata.file_path)
        elif file_extension == '.pdf':
            return self._load_pdf_document(doc_metadata.file_path)
        else:
            raise UnsupportedFileTypeError(
                doc_metadata.file_path,
                file_extension
            )
    
    def _enhance_document_metadata(self, documents: List[Document], 
                                 source_metadata: DocumentMetadata) -> List[Document]:
        """
        Enhance document metadata with source information.
        
        Args:
            documents: List of Document objects
            source_metadata: Source document metadata
            
        Returns:
            List of Document objects with enhanced metadata
        """
        enhanced_documents = []
        
        for i, doc in enumerate(documents):
            # Create enhanced metadata
            enhanced_metadata = {
                **doc.metadata,
                'source_file': source_metadata.file_path,
                'source_name': source_metadata.file_name,
                'file_size': source_metadata.file_size,
                'file_extension': source_metadata.file_extension,
                'modified_date': source_metadata.modified_date.isoformat(),
                'relative_path': source_metadata.relative_path,
                'chunk_index': i,
                'total_chunks': len(documents)
            }
            
            # Create new document with enhanced metadata
            enhanced_doc = Document(
                page_content=doc.page_content,
                metadata=enhanced_metadata
            )
            enhanced_documents.append(enhanced_doc)
        
        return enhanced_documents
    
    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks using the configured text splitter.
        
        Args:
            documents: List of Document objects to split
            
        Returns:
            List of Document chunks
            
        Raises:
            DocumentProcessingError: If splitting fails
        """
        try:
            chunks = self._text_splitter.split_documents(documents)
            logger.debug(f"Split {len(documents)} documents into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to split documents: {e}",
                processing_stage="text_splitting"
            )
    
    def process_document(self, doc_metadata: DocumentMetadata) -> ProcessedDocument:
        """
        Process a single document.
        
        Args:
            doc_metadata: Document metadata
            
        Returns:
            ProcessedDocument with chunks and metadata
            
        Raises:
            DocumentProcessingError: If processing fails
            UnsupportedFileTypeError: If file type is not supported
        """
        try:
            logger.info(f"Processing document: {doc_metadata.relative_path}")
            
            # Load the document
            documents = self._load_document_by_type(doc_metadata)
            
            # Enhance metadata
            documents = self._enhance_document_metadata(documents, doc_metadata)
            
            # Split into chunks
            chunks = self._split_documents(documents)
            
            # Create processing metadata
            processing_metadata = {
                'original_chunks': len(documents),
                'final_chunks': len(chunks),
                'chunk_size': self.config.chunk_size,
                'chunk_overlap': self.config.chunk_overlap,
                'total_characters': sum(len(chunk.page_content) for chunk in chunks),
                'processing_timestamp': logger.handlers[0].formatter.formatTime(
                    logging.LogRecord('', 0, '', 0, '', (), None)
                ) if logger.handlers else None
            }
            
            logger.info(f"Successfully processed {doc_metadata.relative_path}: "
                       f"{len(chunks)} chunks, {processing_metadata['total_characters']} characters")
            
            return ProcessedDocument(
                source_metadata=doc_metadata,
                chunks=chunks,
                processing_metadata=processing_metadata
            )
            
        except (DocumentProcessingError, UnsupportedFileTypeError):
            raise
        except Exception as e:
            raise DocumentProcessingError(
                f"Unexpected error during document processing: {e}",
                doc_metadata.file_path,
                "processing"
            )
    
    def process_documents(self, documents_metadata: List[DocumentMetadata]) -> List[ProcessedDocument]:
        """
        Process multiple documents.
        
        Args:
            documents_metadata: List of document metadata
            
        Returns:
            List of ProcessedDocument objects
            
        Raises:
            DocumentProcessingError: If batch processing fails
        """
        processed_documents = []
        failed_documents = []
        
        logger.info(f"Starting batch processing of {len(documents_metadata)} documents")
        
        for doc_metadata in documents_metadata:
            try:
                processed_doc = self.process_document(doc_metadata)
                processed_documents.append(processed_doc)
            except Exception as e:
                logger.error(f"Failed to process document {doc_metadata.relative_path}: {e}")
                failed_documents.append((doc_metadata, str(e)))
                continue
        
        logger.info(f"Batch processing completed: {len(processed_documents)} successful, "
                   f"{len(failed_documents)} failed")
        
        if failed_documents:
            failed_paths = [doc_metadata.relative_path for doc_metadata, _ in failed_documents]
            logger.warning(f"Failed documents: {failed_paths}")
        
        return processed_documents
    
    def get_processing_stats(self, processed_documents: List[ProcessedDocument]) -> Dict[str, Any]:
        """
        Get statistics about processed documents.
        
        Args:
            processed_documents: List of processed documents
            
        Returns:
            Dictionary with processing statistics
        """
        if not processed_documents:
            return {
                'total_documents': 0,
                'total_chunks': 0,
                'total_characters': 0,
                'average_chunks_per_document': 0,
                'average_characters_per_chunk': 0
            }
        
        total_chunks = sum(len(doc.chunks) for doc in processed_documents)
        total_characters = sum(doc.processing_metadata.get('total_characters', 0) 
                             for doc in processed_documents)
        
        return {
            'total_documents': len(processed_documents),
            'total_chunks': total_chunks,
            'total_characters': total_characters,
            'average_chunks_per_document': total_chunks / len(processed_documents),
            'average_characters_per_chunk': total_characters / total_chunks if total_chunks > 0 else 0,
            'chunk_size_config': self.config.chunk_size,
            'chunk_overlap_config': self.config.chunk_overlap
        }
    
    def update_config(self, new_config: ProcessingConfig) -> None:
        """
        Update the processing configuration.
        
        Args:
            new_config: New processing configuration
        """
        self.config = new_config
        self._text_splitter = self._create_text_splitter()
        logger.info(f"Updated processing configuration: chunk_size={self.config.chunk_size}, "
                   f"chunk_overlap={self.config.chunk_overlap}")