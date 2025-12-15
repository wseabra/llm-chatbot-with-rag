# FastAPI RAG Chat Application

A production-ready FastAPI application with Retrieval-Augmented Generation (RAG) capabilities, featuring a modern React frontend and comprehensive testing suite.

## 🚀 Features

- **RAG-Enhanced Chat**: Automatic context injection from documents
- **Modern React UI**: Clean, responsive chat interface with real-time conversations
- **Document Upload**: Support for `.txt`, `.md`, and `.pdf` files with real-time processing
- **FastAPI Backend**: High-performance API with automatic documentation
- **Production Ready**: 265+ tests, comprehensive error handling, and graceful degradation
- **Real Embeddings**: Sentence Transformers with ChromaDB vector storage
- **Postman Collection**: Complete API testing suite with automated scenarios

## 📁 Project Structure

```
├── src/                    # FastAPI Backend
│   ├── api/               # API routes and dependencies
│   ├── rag/               # RAG system (embeddings, vector store, documents)
│   ├── config/            # Configuration management
│   └── flowApi/           # External API client
├── chatbot-ui/            # React Frontend
│   ├── src/components/    # Chat components
│   ├── src/services/      # API integration
│   └── src/types/         # TypeScript definitions
├── tests/                 # Comprehensive test suite (265+ tests)
├── postman/               # API testing collection
└── examples/              # Usage examples and verification scripts
```

## ⚡ Quick Start

### Backend Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your CI&T Flow credentials

# 3. Add documents (optional)
mkdir rag
# Add your .txt, .md, or .pdf files

# 4. Start backend
python src/main.py
# API available at http://localhost:8000
```

### Frontend Setup

```bash
# 1. Navigate to UI directory
cd chatbot-ui

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
# UI available at http://localhost:5173
```

## 🔗 API Endpoints

### Core Endpoints
- **`GET /`** - Application info
- **`GET /docs`** - Interactive API documentation
- **`GET /health`** - Health check with external API status
- **`GET /rag/status`** - RAG system status and statistics

### Chat Endpoints
- **`POST /chat/completion`** - Simple chat with RAG enhancement
- **`POST /chat/advanced`** - Multi-turn conversations with full context
- **`POST /chat/uploaded`** - Chat with document uploads (real-time processing)

### Example Usage

```bash
# Simple chat
curl -X POST "http://localhost:8000/chat/completion" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main features?"}'

# Chat with file upload
curl -X POST "http://localhost:8000/chat/uploaded" \
  -F 'messages=[{"role":"user","content":"Summarize this document"}]' \
  -F 'files=@document.pdf'
```

## 🎨 Frontend Features

- **Modern React Interface**: Clean, responsive design with TypeScript
- **Real-time Chat**: Multi-turn conversations with loading states
- **File Upload Support**: Drag-and-drop document upload with instant processing
- **Error Handling**: Graceful error handling with retry functionality
- **Accessibility**: Full keyboard navigation and screen reader support
- **Theme Support**: Automatic dark/light theme switching

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

### Backend Tests
```bash
# Run all 265+ tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Test RAG system
python examples/rag_verification.py
```

### Frontend Tests
```bash
cd chatbot-ui

# Run React tests
npm run test

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui
```

### API Testing with Postman
```bash
# Import collection from postman/ directory
# Or run with Newman CLI
newman run postman/FastAPI_RAG_Application.postman_collection.json \
  -e postman/FastAPI_RAG_Environment.postman_environment.json
```

## 📊 RAG System

### How It Works
1. **Document Processing**: Supports `.txt`, `.md`, and `.pdf` files
2. **Real-time Upload**: Process documents instantly via API
3. **Vector Embeddings**: Sentence Transformers with ChromaDB storage
4. **Context Enhancement**: Automatic query enhancement with relevant context
5. **Transparent Integration**: Users see enhanced responses without technical complexity

### RAG Status Monitoring
```bash
curl http://localhost:8000/rag/status
```

## 🔧 Development

### Technology Stack

**Backend:**
- FastAPI, Uvicorn
- Sentence Transformers, ChromaDB
- LangChain, PyPDF
- Comprehensive pytest suite

**Frontend:**
- React 19.2.0, TypeScript
- Vite, Vitest
- React Testing Library
- CSS Variables for theming

### Architecture Highlights
- **Clean Architecture**: SOLID principles and separation of concerns
- **Dependency Injection**: Clean FastAPI integration with optional RAG
- **Error Handling**: Comprehensive exception hierarchy
- **Resource Management**: Automatic cleanup and graceful shutdown
- **Graceful Degradation**: Works even when RAG is unavailable

## 📈 Performance & Quality

- **265+ Tests**: Comprehensive backend and frontend test coverage
- **Real Embeddings**: Production-grade Sentence Transformers
- **Efficient Storage**: ChromaDB vector database with batch processing
- **Memory Management**: Configurable batch sizes and chunking
- **File Upload Limits**: 10MB per file with validation
- **Response Optimization**: Efficient context retrieval and injection

## 🚨 Troubleshooting

### RAG Issues
```bash
# Check RAG status
curl http://localhost:8000/rag/status

# Verify documents
ls -la ./rag/

# Check logs
python src/main.py
```

### Frontend Issues
```bash
# Check backend connectivity
curl http://localhost:8000/health

# Restart development server
cd chatbot-ui && npm run dev
```

### Common Solutions
- Ensure backend is running on port 8000
- Verify `.env` configuration with valid credentials
- Check file permissions for RAG folder
- Validate document formats (`.txt`, `.md`, `.pdf`)

## 📚 Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **React UI**: http://localhost:5173
- **Postman Collection**: Complete API testing suite in `postman/`
- **Examples**: Usage examples in `examples/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `python -m pytest && cd chatbot-ui && npm test`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.