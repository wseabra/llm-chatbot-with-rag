# RAG Document Processing Module

This module provides comprehensive functionality for Retrieval-Augmented Generation (RAG) document processing, including document loading, text processing, and embedding preparation.

## Features

### ✅ Implemented
- **Document Loading**: Load documents from configured folder with support for `.txt`, `.md`, and `.pdf` files
- **Document Processing**: Parse and chunk documents using LangChain with configurable parameters
- **Embedding Interface**: Abstract interface with placeholder implementation for future embedding models
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Configuration**: Flexible configuration system for processing and embedding parameters
- **Logging**: Detailed logging for monitoring and debugging

### 🔄 Placeholder (Ready for Implementation)
- **Real Embedding Models**: Sentence Transformers integration (placeholder implemented)
- **Vector Storage**: ChromaDB integration preparation
- **Advanced Text Processing**: Additional document types and processing strategies

## Architecture

The module follows clean architecture principles with clear separation of concerns:

```
src/rag/
├── __init__.py              # Module exports
├── document_loader.py       # Document loading and file system operations
├── document_processor.py    # Document parsing and chunking
├── embeddings.py           # Embedding configuration and providers
├── exceptions.py           # Custom exceptions
└── README.md              # This file
```

## Usage Examples

### Basic Document Loading

```python
from src.rag import DocumentLoader

# Initialize loader with documents folder
loader = DocumentLoader("/path/to/documents")

# Get document statistics
stats = loader.get_document_stats()
print(f"Found {stats['total_documents']} documents")

# Load all documents
documents = loader.load_documents(recursive=True)
```

### Document Processing

```python
from src.rag import DocumentProcessor, ProcessingConfig

# Configure processing parameters
config = ProcessingConfig(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " "]
)

# Initialize processor
processor = DocumentProcessor(config)

# Process documents
processed_docs = processor.process_documents(documents)

# Get processing statistics
stats = processor.get_processing_stats(processed_docs)
print(f"Created {stats['total_chunks']} chunks")
```

### Embedding Preparation

```python
from src.rag import EmbeddingManager, EmbeddingConfig, EmbeddingModelType

# Configure embedding model
config = EmbeddingConfig(
    model_type=EmbeddingModelType.SENTENCE_TRANSFORMERS,
    model_name="all-MiniLM-L6-v2",
    batch_size=32
)

# Initialize embedding manager
manager = EmbeddingManager(config)
manager.initialize()

# Generate embeddings for document chunks
all_chunks = []
for doc in processed_docs:
    all_chunks.extend(doc.chunks)

embedded_docs = manager.embed_document_chunks(all_chunks)

# Generate query embedding
query_embedding = manager.embed_query("What is machine learning?")
```

### Complete Workflow

```python
from src.config.config import Config
from src.rag import DocumentLoader, DocumentProcessor, EmbeddingManager

# Load configuration
config = Config()
config_dict = config.load_config()

# Document loading
loader = DocumentLoader(config_dict['RAG_FOLDER'])
documents = loader.load_documents()

# Document processing
processor = DocumentProcessor()
processed_docs = processor.process_documents(documents)

# Embedding preparation
embedding_manager = EmbeddingManager()
embedding_manager.initialize()

# Process all chunks
all_chunks = []
for doc in processed_docs:
    all_chunks.extend(doc.chunks)

embedded_docs = embedding_manager.embed_document_chunks(all_chunks)
```

## Configuration

### Environment Variables

The module uses the existing configuration system:

```bash
# Required
RAG_FOLDER=/path/to/your/documents

# Optional embedding configuration
EMBEDDING_MODEL_TYPE=sentence-transformers
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=32
```

### Processing Configuration

```python
ProcessingConfig(
    chunk_size=1000,           # Maximum characters per chunk
    chunk_overlap=200,         # Overlap between chunks
    separators=["\n\n", "\n", ". ", " "],  # Text splitting separators
    keep_separator=False,      # Whether to keep separators in chunks
    length_function=len        # Function to measure chunk length
)
```

### Embedding Configuration

```python
EmbeddingConfig(
    model_type=EmbeddingModelType.SENTENCE_TRANSFORMERS,
    model_name="all-MiniLM-L6-v2",
    batch_size=32,
    normalize_embeddings=True
)
```

## Supported File Types

- **Text Files**: `.txt`, `.md`
- **PDF Files**: `.pdf`
- **Future**: Easy to extend for additional formats

## Error Handling

The module provides comprehensive error handling with custom exceptions:

- `RAGError`: Base exception for all RAG operations
- `DocumentLoadError`: Document loading failures
- `DocumentProcessingError`: Document processing failures
- `UnsupportedFileTypeError`: Unsupported file types
- `FileAccessError`: File permission issues
- `EmbeddingError`: Embedding generation failures

## Performance Considerations

### Document Loading
- Recursive scanning can be disabled for large directories
- File validation prevents processing of inaccessible files
- Lazy loading support for memory efficiency

### Document Processing
- Configurable chunk sizes for optimal performance
- Batch processing with error recovery
- Memory-efficient text splitting

### Embedding Generation
- Configurable batch sizes for hardware optimization
- Placeholder implementation for development/testing
- Ready for production embedding models

## Testing

The module includes comprehensive tests:

```bash
# Run document loader tests
python -m pytest tests/test_rag_document_loader.py -v

# Run document processor tests
python -m pytest tests/test_rag_document_processor.py -v

# Run embedding tests
python -m pytest tests/test_rag_embeddings.py -v
```

## Integration with Existing System

The RAG module integrates seamlessly with the existing FastAPI application:

- Uses the same configuration system (`src.config.config`)
- Follows the same error handling patterns
- Maintains the same code quality standards
- Compatible with existing logging and monitoring

## Future Enhancements

### Phase 1 (Current Implementation)
- ✅ Document loading and processing
- ✅ Embedding interface and placeholder
- ✅ Configuration and error handling

### Phase 2 (Next Steps)
- 🔄 Real embedding model integration
- 🔄 Vector database storage (ChromaDB)
- 🔄 Similarity search implementation

### Phase 3 (Advanced Features)
- 🔄 Additional document formats
- 🔄 Advanced chunking strategies
- 🔄 Metadata filtering and search
- 🔄 Performance optimization

## Dependencies

The module requires the following packages (already added to `requirements.txt`):

```
langchain==0.1.0
langchain-community==0.0.10
pypdf==3.17.4
python-magic==0.4.27
tiktoken==0.5.2
chromadb==0.4.18
sentence-transformers==2.2.2
```

## Examples

See `examples/rag_usage.py` for comprehensive usage examples and demonstrations of all functionality.

## Contributing

When extending this module:

1. Follow the existing code patterns and architecture
2. Add comprehensive tests for new functionality
3. Update this README with new features
4. Maintain backward compatibility
5. Follow the project's coding standards (SOLID, DRY, KISS)

## License

This module is part of the FastAPI RAG Application and follows the same licensing terms.