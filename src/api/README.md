# API Module

A robust HTTP client module for external service communication using the `requests` library.

## Overview

This module provides a clean, type-safe interface for making HTTP requests to external APIs with comprehensive error handling, timeout management, and response validation.

## Features

- **Type Safety**: Full type annotations and validated response models
- **Error Handling**: Comprehensive exception hierarchy for different error types
- **Connection Pooling**: Automatic session management for performance
- **Timeout Management**: Configurable request timeouts
- **Response Validation**: Automatic JSON parsing and schema validation
- **Context Manager Support**: Automatic resource cleanup
- **Extensible Design**: Easy to add new endpoints

## Quick Start

```python
from api import APIClient, HealthResponse

# Basic usage
client = APIClient()
health = client.health_check()
print(f"API is {'healthy' if health.result else 'unhealthy'}")
client.close()

# Using context manager (recommended)
with APIClient() as client:
    health = client.health_check()
    print(f"Status: {health}")
```

## Configuration

```python
# Custom configuration
client = APIClient(
    base_url="https://custom.api.com",
    timeout=60  # seconds
)
```

## Error Handling

The module provides specific exceptions for different error scenarios:

```python
from api import (
    APIConnectionError,
    APITimeoutError, 
    APIHTTPError,
    APIResponseError
)

try:
    with APIClient() as client:
        health = client.health_check()
        
except APIConnectionError:
    print("Network connectivity issue")
except APITimeoutError:
    print("Request timed out")
except APIHTTPError as e:
    print(f"HTTP error {e.status_code}: {e.message}")
except APIResponseError:
    print("Invalid response format")
```

## Available Endpoints

### Health Check

**Endpoint**: `GET /ai-orchestration-api/v1/health`

**Response Format**:
```json
{
  "result": true,
  "timestamp": "2025-12-11T15:01:23.000Z"
}
```

**Usage**:
```python
health = client.health_check()
print(f"Result: {health.result}")
print(f"Timestamp: {health.timestamp}")

# Convert to dictionary
health_dict = health.to_dict()
```

## Response Models

### HealthResponse

A type-safe model for health check responses:

```python
@dataclass
class HealthResponse:
    result: bool
    timestamp: str
    
    @classmethod
    def from_dict(cls, data: dict) -> 'HealthResponse'
    
    def to_dict(self) -> dict
```

## Exception Hierarchy

```
APIError (base)
├── APIConnectionError (network issues)
├── APITimeoutError (request timeouts)
├── APIHTTPError (HTTP 4xx/5xx errors)
└── APIResponseError (invalid response format)
```

## Testing

The module includes comprehensive tests covering:

- Unit tests for all components
- Mock HTTP responses
- Error scenario testing
- Parametrized tests for different cases
- Integration tests

Run tests with:
```bash
pytest tests/test_api.py -v
```

## Adding New Endpoints

To add a new endpoint:

1. **Create Response Model** (if needed):
```python
# In models.py
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
# In client.py
def new_endpoint(self, param: str) -> NewEndpointResponse:
    """Call the new endpoint."""
    endpoint = f'/api/v1/new-endpoint/{param}'
    response = self._make_request('GET', endpoint)
    response_data = response.json()
    return NewEndpointResponse.from_dict(response_data)
```

3. **Update Exports**:
```python
# In __init__.py
from .models import NewEndpointResponse

__all__ = [
    # ... existing exports
    'NewEndpointResponse'
]
```

## Best Practices

1. **Always use context managers** for automatic resource cleanup
2. **Handle specific exceptions** rather than catching all exceptions
3. **Validate response data** using the provided models
4. **Set appropriate timeouts** for your use case
5. **Log errors appropriately** for debugging

## Dependencies

- `requests>=2.31.0`: HTTP client library
- `typing`: Type annotations (built-in)
- `dataclasses`: Response models (built-in)
- `urllib.parse`: URL handling (built-in)

## Architecture

The module follows Clean Architecture principles:

- **Separation of Concerns**: Clear separation between client, models, and exceptions
- **Dependency Inversion**: Abstract interfaces for easy testing
- **Single Responsibility**: Each class has a single, well-defined purpose
- **Open/Closed Principle**: Easy to extend with new endpoints without modifying existing code