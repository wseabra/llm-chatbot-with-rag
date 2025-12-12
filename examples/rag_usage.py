"""
RAG Document Processing Usage Examples.

This module demonstrates how to use the RAG document loading and processing
functionality with various configuration options and error handling.
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.config import Config
from src.rag import (
    DocumentLoader, DocumentProcessor, ProcessingConfig,
    EmbeddingManager, EmbeddingConfig, EmbeddingModelType,
    RAGError, DocumentLoadError, DocumentProcessingError
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demonstrate_document_loading():
    """Demonstrate document loading functionality."""
    print("\n" + "="*60)
    print("DOCUMENT LOADING DEMONSTRATION")
    print("="*60)
    
    try:
        # Load configuration
        config = Config()
        config_dict = config.load_config()
        rag_folder = config_dict['RAG_FOLDER']
        
        print(f"Loading documents from: {rag_folder}")
        
        # Initialize document loader
        loader = DocumentLoader(rag_folder)
        
        # Get document statistics
        stats = loader.get_document_stats()
        print(f"\nDocument Statistics:")
        print(f"  Total documents: {stats['total_documents']}")
        print(f"  Text files (.txt): {stats['txt_files']}")
        print(f"  Markdown files (.md): {stats['md_files']}")
        print(f"  PDF files (.pdf): {stats['pdf_files']}")
        print(f"  Total size: {stats['total_size_bytes']:,} bytes")
        
        # Load all documents
        documents = loader.load_documents(recursive=True)
        
        print(f"\nLoaded {len(documents)} documents:")
        for doc in documents[:5]:  # Show first 5 documents
            print(f"  - {doc.relative_path} ({doc.file_size:,} bytes, {doc.file_extension})")
        
        if len(documents) > 5:
            print(f"  ... and {len(documents) - 5} more documents")
        
        return documents
        
    except DocumentLoadError as e:
        print(f"Document loading error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def demonstrate_document_processing(documents):
    """Demonstrate document processing functionality."""
    print("\n" + "="*60)
    print("DOCUMENT PROCESSING DEMONSTRATION")
    print("="*60)
    
    if not documents:
        print("No documents to process. Skipping processing demonstration.")
        return []
    
    try:
        # Create processing configuration
        config = ProcessingConfig(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " "]
        )
        
        print(f"Processing Configuration:")
        print(f"  Chunk size: {config.chunk_size}")
        print(f"  Chunk overlap: {config.chunk_overlap}")
        print(f"  Separators: {config.separators}")
        
        # Initialize document processor
        processor = DocumentProcessor(config)
        
        # Process a subset of documents for demonstration
        sample_documents = documents[:3] if len(documents) >= 3 else documents
        print(f"\nProcessing {len(sample_documents)} sample documents...")
        
        processed_documents = processor.process_documents(sample_documents)
        
        # Show processing statistics
        stats = processor.get_processing_stats(processed_documents)
        print(f"\nProcessing Statistics:")
        print(f"  Total documents processed: {stats['total_documents']}")
        print(f"  Total chunks created: {stats['total_chunks']}")
        print(f"  Total characters: {stats['total_characters']:,}")
        print(f"  Average chunks per document: {stats['average_chunks_per_document']:.1f}")
        print(f"  Average characters per chunk: {stats['average_characters_per_chunk']:.1f}")
        
        # Show sample chunks
        print(f"\nSample chunks:")
        for i, processed_doc in enumerate(processed_documents[:2]):
            print(f"\n  Document {i+1}: {processed_doc.source_metadata.file_name}")
            for j, chunk in enumerate(processed_doc.chunks[:2]):
                content_preview = chunk.page_content[:100].replace('\n', ' ')
                print(f"    Chunk {j+1}: {content_preview}...")
        
        return processed_documents
        
    except DocumentProcessingError as e:
        print(f"Document processing error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def demonstrate_embedding_preparation(processed_documents):
    """Demonstrate embedding preparation functionality."""
    print("\n" + "="*60)
    print("EMBEDDING PREPARATION DEMONSTRATION")
    print("="*60)
    
    if not processed_documents:
        print("No processed documents available. Skipping embedding demonstration.")
        return
    
    try:
        # Create embedding configuration
        embedding_config = EmbeddingConfig(
            model_type=EmbeddingModelType.SENTENCE_TRANSFORMERS,
            model_name="all-MiniLM-L6-v2",
            batch_size=16,
            normalize_embeddings=True
        )
        
        print(f"Embedding Configuration:")
        print(f"  Model type: {embedding_config.model_type.value}")
        print(f"  Model name: {embedding_config.model_name}")
        print(f"  Batch size: {embedding_config.batch_size}")
        print(f"  Normalize embeddings: {embedding_config.normalize_embeddings}")
        
        # Initialize embedding manager
        embedding_manager = EmbeddingManager(embedding_config)
        embedding_manager.initialize()
        
        print(f"\nEmbedding Manager initialized successfully")
        print(f"  Embedding dimension: {embedding_manager.embedding_dimension}")
        
        # Prepare document chunks for embedding
        all_chunks = []
        for processed_doc in processed_documents:
            all_chunks.extend(processed_doc.chunks)
        
        print(f"\nPreparing embeddings for {len(all_chunks)} chunks...")
        
        # Generate embeddings (using placeholder implementation)
        embedded_documents = embedding_manager.embed_document_chunks(all_chunks[:5])  # Sample 5 chunks
        
        print(f"Generated embeddings for {len(embedded_documents)} chunks")
        
        # Show sample embedded document
        if embedded_documents:
            sample_doc = embedded_documents[0]
            print(f"\nSample embedded document:")
            print(f"  Content preview: {sample_doc['content'][:100]}...")
            print(f"  Embedding dimension: {len(sample_doc['embedding'])}")
            print(f"  Embedding model: {sample_doc['embedding_model']}")
            print(f"  Source file: {sample_doc['metadata'].get('source_name', 'Unknown')}")
        
        # Demonstrate query embedding
        test_query = "What is the main topic of these documents?"
        query_embedding = embedding_manager.embed_query(test_query)
        
        print(f"\nQuery embedding example:")
        print(f"  Query: '{test_query}'")
        print(f"  Embedding dimension: {len(query_embedding)}")
        print(f"  First 5 values: {query_embedding[:5]}")
        
    except Exception as e:
        print(f"Embedding error: {e}")


def demonstrate_error_handling():
    """Demonstrate error handling scenarios."""
    print("\n" + "="*60)
    print("ERROR HANDLING DEMONSTRATION")
    print("="*60)
    
    # Test invalid folder
    print("1. Testing invalid document folder...")
    try:
        loader = DocumentLoader("/nonexistent/folder")
    except DocumentLoadError as e:
        print(f"   ✓ Caught expected error: {e}")
    
    # Test unsupported file type
    print("\n2. Testing unsupported file type processing...")
    try:
        from src.rag.document_loader import DocumentMetadata
        from datetime import datetime
        
        unsupported_metadata = DocumentMetadata(
            file_path="/path/to/file.docx",
            file_name="file.docx",
            file_size=1000,
            file_extension=".docx",
            modified_date=datetime.now(),
            relative_path="file.docx"
        )
        
        processor = DocumentProcessor()
        processor.process_document(unsupported_metadata)
        
    except Exception as e:
        print(f"   ✓ Caught expected error: {type(e).__name__}: {e}")
    
    # Test uninitialized embedding manager
    print("\n3. Testing uninitialized embedding manager...")
    try:
        manager = EmbeddingManager()
        manager.embed_query("test")
    except Exception as e:
        print(f"   ✓ Caught expected error: {type(e).__name__}: {e}")
    
    print("\nError handling demonstration completed.")


def demonstrate_configuration_options():
    """Demonstrate different configuration options."""
    print("\n" + "="*60)
    print("CONFIGURATION OPTIONS DEMONSTRATION")
    print("="*60)
    
    # Different processing configurations
    configs = [
        ProcessingConfig(chunk_size=200, chunk_overlap=50, separators=["\n\n", "\n"]),
        ProcessingConfig(chunk_size=1000, chunk_overlap=200, separators=[". ", "\n", " "]),
        ProcessingConfig(chunk_size=2000, chunk_overlap=400, keep_separator=True)
    ]
    
    print("Processing Configuration Options:")
    for i, config in enumerate(configs, 1):
        print(f"\n  Configuration {i}:")
        print(f"    Chunk size: {config.chunk_size}")
        print(f"    Chunk overlap: {config.chunk_overlap}")
        print(f"    Separators: {config.separators}")
        print(f"    Keep separator: {config.keep_separator}")
    
    # Different embedding configurations
    embedding_configs = [
        EmbeddingConfig(model_name="all-MiniLM-L6-v2", batch_size=32),
        EmbeddingConfig(model_name="all-mpnet-base-v2", batch_size=16),
        EmbeddingConfig(model_name="paraphrase-MiniLM-L6-v2", normalize_embeddings=False)
    ]
    
    print("\nEmbedding Configuration Options:")
    for i, config in enumerate(embedding_configs, 1):
        print(f"\n  Configuration {i}:")
        print(f"    Model name: {config.model_name}")
        print(f"    Batch size: {config.batch_size}")
        print(f"    Normalize embeddings: {config.normalize_embeddings}")


def demonstrate_performance_considerations():
    """Demonstrate performance considerations and best practices."""
    print("\n" + "="*60)
    print("PERFORMANCE CONSIDERATIONS")
    print("="*60)
    
    print("Best Practices for RAG Document Processing:")
    print("\n1. Document Loading:")
    print("   - Use recursive=False for large directory structures when possible")
    print("   - Validate document folder before processing")
    print("   - Monitor file sizes and implement size limits if needed")
    
    print("\n2. Document Processing:")
    print("   - Choose chunk size based on your embedding model's context window")
    print("   - Balance chunk overlap vs. processing time")
    print("   - Process documents in batches for large collections")
    
    print("\n3. Embedding Generation:")
    print("   - Use appropriate batch sizes for your hardware")
    print("   - Consider caching embeddings for frequently accessed documents")
    print("   - Monitor memory usage with large document collections")
    
    print("\n4. Error Handling:")
    print("   - Always handle file access permissions gracefully")
    print("   - Implement retry logic for transient failures")
    print("   - Log processing statistics for monitoring")


def main():
    """Main demonstration function."""
    print("RAG Document Processing Usage Examples")
    print("=" * 60)
    
    try:
        # Check if configuration is available
        config = Config()
        config_dict = config.load_config()
        
        print(f"Configuration loaded successfully:")
        print(f"  RAG Folder: {config_dict['RAG_FOLDER']}")
        
        # Run demonstrations
        documents = demonstrate_document_loading()
        processed_documents = demonstrate_document_processing(documents)
        demonstrate_embedding_preparation(processed_documents)
        demonstrate_error_handling()
        demonstrate_configuration_options()
        demonstrate_performance_considerations()
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\nConfiguration error: {e}")
        print("\nPlease ensure:")
        print("1. You have a .env file with RAG_FOLDER configured")
        print("2. The RAG_FOLDER path exists and contains some documents")
        print("3. You have the required dependencies installed")
        
        # Still run some demonstrations that don't require configuration
        demonstrate_error_handling()
        demonstrate_configuration_options()
        demonstrate_performance_considerations()


if __name__ == "__main__":
    main()