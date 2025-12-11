# LLM Chatbot with RAG

A sophisticated chatbot application built with FastAPI that integrates Large Language Models (LLM) with Retrieval-Augmented Generation (RAG) capabilities using CI&T Flow API.

## 🚀 Features

- **FastAPI Backend**: High-performance web framework for building APIs
- **Configuration Management**: Environment-based configuration using python-dotenv
- **RAG Integration**: Retrieval-Augmented Generation for enhanced responses
- **Comprehensive Testing**: Full test coverage with pytest
- **Clean Architecture**: Following SOLID principles and best practices

## 📁 Project Structure

```
llm-chatbot-with-rag/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   └── config/
│       ├── __init__.py
│       └── config.py           # Configuration management module
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration and fixtures
│   └── test_config.py         # Configuration module tests
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

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Run only configuration tests
pytest tests/test_config.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src
```

### Test Coverage
The project includes comprehensive test coverage for:
- ✅ Configuration management (31 tests)
- ✅ Environment variable loading and validation
- ✅ Error handling and edge cases
- ✅ Unicode and special character support
- ✅ Integration workflows

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

The project follows clean architecture principles:

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
- **Documentation**: Inline documentation and docstrings

## 🔧 Development

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement feature following existing patterns
3. Add comprehensive tests
4. Update documentation
5. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions and methods
- Write descriptive docstrings
- Maintain test coverage above 90%

### Testing Guidelines
- Write tests before implementing features (TDD)
- Use descriptive test names
- Include both positive and negative test cases
- Test edge cases and error scenarios
- Use fixtures for test data setup

## 📚 Dependencies

### Core Dependencies
- **FastAPI**: Modern web framework for building APIs
- **uvicorn**: ASGI server for FastAPI applications
- **python-dotenv**: Environment variable management

### Development Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support
- **httpx**: HTTP client for testing FastAPI endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 🆘 Support

For questions or issues:
1. Check the existing issues in the repository
2. Create a new issue with detailed description
3. Include steps to reproduce any bugs
4. Provide relevant logs and error messages

## 🔮 Roadmap

- [ ] LLM integration with CI&T Flow API
- [ ] RAG document processing and indexing
- [ ] Chat interface implementation