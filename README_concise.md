# FastAPI RAG Chat Application

A production-ready FastAPI application with Retrieval-Augmented Generation (RAG) capabilities for enhanced AI chat interactions.

## 🚀 Features

- **RAG-Enhanced Chat**: Automatic context injection from your documents
- **FastAPI Backend**: High-performance API with automatic documentation
- **Real Embeddings**: Sentence Transformers with ChromaDB vector storage
- **Document Support**: `.txt`, `.md`, and `.pdf` files
- **Health Monitoring**: Comprehensive health checks and RAG status
- **Production Ready**: 314 tests, error handling, and graceful degradation

## 📁 Project Structure

```
src/
├── api/                 # FastAPI application
│   ├── routes/         # API endpoints (chat, health)
│   └── rag_dependency.py # RAG dependency injection
├── rag/                # RAG system
│   ├── rag_manager.py  # Main RAG orchestrator
│   ├── vector_store.py # ChromaDB integration
│   ├── embeddings.py   # Sentence Transformers
│   └── document_*.py   # Document processing
├── config/             # Configuration management
└── flowApi/           # External API client
```

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings:
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
RAG_FOLDER=./rag
```

### 3. Add Documents
```bash
mkdir rag
# Add your .txt, .md, or .pdf files to the rag/ folder
```

### 4. Run Application
```bash
python src/main.py
```

The application will automatically:
- Initialize the RAG system
- Index your documents
- Start the API server at http://localhost:8000

## 🔗 API Endpoints

### Core Endpoints
- **`GET /`** - Application info
- **`GET /docs`** - Interactive API documentation
- **`GET /health`** - Health check with external API status
- **`GET /rag/status`** - RAG system status and statistics

### Chat Endpoints (RAG-Enhanced)
- **`POST /chat/completion`** - Simple chat with automatic context injection
- **`POST /chat/advanced`** - Multi-turn chat with RAG enhancement

### Example Chat Request
```bash
curl -X POST "http://localhost:8000/chat/completion" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main features?"}'
```

### Example Response
```json
{
  "content": "Based on your documents, the main features are...",
  "rag_metadata": {
    "rag_enabled": true,
    "sources_used": 2,
    "sources": ["feature_guide.md", "overview.txt"],
    "similarity_scores": [0.85, 0.78]
  }
}
```

## ⚙️ Configuration

### Required Settings
```env
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
RAG_FOLDER=./rag
```

### Optional RAG Settings
```env
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_SIMILARITY_THRESHOLD=0.7
RAG_MAX_CONTEXT_CHUNKS=5
RAG_VECTOR_DB_PATH=./data/chroma_db
```

## 🧪 Testing

```bash
# Run all tests (314 tests)
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Test RAG system
python examples/rag_verification.py
```

## 📊 RAG System

### How It Works
1. **Document Indexing**: Automatically processes documents in `RAG_FOLDER`
2. **Embedding Generation**: Creates vector embeddings using Sentence Transformers
3. **Vector Storage**: Stores embeddings in ChromaDB for fast similarity search
4. **Context Injection**: Automatically enhances chat queries with relevant context
5. **Response Generation**: Sends enhanced queries to external AI service

### Supported File Types
- **Text Files**: `.txt`, `.md`
- **PDF Files**: `.pdf`

### RAG Status Monitoring
```bash
curl http://localhost:8000/rag/status
```

## 🔧 Development

### Project Dependencies
- **FastAPI**: Web framework
- **Sentence Transformers**: Embeddings
- **ChromaDB**: Vector database
- **LangChain**: Document processing
- **Uvicorn**: ASGI server

### Architecture Highlights
- **Clean Architecture**: SOLID principles and separation of concerns
- **Dependency Injection**: Clean FastAPI integration
- **Error Handling**: Comprehensive exception hierarchy
- **Resource Management**: Automatic cleanup and graceful shutdown
- **Graceful Degradation**: Works even when RAG is unavailable

## 📈 Performance

- **314 Tests**: 100% pass rate
- **Real Embeddings**: Production Sentence Transformers
- **Efficient Storage**: ChromaDB vector database
- **Batch Processing**: Optimized for large document sets
- **Memory Management**: Configurable batch sizes and chunking

## 🚨 Troubleshooting

### Common Issues

**RAG not working?**
```bash
# Check RAG status
curl http://localhost:8000/rag/status

# Verify documents exist
ls -la ./rag/

# Check logs for errors
python src/main.py  # Look for RAG initialization messages
```

**No documents indexed?**
- Ensure `RAG_FOLDER` exists and contains supported files
- Check file permissions
- Verify file formats (`.txt`, `.md`, `.pdf`)

**Performance issues?**
- Reduce `RAG_CHUNK_SIZE` for faster processing
- Adjust `RAG_EMBEDDING_BATCH_SIZE` based on available memory
- Use fewer `RAG_MAX_CONTEXT_CHUNKS` for faster responses

## 📚 Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **RAG Examples**: `examples/rag_usage_examples.py`
- **API Examples**: `examples/api_usage.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `python -m pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.