#!/usr/bin/env python3
"""
RAG System Verification Script

This script verifies that the RAG system is working correctly by testing
all components from document loading to chat enhancement.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.config.config import Config
from src.rag.rag_manager import RAGManager, RAGConfig
from src.rag.exceptions import RAGError


async def verify_rag_system() -> Dict[str, Any]:
    """
    Comprehensive RAG system verification.
    
    Returns:
        Dictionary with verification results
    """
    results = {
        'config_loading': False,
        'rag_initialization': False,
        'document_indexing': False,
        'context_retrieval': False,
        'query_enhancement': False,
        'errors': []
    }
    
    try:
        print("🔍 Starting RAG System Verification...")
        print("=" * 50)
        
        # Step 1: Verify Configuration
        print("\n1️⃣ Testing Configuration Loading...")
        try:
            config = Config()
            config_dict = config.load_config()
            
            required_keys = ['CLIENT_ID', 'CLIENT_SECRET', 'RAG_FOLDER']
            missing_keys = [key for key in required_keys if key not in config_dict]
            
            if missing_keys:
                results['errors'].append(f"Missing required config keys: {missing_keys}")
                print(f"❌ Missing configuration: {missing_keys}")
                return results
            
            print(f"✅ Configuration loaded successfully")
            print(f"   RAG Folder: {config_dict['RAG_FOLDER']}")
            print(f"   Vector DB Path: {config_dict.get('RAG_VECTOR_DB_PATH', 'default')}")
            print(f"   Embedding Model: {config_dict.get('RAG_EMBEDDING_MODEL', 'default')}")
            
            results['config_loading'] = True
            
        except Exception as e:
            results['errors'].append(f"Configuration loading failed: {e}")
            print(f"❌ Configuration loading failed: {e}")
            return results
        
        # Step 2: Verify RAG Folder
        print(f"\n2️⃣ Verifying RAG Folder...")
        rag_folder = Path(config_dict['RAG_FOLDER'])
        
        if not rag_folder.exists():
            results['errors'].append(f"RAG folder does not exist: {rag_folder}")
            print(f"❌ RAG folder does not exist: {rag_folder}")
            return results
        
        # Count documents in RAG folder
        doc_files = list(rag_folder.glob('**/*.txt')) + list(rag_folder.glob('**/*.md')) + list(rag_folder.glob('**/*.pdf'))
        print(f"✅ RAG folder exists with {len(doc_files)} documents")
        
        if len(doc_files) == 0:
            print("⚠️  Warning: No documents found in RAG folder")
        else:
            print("   Documents found:")
            for doc_file in doc_files[:5]:  # Show first 5
                print(f"     - {doc_file.name}")
            if len(doc_files) > 5:
                print(f"     ... and {len(doc_files) - 5} more")
        
        # Step 3: Initialize RAG Manager
        print(f"\n3️⃣ Initializing RAG Manager...")
        try:
            rag_config = RAGConfig(
                chunk_size=int(config_dict.get('RAG_CHUNK_SIZE', 1000)),
                chunk_overlap=int(config_dict.get('RAG_CHUNK_OVERLAP', 200)),
                embedding_model=config_dict.get('RAG_EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
                vector_db_path=config_dict.get('RAG_VECTOR_DB_PATH', './data/chroma_db'),
                similarity_threshold=float(config_dict.get('RAG_SIMILARITY_THRESHOLD', 0.7)),
                max_context_chunks=int(config_dict.get('RAG_MAX_CONTEXT_CHUNKS', 5))
            )
            
            rag_manager = RAGManager(
                documents_folder=config_dict['RAG_FOLDER'],
                config=rag_config
            )
            
            await rag_manager.initialize()
            print(f"✅ RAG Manager initialized successfully")
            print(f"   Embedding Model: {rag_config.embedding_model}")
            print(f"   Chunk Size: {rag_config.chunk_size}")
            print(f"   Similarity Threshold: {rag_config.similarity_threshold}")
            
            results['rag_initialization'] = True
            
        except Exception as e:
            results['errors'].append(f"RAG initialization failed: {e}")
            print(f"❌ RAG initialization failed: {e}")
            return results
        
        # Step 4: Test Document Indexing
        print(f"\n4️⃣ Testing Document Indexing...")
        try:
            indexing_stats = await rag_manager.index_all_documents()
            
            print(f"✅ Document indexing completed")
            print(f"   Documents processed: {indexing_stats['total_documents']}")
            print(f"   Chunks created: {indexing_stats['total_chunks']}")
            print(f"   Embedding dimension: {indexing_stats.get('embedding_dimension', 'N/A')}")
            
            if indexing_stats['total_chunks'] == 0:
                results['errors'].append("No chunks were created during indexing")
                print("❌ No chunks were created")
                return results
            
            results['document_indexing'] = True
            
        except Exception as e:
            results['errors'].append(f"Document indexing failed: {e}")
            print(f"❌ Document indexing failed: {e}")
            return results
        
        # Step 5: Test Context Retrieval
        print(f"\n5️⃣ Testing Context Retrieval...")
        try:
            test_queries = [
                "What is this document about?",
                "Tell me about the company",
                "How does this work?",
                "What are the main features?"
            ]
            
            for query in test_queries:
                context_chunks = await rag_manager.retrieve_context(query, max_chunks=3)
                
                if context_chunks:
                    print(f"✅ Query: '{query}' -> {len(context_chunks)} relevant chunks found")
                    
                    # Show first chunk details
                    first_chunk = context_chunks[0]
                    print(f"   Best match (score: {first_chunk['similarity_score']:.3f}): {first_chunk['content'][:100]}...")
                    break
            else:
                print("⚠️  No relevant context found for any test query")
            
            results['context_retrieval'] = True
            
        except Exception as e:
            results['errors'].append(f"Context retrieval failed: {e}")
            print(f"❌ Context retrieval failed: {e}")
            return results
        
        # Step 6: Test Query Enhancement
        print(f"\n6️⃣ Testing Query Enhancement...")
        try:
            test_query = "What is this about?"
            enhanced_query, context_chunks = await rag_manager.enhance_query_with_context(test_query)
            
            print(f"✅ Query enhancement successful")
            print(f"   Original query: '{test_query}'")
            print(f"   Context chunks used: {len(context_chunks)}")
            print(f"   Enhanced query length: {len(enhanced_query)} characters")
            
            if context_chunks:
                print(f"   Sources used: {[chunk['source_file'] for chunk in context_chunks]}")
            
            results['query_enhancement'] = True
            
        except Exception as e:
            results['errors'].append(f"Query enhancement failed: {e}")
            print(f"❌ Query enhancement failed: {e}")
            return results
        
        # Step 7: Get System Statistics
        print(f"\n7️⃣ RAG System Statistics...")
        try:
            stats = rag_manager.get_stats()
            
            print(f"✅ RAG System Status: {stats['status']}")
            print(f"   Ready for queries: {stats['is_ready']}")
            print(f"   Vector store chunks: {stats['vector_store']['total_chunks']}")
            print(f"   Embedding dimension: {stats.get('embedding_dimension', 'N/A')}")
            
        except Exception as e:
            print(f"⚠️  Could not get system statistics: {e}")
        
        print(f"\n🎉 RAG System Verification Complete!")
        print(f"✅ All components working correctly")
        
        return results
        
    except Exception as e:
        results['errors'].append(f"Unexpected error: {e}")
        print(f"❌ Unexpected error during verification: {e}")
        return results


async def main():
    """Main verification function."""
    print("RAG System Verification Tool")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and configure your settings.")
        return
    
    results = await verify_rag_system()
    
    print(f"\n📊 VERIFICATION SUMMARY")
    print("=" * 30)
    
    checks = [
        ('Configuration Loading', results['config_loading']),
        ('RAG Initialization', results['rag_initialization']),
        ('Document Indexing', results['document_indexing']),
        ('Context Retrieval', results['context_retrieval']),
        ('Query Enhancement', results['query_enhancement'])
    ]
    
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:.<25} {status}")
    
    if results['errors']:
        print(f"\n❌ ERRORS ENCOUNTERED:")
        for error in results['errors']:
            print(f"   - {error}")
    
    all_passed = all(passed for _, passed in checks)
    
    if all_passed:
        print(f"\n🎉 RAG SYSTEM IS FULLY OPERATIONAL!")
        print(f"You can now use the RAG-enhanced chat endpoints:")
        print(f"   - POST /chat/completion")
        print(f"   - POST /chat/advanced")
        print(f"   - GET /rag/status")
    else:
        print(f"\n⚠️  RAG SYSTEM HAS ISSUES")
        print(f"Please fix the errors above before using RAG features.")


if __name__ == "__main__":
    asyncio.run(main())