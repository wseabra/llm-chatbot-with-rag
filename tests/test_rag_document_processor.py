"""
Tests for RAG document processor functionality.

This module contains comprehensive tests for the DocumentProcessor class,
including document processing, chunking, and error handling.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from langchain.schema import Document

from src.rag.document_processor import DocumentProcessor, ProcessedDocument, ProcessingConfig
from src.rag.document_loader import DocumentMetadata
from src.rag.exceptions import DocumentProcessingError, UnsupportedFileTypeError


# Module-level fixtures
@pytest.fixture
def temp_documents():
    """Create temporary test documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test text file
        text_file = temp_path / "test.txt"
        text_content = "This is a test document.\n\nIt has multiple paragraphs.\n\nEach paragraph contains some text."
        text_file.write_text(text_content, encoding='utf-8')
        
        # Create test markdown file
        md_file = temp_path / "test.md"
        md_content = "# Test Document\n\nThis is a markdown document.\n\n## Section 1\n\nContent here."
        md_file.write_text(md_content, encoding='utf-8')
        
        # Create mock PDF file (for testing purposes)
        pdf_file = temp_path / "test.pdf"
        pdf_file.write_bytes(b"Mock PDF content for testing")
        
        yield {
            'text_file': text_file,
            'md_file': md_file,
            'pdf_file': pdf_file,
            'text_content': text_content,
            'md_content': md_content
        }


@pytest.fixture
def sample_metadata(temp_documents):
    """Create sample DocumentMetadata objects."""
    return {
        'text': DocumentMetadata(
            file_path=str(temp_documents['text_file']),
            file_name="test.txt",
            file_size=len(temp_documents['text_content']),
            file_extension=".txt",
            modified_date=datetime.now(),
            relative_path="test.txt"
        ),
        'md': DocumentMetadata(
            file_path=str(temp_documents['md_file']),
            file_name="test.md",
            file_size=len(temp_documents['md_content']),
            file_extension=".md",
            modified_date=datetime.now(),
            relative_path="test.md"
        ),
        'pdf': DocumentMetadata(
            file_path=str(temp_documents['pdf_file']),
            file_name="test.pdf",
            file_size=20,
            file_extension=".pdf",
            modified_date=datetime.now(),
            relative_path="test.pdf"
        )
    }


@pytest.fixture
def processor_with_mocks():
    """Create a DocumentProcessor with mocked dependencies."""
    with patch('src.rag.document_processor.TextLoader'), \
         patch('src.rag.document_processor.PyPDFLoader'):
        yield DocumentProcessor()


class TestProcessingConfig:
    """Test cases for ProcessingConfig dataclass."""
    
    def test_processing_config_defaults(self):
        """Test ProcessingConfig with default values."""
        config = ProcessingConfig()
        
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200
        assert config.separators == ["\n\n", "\n", " ", ""]
        assert config.keep_separator is False
        assert config.length_function is None
    
    def test_processing_config_custom_values(self):
        """Test ProcessingConfig with custom values."""
        config = ProcessingConfig(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n", " "],
            keep_separator=True
        )
        
        assert config.chunk_size == 500
        assert config.chunk_overlap == 100
        assert config.separators == ["\n", " "]
        assert config.keep_separator is True
    
    def test_processing_config_post_init(self):
        """Test ProcessingConfig __post_init__ method."""
        config = ProcessingConfig(separators=None)
        
        assert config.separators == ["\n\n", "\n", " ", ""]


class TestDocumentProcessor:
    """Test cases for DocumentProcessor class."""
    
    def test_document_processor_init_default(self):
        """Test DocumentProcessor initialization with default config."""
        processor = DocumentProcessor()
        
        assert processor.config.chunk_size == 1000
        assert processor.config.chunk_overlap == 200
        assert processor._text_splitter is not None
    
    def test_document_processor_init_custom_config(self):
        """Test DocumentProcessor initialization with custom config."""
        config = ProcessingConfig(chunk_size=500, chunk_overlap=50)
        processor = DocumentProcessor(config)
        
        assert processor.config.chunk_size == 500
        assert processor.config.chunk_overlap == 50
    
    def test_load_text_document(self, temp_documents):
        """Test loading text documents."""
        processor = DocumentProcessor()
        
        with patch('src.rag.document_processor.TextLoader') as mock_loader_class:
            mock_loader = MagicMock()
            mock_loader_class.return_value = mock_loader
            mock_loader.load.return_value = [
                Document(page_content=temp_documents['text_content'], metadata={'source': str(temp_documents['text_file'])})
            ]
            
            documents = processor._load_text_document(str(temp_documents['text_file']))
            
            assert len(documents) == 1
            assert documents[0].page_content == temp_documents['text_content']
            mock_loader_class.assert_called_once_with(str(temp_documents['text_file']), encoding='utf-8')
    
    def test_load_text_document_encoding_fallback(self, temp_documents):
        """Test text document loading with encoding fallback."""
        processor = DocumentProcessor()
        
        with patch('src.rag.document_processor.TextLoader') as mock_loader_class:
            # First call (utf-8) raises UnicodeDecodeError
            # Second call (latin-1) succeeds
            mock_loader_utf8 = MagicMock()
            mock_loader_latin1 = MagicMock()
            
            mock_loader_utf8.load.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')
            mock_loader_latin1.load.return_value = [
                Document(page_content="Decoded content", metadata={'source': str(temp_documents['text_file'])})
            ]
            
            mock_loader_class.side_effect = [mock_loader_utf8, mock_loader_latin1]
            
            documents = processor._load_text_document(str(temp_documents['text_file']))
            
            assert len(documents) == 1
            assert documents[0].page_content == "Decoded content"
            assert mock_loader_class.call_count == 2
    
    def test_load_pdf_document(self, temp_documents):
        """Test loading PDF documents."""
        processor = DocumentProcessor()
        
        with patch('src.rag.document_processor.PyPDFLoader') as mock_loader_class:
            mock_loader = MagicMock()
            mock_loader_class.return_value = mock_loader
            mock_loader.load.return_value = [
                Document(page_content="PDF content", metadata={'source': str(temp_documents['pdf_file'])})
            ]
            
            documents = processor._load_pdf_document(str(temp_documents['pdf_file']))
            
            assert len(documents) == 1
            assert documents[0].page_content == "PDF content"
            mock_loader_class.assert_called_once_with(str(temp_documents['pdf_file']))
    
    def test_load_document_by_type_text(self, sample_metadata):
        """Test loading document by type for text files."""
        processor = DocumentProcessor()
        
        with patch.object(processor, '_load_text_document') as mock_load_text:
            mock_load_text.return_value = [Document(page_content="Text content")]
            
            documents = processor._load_document_by_type(sample_metadata['text'])
            
            assert len(documents) == 1
            mock_load_text.assert_called_once_with(sample_metadata['text'].file_path)
    
    def test_load_document_by_type_pdf(self, sample_metadata):
        """Test loading document by type for PDF files."""
        processor = DocumentProcessor()
        
        with patch.object(processor, '_load_pdf_document') as mock_load_pdf:
            mock_load_pdf.return_value = [Document(page_content="PDF content")]
            
            documents = processor._load_document_by_type(sample_metadata['pdf'])
            
            assert len(documents) == 1
            mock_load_pdf.assert_called_once_with(sample_metadata['pdf'].file_path)
    
    def test_load_document_by_type_unsupported(self):
        """Test loading document with unsupported file type."""
        processor = DocumentProcessor()
        
        # Create metadata with unsupported extension
        unsupported_metadata = DocumentMetadata(
            file_path="/path/to/file.docx",
            file_name="file.docx",
            file_size=1000,
            file_extension=".docx",
            modified_date=datetime.now(),
            relative_path="file.docx"
        )
        
        with pytest.raises(UnsupportedFileTypeError):
            processor._load_document_by_type(unsupported_metadata)
    
    def test_enhance_document_metadata(self, sample_metadata):
        """Test document metadata enhancement."""
        processor = DocumentProcessor()
        
        documents = [
            Document(page_content="Content 1", metadata={'page': 1}),
            Document(page_content="Content 2", metadata={'page': 2})
        ]
        
        enhanced = processor._enhance_document_metadata(documents, sample_metadata['text'])
        
        assert len(enhanced) == 2
        
        # Check first document
        assert enhanced[0].page_content == "Content 1"
        assert enhanced[0].metadata['source_file'] == sample_metadata['text'].file_path
        assert enhanced[0].metadata['source_name'] == "test.txt"
        assert enhanced[0].metadata['chunk_index'] == 0
        assert enhanced[0].metadata['total_chunks'] == 2
        assert enhanced[0].metadata['page'] == 1  # Original metadata preserved
        
        # Check second document
        assert enhanced[1].metadata['chunk_index'] == 1
        assert enhanced[1].metadata['total_chunks'] == 2
    
    def test_split_documents(self):
        """Test document splitting."""
        processor = DocumentProcessor(ProcessingConfig(chunk_size=50, chunk_overlap=10))
        
        long_content = "This is a very long document. " * 10  # Create long content
        documents = [Document(page_content=long_content, metadata={'source': 'test'})]
        
        chunks = processor._split_documents(documents)
        
        assert len(chunks) > 1  # Should be split into multiple chunks
        assert all(isinstance(chunk, Document) for chunk in chunks)
    
    def test_process_document_success(self, sample_metadata):
        """Test successful document processing."""
        processor = DocumentProcessor()
        
        with patch.object(processor, '_load_document_by_type') as mock_load, \
             patch.object(processor, '_enhance_document_metadata') as mock_enhance, \
             patch.object(processor, '_split_documents') as mock_split:
            
            # Setup mocks
            mock_documents = [Document(page_content="Test content", metadata={})]
            mock_enhanced = [Document(page_content="Test content", metadata={'enhanced': True})]
            mock_chunks = [
                Document(page_content="Chunk 1", metadata={'enhanced': True}),
                Document(page_content="Chunk 2", metadata={'enhanced': True})
            ]
            
            mock_load.return_value = mock_documents
            mock_enhance.return_value = mock_enhanced
            mock_split.return_value = mock_chunks
            
            # Process document
            result = processor.process_document(sample_metadata['text'])
            
            # Verify result
            assert isinstance(result, ProcessedDocument)
            assert result.source_metadata == sample_metadata['text']
            assert result.chunks == mock_chunks
            assert result.processing_metadata['original_chunks'] == 1
            assert result.processing_metadata['final_chunks'] == 2
            assert result.processing_metadata['chunk_size'] == 1000
    
    def test_process_document_error_handling(self, sample_metadata):
        """Test document processing error handling."""
        processor = DocumentProcessor()
        
        with patch.object(processor, '_load_document_by_type', side_effect=Exception("Load error")):
            with pytest.raises(DocumentProcessingError, match="Unexpected error during document processing"):
                processor.process_document(sample_metadata['text'])
    
    def test_process_documents_batch(self, sample_metadata):
        """Test batch document processing."""
        processor = DocumentProcessor()
        
        with patch.object(processor, 'process_document') as mock_process:
            # Setup mock to return processed documents
            mock_processed = [
                ProcessedDocument(
                    source_metadata=sample_metadata['text'],
                    chunks=[Document(page_content="Chunk", metadata={})],
                    processing_metadata={'final_chunks': 1}
                ),
                ProcessedDocument(
                    source_metadata=sample_metadata['md'],
                    chunks=[Document(page_content="Chunk", metadata={})],
                    processing_metadata={'final_chunks': 1}
                )
            ]
            mock_process.side_effect = mock_processed
            
            # Process batch
            documents_list = [sample_metadata['text'], sample_metadata['md']]
            results = processor.process_documents(documents_list)
            
            assert len(results) == 2
            assert all(isinstance(result, ProcessedDocument) for result in results)
            assert mock_process.call_count == 2
    
    def test_process_documents_with_failures(self, sample_metadata):
        """Test batch processing with some failures."""
        processor = DocumentProcessor()
        
        with patch.object(processor, 'process_document') as mock_process:
            # First document succeeds, second fails
            mock_process.side_effect = [
                ProcessedDocument(
                    source_metadata=sample_metadata['text'],
                    chunks=[Document(page_content="Chunk", metadata={})],
                    processing_metadata={'final_chunks': 1}
                ),
                DocumentProcessingError("Processing failed", sample_metadata['md'].file_path)
            ]
            
            documents_list = [sample_metadata['text'], sample_metadata['md']]
            results = processor.process_documents(documents_list)
            
            # Should return only successful results
            assert len(results) == 1
            assert results[0].source_metadata == sample_metadata['text']
    
    def test_get_processing_stats_empty(self):
        """Test processing statistics with empty list."""
        processor = DocumentProcessor()
        
        stats = processor.get_processing_stats([])
        
        assert stats['total_documents'] == 0
        assert stats['total_chunks'] == 0
        assert stats['total_characters'] == 0
        assert stats['average_chunks_per_document'] == 0
        assert stats['average_characters_per_chunk'] == 0
    
    def test_get_processing_stats_with_documents(self, sample_metadata):
        """Test processing statistics with processed documents."""
        processor = DocumentProcessor()
        
        processed_docs = [
            ProcessedDocument(
                source_metadata=sample_metadata['text'],
                chunks=[
                    Document(page_content="Chunk 1", metadata={}),
                    Document(page_content="Chunk 2", metadata={})
                ],
                processing_metadata={'total_characters': 100}
            ),
            ProcessedDocument(
                source_metadata=sample_metadata['md'],
                chunks=[Document(page_content="Chunk 3", metadata={})],
                processing_metadata={'total_characters': 50}
            )
        ]
        
        stats = processor.get_processing_stats(processed_docs)
        
        assert stats['total_documents'] == 2
        assert stats['total_chunks'] == 3
        assert stats['total_characters'] == 150
        assert stats['average_chunks_per_document'] == 1.5
        assert stats['average_characters_per_chunk'] == 50.0
    
    def test_update_config(self):
        """Test configuration update."""
        processor = DocumentProcessor()
        original_chunk_size = processor.config.chunk_size
        
        new_config = ProcessingConfig(chunk_size=2000, chunk_overlap=400)
        processor.update_config(new_config)
        
        assert processor.config.chunk_size == 2000
        assert processor.config.chunk_overlap == 400
        assert processor.config.chunk_size != original_chunk_size


class TestDocumentProcessorErrorHandling:
    """Test error handling in DocumentProcessor."""
    
    def test_load_text_document_all_encodings_fail(self, temp_documents):
        """Test text loading when all encodings fail."""
        processor = DocumentProcessor()
        
        with patch('src.rag.document_processor.TextLoader') as mock_loader_class:
            mock_loader = MagicMock()
            mock_loader_class.return_value = mock_loader
            mock_loader.load.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')
            
            with pytest.raises(DocumentProcessingError, match="Failed to decode text file"):
                processor._load_text_document(str(temp_documents['text_file']))
    
    def test_load_pdf_document_error(self, temp_documents):
        """Test PDF loading error handling."""
        processor = DocumentProcessor()
        
        with patch('src.rag.document_processor.PyPDFLoader') as mock_loader_class:
            mock_loader = MagicMock()
            mock_loader_class.return_value = mock_loader
            mock_loader.load.side_effect = Exception("PDF parsing error")
            
            with pytest.raises(DocumentProcessingError, match="Failed to load PDF document"):
                processor._load_pdf_document(str(temp_documents['pdf_file']))
    
    def test_split_documents_error(self):
        """Test document splitting error handling."""
        processor = DocumentProcessor()
        
        with patch.object(processor._text_splitter, 'split_documents', side_effect=Exception("Split error")):
            documents = [Document(page_content="Test", metadata={})]
            
            with pytest.raises(DocumentProcessingError, match="Failed to split documents"):
                processor._split_documents(documents)


class TestProcessedDocument:
    """Test ProcessedDocument dataclass."""
    
    def test_processed_document_creation(self, sample_metadata):
        """Test ProcessedDocument creation."""
        chunks = [Document(page_content="Chunk", metadata={})]
        processing_metadata = {'chunks': 1}
        
        processed_doc = ProcessedDocument(
            source_metadata=sample_metadata['text'],
            chunks=chunks,
            processing_metadata=processing_metadata
        )
        
        assert processed_doc.source_metadata == sample_metadata['text']
        assert processed_doc.chunks == chunks
        assert processed_doc.processing_metadata == processing_metadata