"""
Tests for RAG document loader functionality.

This module contains comprehensive tests for the DocumentLoader class,
including file system operations, error handling, and edge cases.
"""

import os
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.rag.document_loader import DocumentLoader, DocumentMetadata
from src.rag.exceptions import DocumentLoadError, FileAccessError, UnsupportedFileTypeError


# Module-level fixtures available to all test classes
@pytest.fixture
def temp_documents_folder():
    """Create a temporary folder with test documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        (temp_path / "test.txt").write_text("This is a test text file.")
        (temp_path / "readme.md").write_text("# Test Markdown\nThis is markdown content.")
        (temp_path / "document.pdf").write_bytes(b"Mock PDF content")
        (temp_path / "unsupported.docx").write_bytes(b"Mock DOCX content")
        (temp_path / ".hidden.txt").write_text("Hidden file content")
        
        # Create subdirectory with files
        subdir = temp_path / "subdirectory"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("Nested file content")
        (subdir / "nested.pdf").write_bytes(b"Mock nested PDF")
        
        yield temp_path


@pytest.fixture
def empty_folder():
    """Create an empty temporary folder."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestDocumentLoader:
    """Test cases for DocumentLoader class."""
    
    def test_document_loader_init_valid_folder(self, temp_documents_folder):
        """Test DocumentLoader initialization with valid folder."""
        loader = DocumentLoader(str(temp_documents_folder))
        assert loader.documents_folder == temp_documents_folder
    
    def test_document_loader_init_nonexistent_folder(self):
        """Test DocumentLoader initialization with nonexistent folder."""
        with pytest.raises(DocumentLoadError, match="Documents folder does not exist"):
            DocumentLoader("/nonexistent/folder")
    
    def test_document_loader_init_file_instead_of_folder(self, temp_documents_folder):
        """Test DocumentLoader initialization with file path instead of folder."""
        file_path = temp_documents_folder / "test.txt"
        with pytest.raises(DocumentLoadError, match="Documents path is not a directory"):
            DocumentLoader(str(file_path))
    
    def test_document_loader_init_no_read_permission(self, temp_documents_folder):
        """Test DocumentLoader initialization with no read permission."""
        # Create a separate temporary directory for this test
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)
            
            # Mock os.access to return False only for the specific path
            with patch('os.access') as mock_access:
                def access_side_effect(path, mode):
                    if str(path) == str(test_path):
                        return False
                    return True  # Allow access to other paths
                
                mock_access.side_effect = access_side_effect
                
                with pytest.raises(FileAccessError, match="Cannot read file"):
                    DocumentLoader(str(test_path))
    
    def test_is_supported_file(self, temp_documents_folder):
        """Test file type support detection."""
        loader = DocumentLoader(str(temp_documents_folder))
        
        assert loader._is_supported_file(Path("test.txt"))
        assert loader._is_supported_file(Path("test.md"))
        assert loader._is_supported_file(Path("test.pdf"))
        assert loader._is_supported_file(Path("TEST.TXT"))  # Case insensitive
        assert not loader._is_supported_file(Path("test.docx"))
        assert not loader._is_supported_file(Path("test.jpg"))
    
    def test_should_skip_file(self, temp_documents_folder):
        """Test file skipping logic."""
        loader = DocumentLoader(str(temp_documents_folder))
        
        assert loader._should_skip_file(Path(".hidden.txt"))
        assert loader._should_skip_file(Path("__pycache__"))
        assert loader._should_skip_file(Path(".git"))
        assert loader._should_skip_file(Path(".DS_Store"))
        assert not loader._should_skip_file(Path("normal.txt"))
    
    def test_create_document_metadata(self, temp_documents_folder):
        """Test document metadata creation."""
        loader = DocumentLoader(str(temp_documents_folder))
        file_path = temp_documents_folder / "test.txt"
        
        metadata = loader._create_document_metadata(file_path)
        
        assert isinstance(metadata, DocumentMetadata)
        assert metadata.file_name == "test.txt"
        assert metadata.file_extension == ".txt"
        assert metadata.relative_path == "test.txt"
        assert metadata.file_size > 0
        assert isinstance(metadata.modified_date, datetime)
    
    def test_scan_documents_recursive(self, temp_documents_folder):
        """Test recursive document scanning."""
        loader = DocumentLoader(str(temp_documents_folder))
        
        documents = list(loader.scan_documents(recursive=True))
        
        # Should find supported files in root and subdirectory
        file_names = [doc.file_name for doc in documents]
        assert "test.txt" in file_names
        assert "readme.md" in file_names
        assert "document.pdf" in file_names
        assert "nested.txt" in file_names
        assert "nested.pdf" in file_names
        
        # Should not find unsupported or hidden files
        assert "unsupported.docx" not in file_names
        assert ".hidden.txt" not in file_names
    
    def test_scan_documents_non_recursive(self, temp_documents_folder):
        """Test non-recursive document scanning."""
        loader = DocumentLoader(str(temp_documents_folder))
        
        documents = list(loader.scan_documents(recursive=False))
        
        # Should find supported files only in root directory
        file_names = [doc.file_name for doc in documents]
        assert "test.txt" in file_names
        assert "readme.md" in file_names
        assert "document.pdf" in file_names
        
        # Should not find files in subdirectory
        assert "nested.txt" not in file_names
        assert "nested.pdf" not in file_names
    
    def test_load_documents(self, temp_documents_folder):
        """Test loading all documents."""
        loader = DocumentLoader(str(temp_documents_folder))
        
        documents = loader.load_documents()
        
        assert len(documents) >= 3  # At least the supported files in root
        assert all(isinstance(doc, DocumentMetadata) for doc in documents)
    
    def test_load_documents_empty_folder(self, empty_folder):
        """Test loading documents from empty folder."""
        loader = DocumentLoader(str(empty_folder))
        
        documents = loader.load_documents()
        
        assert documents == []
    
    def test_get_document_stats(self, temp_documents_folder):
        """Test document statistics generation."""
        loader = DocumentLoader(str(temp_documents_folder))
        
        stats = loader.get_document_stats()
        
        assert isinstance(stats, dict)
        assert 'total_documents' in stats
        assert 'txt_files' in stats
        assert 'md_files' in stats
        assert 'pdf_files' in stats
        assert 'total_size_bytes' in stats
        
        assert stats['total_documents'] > 0
        assert stats['txt_files'] >= 1
        assert stats['md_files'] >= 1
        assert stats['pdf_files'] >= 1
        assert stats['total_size_bytes'] > 0
    
    def test_get_document_stats_empty_folder(self, empty_folder):
        """Test document statistics for empty folder."""
        loader = DocumentLoader(str(empty_folder))
        
        stats = loader.get_document_stats()
        
        assert stats['total_documents'] == 0
        assert stats['txt_files'] == 0
        assert stats['md_files'] == 0
        assert stats['pdf_files'] == 0
        assert stats['total_size_bytes'] == 0
    
    def test_validate_document_file_valid(self, temp_documents_folder):
        """Test document file validation for valid files."""
        loader = DocumentLoader(str(temp_documents_folder))
        
        assert loader.validate_document_file(str(temp_documents_folder / "test.txt"))
        assert loader.validate_document_file(str(temp_documents_folder / "readme.md"))
        assert loader.validate_document_file(str(temp_documents_folder / "document.pdf"))
    
    def test_validate_document_file_invalid(self, temp_documents_folder):
        """Test document file validation for invalid files."""
        loader = DocumentLoader(str(temp_documents_folder))
        
        # Nonexistent file
        assert not loader.validate_document_file("/nonexistent/file.txt")
        
        # Unsupported file type
        assert not loader.validate_document_file(str(temp_documents_folder / "unsupported.docx"))
        
        # Directory instead of file
        assert not loader.validate_document_file(str(temp_documents_folder))
    
    def test_validate_document_file_no_permission(self, temp_documents_folder):
        """Test document file validation with no read permission."""
        loader = DocumentLoader(str(temp_documents_folder))
        test_file = str(temp_documents_folder / "test.txt")
        
        # Mock os.access to return False only for the specific file validation
        with patch('os.access') as mock_access:
            def access_side_effect(path, mode):
                if str(path) == test_file:
                    return False
                return True  # Allow access to other paths (like the folder itself)
            
            mock_access.side_effect = access_side_effect
            
            assert not loader.validate_document_file(test_file)


class TestDocumentLoaderErrorHandling:
    """Test error handling in DocumentLoader."""
    
    def test_scan_documents_with_permission_errors(self, temp_documents_folder):
        """Test scanning with file permission errors."""
        loader = DocumentLoader(str(temp_documents_folder))
        
        # Mock os.access to deny access to specific files during scanning
        with patch('os.access') as mock_access:
            def access_side_effect(path, mode):
                # Allow folder access but deny access to test.txt
                if str(path).endswith('test.txt'):
                    return False
                return True
            
            mock_access.side_effect = access_side_effect
            
            documents = list(loader.scan_documents())
            
            # Should skip files without permission but continue with others
            file_names = [doc.file_name for doc in documents]
            assert "test.txt" not in file_names
            assert len(file_names) > 0  # Should still find other files
    
    def test_create_metadata_with_stat_error(self, temp_documents_folder):
        """Test metadata creation with stat errors."""
        loader = DocumentLoader(str(temp_documents_folder))
        file_path = temp_documents_folder / "test.txt"
        
        with patch.object(Path, 'stat', side_effect=OSError("Permission denied")):
            with pytest.raises(DocumentLoadError, match="Failed to create metadata"):
                loader._create_document_metadata(file_path)


class TestDocumentLoaderParametrized:
    """Parametrized tests for DocumentLoader."""
    
    @pytest.mark.parametrize("extension,expected", [
        (".txt", True),
        (".md", True),
        (".pdf", True),
        (".TXT", True),
        (".MD", True),
        (".PDF", True),
        (".docx", False),
        (".jpg", False),
        (".py", False),
        ("", False)
    ])
    def test_supported_extensions(self, extension, expected):
        """Test file extension support detection."""
        # Create a minimal loader for testing (using a temp directory)
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = DocumentLoader(temp_dir)
            test_path = Path(f"test{extension}")
            
            assert loader._is_supported_file(test_path) == expected
    
    @pytest.mark.parametrize("filename,should_skip", [
        (".hidden.txt", True),
        ("__pycache__", True),
        (".git", True),
        (".svn", True),
        ("node_modules", True),
        (".DS_Store", True),
        ("normal.txt", False),
        ("README.md", False),
        ("document.pdf", False)
    ])
    def test_file_skipping_patterns(self, filename, should_skip):
        """Test file skipping patterns."""
        # Create a minimal loader for testing (using a temp directory)
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = DocumentLoader(temp_dir)
            test_path = Path(filename)
            
            assert loader._should_skip_file(test_path) == should_skip


class TestDocumentMetadata:
    """Test DocumentMetadata dataclass."""
    
    def test_document_metadata_creation(self):
        """Test DocumentMetadata creation."""
        metadata = DocumentMetadata(
            file_path="/path/to/file.txt",
            file_name="file.txt",
            file_size=1024,
            file_extension=".txt",
            modified_date=datetime.now(),
            relative_path="file.txt"
        )
        
        assert metadata.file_path == "/path/to/file.txt"
        assert metadata.file_name == "file.txt"
        assert metadata.file_size == 1024
        assert metadata.file_extension == ".txt"
        assert isinstance(metadata.modified_date, datetime)
        assert metadata.relative_path == "file.txt"
    
    def test_document_metadata_equality(self):
        """Test DocumentMetadata equality comparison."""
        now = datetime.now()
        
        metadata1 = DocumentMetadata(
            file_path="/path/to/file.txt",
            file_name="file.txt",
            file_size=1024,
            file_extension=".txt",
            modified_date=now,
            relative_path="file.txt"
        )
        
        metadata2 = DocumentMetadata(
            file_path="/path/to/file.txt",
            file_name="file.txt",
            file_size=1024,
            file_extension=".txt",
            modified_date=now,
            relative_path="file.txt"
        )
        
        assert metadata1 == metadata2