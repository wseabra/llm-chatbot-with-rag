# LLM Chatbot with RAG

A sophisticated chatbot application built with FastAPI that integrates Large Language Models (LLM) with Retrieval-Augmented Generation (RAG) capabilities using CI&T Flow API.

## 🚀 Features

- **FastAPI Backend**: High-performance web framework for building APIs
- **API Client Module**: Robust HTTP client for external service communication
- **Configuration Management**: Environment-based configuration using python-dotenv
- **RAG Integration**: Retrieval-Augmented Generation for enhanced responses
- **Comprehensive Testing**: Full test coverage with pytest (74 tests)
- **Clean Architecture**: Following SOLID principles and best practices
- **Type Safety**: Full type annotations throughout the codebase
- **Error Handling**: Comprehensive exception hierarchy for robust error management

## 📁 Project Structure

```
llm-chatbot-with-rag/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py           # Configuration management module
│   └── api/
│       ├── __init__.py
│       ├── client.py           # HTTP API client
│       ├── models.py           # Response/request models
│       ├── exceptions.py       # Custom API exceptions
│       └── README.md           # API module documentation
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration and fixtures
│   ├── test_config.py         # Configuration module tests (31 tests)
│   └── test_api.py            # API module tests (43 tests)
├── examples/
│   └── api_usage.py           # API usage examples
├── .env                       # Environment variables (create from .env.example)
├── requirements.txt           # Python dependencies
├── pytest.ini               # Pytest configuration
└── README.md                 # This file
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd llm-chatbot-with-rag
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root with the following variables:
   ```env
   CLIENT_ID=your_client_id_here
   CLIENT_SECRET=your_client_secret_here
   RAG_FOLDER=/path/to/your/rag/documents
   ```

## 🏃‍♂️ Running the Application

### Development Server
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Usage Examples
```bash
# Run the API usage examples
python examples/api_usage.py
```

## 🌐 API Client Module

The project includes a robust API client for communicating with external services:

### Quick Start
```python
from api import APIClient

# Basic health check
with APIClient() as client:
    health = client.health_check()
    print(f"API Status: {'healthy' if health.result else 'unhealthy'}")
```

### Error Handling
```python
from api import APIClient, APIConnectionError, APITimeoutError, APIHTTPError

try:
    with APIClient() as client:
        health = client.health_check()
        print(f"Timestamp: {health.timestamp}")
except APIConnectionError:
    print("Network connectivity issue")
except APITimeoutError:
    print("Request timed out")
except APIHTTPError as e:
    print(f"HTTP error {e.status_code}: {e.message}")
```

### Configuration
```python
# Custom configuration
client = APIClient(
    base_url="https://flow.ciandt.com",
    timeout=60  # seconds
)
```

### Available Endpoints
- **Health Check**: `GET /ai-orchestration-api/v1/health`
  - Returns: `{"result": true, "timestamp": "2025-12-11T15:01:23.000Z"}`

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Run only configuration tests
pytest tests/test_config.py

# Run only API tests
pytest tests/test_api.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src
```

### Test Coverage
The project includes comprehensive test coverage for:

#### Configuration Module (31 tests)
- ✅ Environment variable loading and validation
- ✅ Error handling and edge cases
- ✅ Unicode and special character support
- ✅ Integration workflows

#### API Module (43 tests)
- ✅ HTTP client functionality
- ✅ Response model validation
- ✅ Error handling scenarios
- ✅ Connection and timeout management
- ✅ Context manager support
- ✅ URL construction and normalization

**Total: 74 tests with comprehensive coverage**

## 📋 Configuration

The application uses a robust configuration system that loads settings from environment variables:

### Configuration Module (`src/config/`)

```python
from config import Config

# Load configuration from .env file
config = Config()
settings = config.load_config()

# Access configuration values
client_id = settings['CLIENT_ID']
client_secret = settings['CLIENT_SECRET']
rag_folder = settings['RAG_FOLDER']
```

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CLIENT_ID` | CI&T Flow API client identifier | `your_client_123` |
| `CLIENT_SECRET` | CI&T Flow API client secret | `your_secret_key` |
| `RAG_FOLDER` | Path to RAG documents directory | `/path/to/documents` |

### Configuration Features

- **Environment Variable Loading**: Uses python-dotenv for .env file support
- **Validation**: Ensures all required variables are present and non-empty
- **Error Handling**: Descriptive error messages for missing/invalid configuration
- **Immutability**: Returns configuration copies to prevent external modification
- **Testing Support**: Configurable for unit testing scenarios

## 🏗️ Architecture

The project follows clean architecture principles with modular design:

### Modules

#### API Module (`src/api/`)
- **APIClient**: HTTP client with connection pooling and error handling
- **Response Models**: Type-safe data models with validation
- **Exception Hierarchy**: Comprehensive error handling system
- **Context Manager**: Automatic resource cleanup

#### Configuration Module (`src/config/`)
- **Environment Management**: Secure configuration loading
- **Validation**: Input validation and error reporting
- **Flexibility**: Support for different environments

### Design Patterns
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **KISS**: Keep It Simple, Stupid
- **DRY**: Don't Repeat Yourself
- **YAGNI**: You Aren't Gonna Need It
- **Separation of Concerns**: Clear module boundaries and responsibilities

### Code Quality
- **Type Hints**: Full type annotation support
- **Comprehensive Testing**: Unit tests with fixtures and parametrization
- **Error Handling**: Proper exception handling with descriptive messages
- **Documentation**: Inline documentation and comprehensive README files

## 🔧 Development

### Adding New API Endpoints

1. **Create Response Model** (if needed):
```python
# In src/api/models.py
@dataclass
class NewEndpointResponse:
    field1: str
    field2: int
    
    @classmethod
    def from_dict(cls, data: dict) -> 'NewEndpointResponse':
        # Validation logic
        return cls(field1=data['field1'], field2=data['field2'])
```

2. **Add Client Method**:
```python
# In src/api/client.py
def new_endpoint(self, param: str) -> NewEndpointResponse:
    """Call the new endpoint."""
    endpoint = f'/api/v1/new-endpoint/{param}'
    response = self._make_request('GET', endpoint)
    response_data = response.json()
    return NewEndpointResponse.from_dict(response_data)
```

3. **Add Tests**: Create comprehensive tests following existing patterns

### Code Style Guidelines
- Follow PEP 8 guidelines
- Use type hints for all functions and methods
- Write descriptive docstrings
- Maintain test coverage above 90%
- Handle errors gracefully with specific exceptions

### Testing Guidelines
- Write tests before implementing features (TDD)
- Use descriptive test names
- Include both positive and negative test cases
- Test edge cases and error scenarios
- Use fixtures for test data setup
- Mock external dependencies appropriately

## 📚 Dependencies

### Core Dependencies
- **FastAPI**: Modern web framework for building APIs
- **uvicorn**: ASGI server for FastAPI applications
- **python-dotenv**: Environment variable management
- **requests**: HTTP client library for API communication

### Development Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support
- **httpx**: HTTP client for testing FastAPI endpoints

## 🔒 Error Handling

The project implements comprehensive error handling:

### API Module Exceptions
```python
APIError (base)
├── APIConnectionError (network issues)
├── APITimeoutError (request timeouts)
├── APIHTTPError (HTTP 4xx/5xx errors)
└── APIResponseError (invalid response format)
```

### Configuration Exceptions
- **EnvironmentError**: Missing environment variables
- **ValueError**: Invalid or empty configuration values

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Implement feature following existing patterns
4. Add comprehensive tests
5. Ensure all tests pass: `pytest`
6. Update documentation
7. Submit a pull request

### Contribution Guidelines
- Follow existing code style and architecture patterns
- Add tests for all new functionality
- Update documentation for any API changes
- Ensure backward compatibility when possible
- Write clear commit messages

## 🆘 Support

For questions or issues:
1. Check the existing issues in the repository
2. Review the module-specific README files in `src/api/README.md`
3. Run the examples in `examples/` directory
4. Create a new issue with detailed description
5. Include steps to reproduce any bugs
6. Provide relevant logs and error messages

## 🔮 Roadmap

### Completed ✅
- [x] FastAPI application foundation
- [x] Configuration management system
- [x] API client module with health check endpoint
- [x] Comprehensive testing suite (74 tests)
- [x] Error handling and validation
- [x] Type safety and documentation

### In Progress 🚧
- [ ] LLM integration with CI&T Flow API
- [ ] RAG document processing and indexing
- [ ] Chat interface implementation

### Future Enhancements 🔮
- [ ] Authentication and authorization
- [ ] Rate limiting and caching
- [ ] Monitoring and logging
- [ ] Docker containerization
- [ ] CI/CD pipeline setup

## 📊 Project Statistics

- **Total Lines of Code**: ~2,000+
- **Test Coverage**: 74 comprehensive tests
- **Modules**: 2 main modules (config, api)
- **Dependencies**: 6 core + development dependencies
- **Documentation**: 4 README files + inline documentation
- **Architecture**: Clean Architecture with SOLID principles