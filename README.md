# Simple Chat Application with Pluggable LLM Providers

A production-ready FastAPI application with **hotswappable LLM providers** and Retrieval-Augmented Generation (RAG) capabilities, featuring a modern React frontend and dead-simple provider switching.

## 🎯 Key Features

- **🔄 Hotswappable LLM Providers**: Switch between CI&T Flow, or your own provider implementation
- **🚀 Dead Simple**: Edit `src/llm_providers/provider_config.py` to change providers - that's it!
- **📚 RAG-Enhanced Conversations**: Automatic context injection from documents
- **📁 Document Upload**: Support for `.txt`, `.md`, and `.pdf` files with real-time processing
- **🎨 Modern React UI**: Clean, responsive chat interface with real-time conversations
- **🧪 Production Ready**: Comprehensive error handling, testing, and graceful degradation
- **🔧 Easy Extension**: Add your own LLM provider by implementing just 2 methods

## 🔄 LLM Provider System

### Switch Providers in Seconds

**Edit ONE file to switch providers:**

```python
# src/llm_providers/provider_config.py
def get_llm_provider():
    # return FlowProvider()        # CI&T Flow (default)
    return OpenAIProvider()      # OpenAI
```

**Set your API key:**
```bash
export OPENAPIKEY=your_key_here
```

**That's it!** Your entire application now uses OpenAPI

### Add Your Own Provider

**Implement ONE class with TWO methods:**

```python
# src/llm_providers/my_provider.py
from .base import LLMProvider, LLMRequest, LLMResponse

class MyProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def chat_completion(self, request: LLMRequest) -> LLMResponse:
        # Your implementation here
        pass
    
    async def health_check(self) -> bool:
        # Your health check here
        return True
```

**Use your provider:**
```python
# src/llm_providers/provider_config.py
def get_llm_provider():
    return MyProvider(api_key="your_key")
```

**Done!** Your custom provider is now live.

### Supported Providers

- ✅ **CI&T Flow** (default) - Production ready
- ✅ **OpenAI** (example) - GPT-3.5, GPT-4
- ✅ **Your Custom Provider** - Easy to add!

## 📁 Project Structure

```
├── src/
│   ├── llm_providers/         # 🔥 Hotswappable LLM Provider System
│   │   ├── provider_config.py # ← Edit this file to switch providers
│   │   ├── base.py            # Simple 2-method interface
│   │   ├── flow_provider.py   # CI&T Flow (default)
│   │   └── openai_provider.py # OpenAI example
│   ├── api/                   # FastAPI Backend
│   │   ├── routes/chat.py     # Unified chat + health endpoint
│   │   └── app.py             # Main FastAPI application
│   ├── rag/                   # RAG system (embeddings, vector store)
│   ├── config/                # Configuration management
│   └── flowApi/               # Flow API client
├── chatbot-ui/                # React Frontend
│   ├── src/components/        # Chat components
│   ├── src/services/          # API integration
│   └── src/types/             # TypeScript definitions
├── tests/                     # Comprehensive test suite (324 tests ✅)
└── run.py                     # Application entrypoint
```

## ⚡ Quick Start

### 1. Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment (CI&T Flow - works out of the box)
cp .env.example .env
# Edit .env with your CI&T Flow credentials

# Add documents (optional)
mkdir rag
# Add your .txt, .md, or .pdf files

# Start backend
python run.py
# API available at http://localhost:8000
```

### 2. Frontend Setup

```bash
# Navigate to UI directory
cd chatbot-ui

# Install dependencies
npm install

# Start development server
npm run dev
# UI available at http://localhost:5173
```

### 3. Switch Providers (Optional)

```bash
# To use OpenAI instead:
# 1. Edit src/llm_providers/provider_config.py
# 2. Change: return FlowProvider() → return OpenAIProvider()
# 3. Set: export OPENAI_API_KEY=sk-your_key
# 4. Restart: python run.py

# To use Anthropic:
# 1. Change: return AnthropicProvider()
# 2. Set: export ANTHROPIC_API_KEY=your_key
# 3. Restart: python run.py
```

## 🔗 API Endpoints

### Ultra-Simple API
- **`GET /health`** - Health check (includes LLM provider status)
- **`POST /chat`** - Unified chat endpoint (works with ANY provider)

### Usage Examples

#### Regular Chat (Works with ANY Provider)
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
  -F 'max_tokens=4096'
```

#### Health Check (Shows Current Provider)
```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy", "llm_provider_healthy": true}
```

## 🎨 Frontend Features

- **Provider Agnostic**: Works seamlessly with any LLM provider
- **Real-time Chat**: Multi-turn conversations with loading states
- **File Upload Support**: Drag-and-drop document upload
- **Error Handling**: Graceful error handling with retry functionality
- **Accessibility**: Full keyboard navigation and screen reader support
- **Theme Support**: Automatic dark/light theme switching

## ⚙️ Configuration

### Required Settings (CI&T Flow - Default)
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

### Backend Tests (All 324 Tests Pass ✅)
```bash
# Run all tests
python -m pytest
# ✅ 324 passed in 8.93s

# Test LLM provider system
python -m pytest tests/test_simple_llm_providers.py -v

# Test provider switching demo
python examples/simple_usage.py
```

### Frontend Tests
```bash
cd chatbot-ui

# Run React tests
npm run test

# Run with coverage
npm run test:coverage
```

## 📊 RAG System

### How It Works (Provider Independent)
1. **Document Processing**: Supports `.txt`, `.md`, and `.pdf` files
2. **Real-time Upload**: Process documents instantly via unified chat endpoint
3. **Vector Embeddings**: Sentence Transformers with ChromaDB storage
4. **Context Enhancement**: Automatic query enhancement with relevant context
5. **Provider Agnostic**: Works with ANY LLM provider seamlessly

### Features
- **Universal Compatibility**: RAG works with Flow, or your custom provider
- **Automatic Enhancement**: RAG context automatically added to user messages
- **Graceful Fallback**: Works even when RAG is unavailable
- **File Validation**: Supports `.txt`, `.md`, `.pdf` with 10MB size limit

## 🔧 Development

### Technology Stack

**LLM Provider System:**
- Simple 2-method interface (`chat_completion`, `health_check`)
- Easy extension for any LLM API
- Configuration-driven switching

**Backend:**
- FastAPI, Uvicorn
- Sentence Transformers, ChromaDB
- LangChain, PyPDF
- Provider-agnostic architecture

**Frontend:**
- React 19.2.0, TypeScript
- Vite, Vitest
- Provider-agnostic API service
- CSS Variables for theming

### Architecture Benefits
- **🔄 Hotswappable**: Switch providers without code changes
- **🎯 Simple**: Edit one file to change providers
- **🧪 Testable**: Easy to mock and test any provider
- **🚀 Extensible**: Add new providers in minutes
- **🔒 Reliable**: Comprehensive error handling
- **📈 Scalable**: Clean abstractions for growth

## 🎯 LLM Provider Examples

### CI&T Flow (Default - Production Ready)
```python
# Already configured - just works!
return FlowProvider()
```

### Your Custom Provider
```python
class MyProvider(LLMProvider):
    async def chat_completion(self, request: LLMRequest) -> LLMResponse:
        # Call your API here
        pass
    
    async def health_check(self) -> bool:
        return True

return MyProvider(api_key="your_key")
```

## 🚨 Troubleshooting

### RAG Issues
```bash
# Verify RAG folder exists
ls -la ./rag/

# Check file permissions
chmod -R 755 ./rag/

# Validate document formats
file ./rag/*
```

## 📚 Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **React UI**: http://localhost:5173