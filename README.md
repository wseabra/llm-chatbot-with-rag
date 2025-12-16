# FastAPI RAG Chat Application

A simplified, production-ready FastAPI application with Retrieval-Augmented Generation (RAG) capabilities, featuring a modern React frontend and unified chat endpoint.

## 🚀 Features

- **Unified Chat Endpoint**: Single endpoint handles both regular chat and file uploads
- **RAG-Enhanced Conversations**: Automatic context injection from documents
- **Modern React UI**: Clean, responsive chat interface with real-time conversations
- **Document Upload**: Support for `.txt`, `.md`, and `.pdf` files with real-time processing
- **Simplified Architecture**: Streamlined API with only essential endpoints
- **Production Ready**: Comprehensive error handling and graceful degradation
- **Real Embeddings**: Sentence Transformers with ChromaDB vector storage

## 📁 Project Structure

```
├── src/                    # FastAPI Backend
│   ├── api/               # API routes and dependencies
│   │   ├── routes/        # Simplified routes (health, chat)
│   │   ├── app.py         # Main application
│   │   └── ...            # Dependencies and utilities
│   ├── rag/               # RAG system (embeddings, vector store, documents)
│   ├── config/            # Configuration management
│   └── flowApi/           # External API client
├── chatbot-ui/            # React Frontend
│   ├── src/components/    # Chat components
│   ├── src/services/      # Unified API integration
│   └── src/types/         # TypeScript definitions
├── tests/                 # Comprehensive test suite
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

### Simplified API Surface
- **`GET /health`** - Health check with external API status
- **`POST /chat`** - Unified chat endpoint (supports both regular chat and file uploads)
- **`GET /docs`** - Interactive API documentation

### Usage Examples

#### Regular Chat
```bash
curl -X POST "http://localhost:8000/chat" \
  -F 'messages=[{"role":"user","content":"Hello, how are you?"}]' \
  -F 'max_tokens=4096' \
  -F 'temperature=0.7'
```

#### Chat with File Upload
```bash
curl -X POST "http://localhost:8000/chat" \
  -F 'messages=[{"role":"user","content":"Summarize this document"}]' \
  -F 'files=@document.pdf' \
  -F 'max_tokens=4096' \
  -F 'temperature=0.7'
```

#### Health Check
```bash
curl http://localhost:8000/health
```

## 🎨 Frontend Features

- **Unified Interface**: Single service handles all chat interactions
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
# Run all tests
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
```

### Manual API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST "http://localhost:8000/chat" \
  -F 'messages=[{"role":"user","content":"Test message"}]'
```

## 📊 RAG System

### How It Works
1. **Document Processing**: Supports `.txt`, `.md`, and `.pdf` files
2. **Real-time Upload**: Process documents instantly via unified chat endpoint
3. **Vector Embeddings**: Sentence Transformers with ChromaDB storage
4. **Context Enhancement**: Automatic query enhancement with relevant context
5. **Transparent Integration**: Users see enhanced responses without technical complexity

### Features
- **Unified Processing**: Same endpoint handles both pre-indexed and uploaded documents
- **Automatic Enhancement**: RAG context automatically added to user messages
- **Graceful Fallback**: Works even when RAG is unavailable
- **File Validation**: Supports `.txt`, `.md`, `.pdf` with 10MB size limit

## 🔧 Development

### Technology Stack

**Backend:**
- FastAPI, Uvicorn
- Sentence Transformers, ChromaDB
- LangChain, PyPDF
- Simplified route structure

**Frontend:**
- React 19.2.0, TypeScript
- Vite, Vitest
- Unified API service
- CSS Variables for theming

### Architecture Benefits
- **Simplified API**: Only 2 essential endpoints
- **Unified Interface**: Single chat endpoint for all use cases
- **Clean Architecture**: SOLID principles with streamlined design
- **Better Performance**: Fewer route evaluations and consolidated processing
- **Easier Testing**: Simplified test scenarios and debugging

## 📈 Performance & Quality

- **Minimal API Surface**: Only essential endpoints maintained
- **Unified Request Handling**: Single endpoint for all chat scenarios
- **Efficient Processing**: Consolidated middleware and dependency injection
- **Memory Management**: Configurable batch sizes and automatic cleanup
- **File Upload Optimization**: Streaming upload with size validation
- **Response Optimization**: Efficient context retrieval and injection

## 🚨 Troubleshooting

### Common Issues
```bash
# Check if API is running
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST "http://localhost:8000/chat" \
  -F 'messages=[{"role":"user","content":"Test"}]'

# Check logs
python src/main.py
```

### RAG Issues
```bash
# Verify RAG folder exists
ls -la ./rag/

# Check file permissions
chmod -R 755 ./rag/

# Validate document formats
file ./rag/*
```

### Frontend Issues
```bash
# Check backend connectivity
curl http://localhost:8000/health

# Restart development server
cd chatbot-ui && npm run dev
```

## 📚 Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **React UI**: http://localhost:5173
- **Simplified Endpoints**: Only `/health` and `/chat` endpoints
- **Examples**: Usage examples in `examples/`

## 🎯 Architecture Overview

### Simplified Design
- **Endpoints**: Only 2 essential endpoints (`/health`, `/chat`)
- **Route Files**: Minimal structure with health and chat modules
- **Unified Logic**: Single endpoint handles all chat scenarios
- **Clean Separation**: Clear distinction between health monitoring and chat functionality

### Key Benefits
- ✅ All RAG capabilities preserved
- ✅ File upload support maintained
- ✅ Health monitoring kept
- ✅ Error handling preserved
- ✅ Authentication flow unchanged
- ✅ Simplified maintenance and testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `python -m pytest && cd chatbot-ui && npm test`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.