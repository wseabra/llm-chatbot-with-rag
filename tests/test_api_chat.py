"""
Tests for chat completion functionality in the API client.

This module provides comprehensive tests for the chat completion models and methods,
ensuring proper validation, serialization, and API interaction.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from requests import Response

from src.api import (
    APIClient, ChatMessage, ChatCompletionRequest, ChatCompletionResponse,
    ChatCompletionChoice, ChatCompletionUsage, APIResponseError,
    APIAuthenticationError, APIConnectionError
)


class TestChatMessage:
    """Test cases for ChatMessage model."""
    
    def test_chat_message_creation_valid(self):
        """Test creating a valid ChatMessage."""
        message = ChatMessage(role="user", content="Hello, world!")
        assert message.role == "user"
        assert message.content == "Hello, world!"
    
    def test_chat_message_role_normalization(self):
        """Test that role is normalized to lowercase."""
        message = ChatMessage(role="USER", content="Hello")
        assert message.role == "user"
        
        message = ChatMessage(role="Assistant", content="Hi there")
        assert message.role == "assistant"
    
    def test_chat_message_whitespace_stripping(self):
        """Test that whitespace is stripped from fields."""
        message = ChatMessage(role="  user  ", content="  Hello, world!  ")
        assert message.role == "user"
        assert message.content == "Hello, world!"
    
    def test_chat_message_invalid_role(self):
        """Test that invalid roles raise ValueError."""
        with pytest.raises(ValueError, match="role must be one of"):
            ChatMessage(role="invalid", content="Hello")
    
    def test_chat_message_empty_role(self):
        """Test that empty role raises ValueError."""
        with pytest.raises(ValueError, match="role cannot be empty"):
            ChatMessage(role="", content="Hello")
        
        with pytest.raises(ValueError, match="role cannot be empty"):
            ChatMessage(role="   ", content="Hello")
    
    def test_chat_message_empty_content(self):
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            ChatMessage(role="user", content="")
        
        with pytest.raises(ValueError, match="content cannot be empty"):
            ChatMessage(role="user", content="   ")
    
    def test_chat_message_to_dict(self):
        """Test ChatMessage serialization to dictionary."""
        message = ChatMessage(role="user", content="Hello, world!")
        expected = {"role": "user", "content": "Hello, world!"}
        assert message.to_dict() == expected
    
    def test_chat_message_from_dict_valid(self):
        """Test ChatMessage deserialization from valid dictionary."""
        data = {"role": "assistant", "content": "Hi there!"}
        message = ChatMessage.from_dict(data)
        assert message.role == "assistant"
        assert message.content == "Hi there!"
    
    def test_chat_message_from_dict_invalid_format(self):
        """Test ChatMessage deserialization from invalid format."""
        with pytest.raises(APIResponseError, match="Invalid message format"):
            ChatMessage.from_dict("not a dict")
    
    def test_chat_message_from_dict_missing_fields(self):
        """Test ChatMessage deserialization with missing fields."""
        with pytest.raises(APIResponseError, match="Missing required fields"):
            ChatMessage.from_dict({"role": "user"})
        
        with pytest.raises(APIResponseError, match="Missing required fields"):
            ChatMessage.from_dict({"content": "Hello"})
    
    def test_chat_message_from_dict_invalid_data(self):
        """Test ChatMessage deserialization with invalid data."""
        with pytest.raises(APIResponseError, match="Invalid message data"):
            ChatMessage.from_dict({"role": "invalid", "content": "Hello"})
    
    def test_chat_message_str_representation(self):
        """Test string representation of ChatMessage."""
        message = ChatMessage(role="user", content="Hello, world!")
        str_repr = str(message)
        assert "user" in str_repr
        assert "Hello, world!" in str_repr
        
        # Test truncation for long content
        long_content = "A" * 100
        message = ChatMessage(role="user", content=long_content)
        str_repr = str(message)
        assert "..." in str_repr
        assert len(str_repr) < len(long_content) + 50


class TestChatCompletionUsage:
    """Test cases for ChatCompletionUsage model."""
    
    def test_usage_creation_valid(self):
        """Test creating a valid ChatCompletionUsage."""
        usage = ChatCompletionUsage(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 20
        assert usage.total_tokens == 30
    
    def test_usage_invalid_token_counts(self):
        """Test that negative token counts raise ValueError."""
        with pytest.raises(ValueError, match="prompt_tokens must be a non-negative integer"):
            ChatCompletionUsage(prompt_tokens=-1, completion_tokens=20, total_tokens=19)
        
        with pytest.raises(ValueError, match="completion_tokens must be a non-negative integer"):
            ChatCompletionUsage(prompt_tokens=10, completion_tokens=-1, total_tokens=9)
        
        with pytest.raises(ValueError, match="total_tokens must be a non-negative integer"):
            ChatCompletionUsage(prompt_tokens=10, completion_tokens=20, total_tokens=-1)
    
    def test_usage_invalid_total(self):
        """Test that incorrect total raises ValueError."""
        with pytest.raises(ValueError, match="total_tokens .* must equal"):
            ChatCompletionUsage(prompt_tokens=10, completion_tokens=20, total_tokens=25)
    
    def test_usage_to_dict(self):
        """Test ChatCompletionUsage serialization to dictionary."""
        usage = ChatCompletionUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        expected = {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
        assert usage.to_dict() == expected
    
    def test_usage_from_dict_valid(self):
        """Test ChatCompletionUsage deserialization from valid dictionary."""
        data = {"prompt_tokens": 15, "completion_tokens": 25, "total_tokens": 40}
        usage = ChatCompletionUsage.from_dict(data)
        assert usage.prompt_tokens == 15
        assert usage.completion_tokens == 25
        assert usage.total_tokens == 40
    
    def test_usage_from_dict_invalid_format(self):
        """Test ChatCompletionUsage deserialization from invalid format."""
        with pytest.raises(APIResponseError, match="Invalid usage format"):
            ChatCompletionUsage.from_dict("not a dict")
    
    def test_usage_from_dict_missing_fields(self):
        """Test ChatCompletionUsage deserialization with missing fields."""
        with pytest.raises(APIResponseError, match="Missing required fields"):
            ChatCompletionUsage.from_dict({"prompt_tokens": 10, "completion_tokens": 20})


class TestChatCompletionChoice:
    """Test cases for ChatCompletionChoice model."""
    
    def test_choice_creation_valid(self):
        """Test creating a valid ChatCompletionChoice."""
        message = ChatMessage(role="assistant", content="Hello!")
        choice = ChatCompletionChoice(
            index=0,
            message=message,
            finish_reason="stop"
        )
        assert choice.index == 0
        assert choice.message == message
        assert choice.finish_reason == "stop"
    
    def test_choice_invalid_index(self):
        """Test that negative index raises ValueError."""
        message = ChatMessage(role="assistant", content="Hello!")
        with pytest.raises(ValueError, match="index must be a non-negative integer"):
            ChatCompletionChoice(index=-1, message=message, finish_reason="stop")
    
    def test_choice_invalid_message(self):
        """Test that non-ChatMessage raises ValueError."""
        with pytest.raises(ValueError, match="message must be a ChatMessage instance"):
            ChatCompletionChoice(index=0, message="not a message", finish_reason="stop")
    
    def test_choice_empty_finish_reason(self):
        """Test that empty finish_reason raises ValueError."""
        message = ChatMessage(role="assistant", content="Hello!")
        with pytest.raises(ValueError, match="finish_reason cannot be empty"):
            ChatCompletionChoice(index=0, message=message, finish_reason="")
    
    def test_choice_to_dict(self):
        """Test ChatCompletionChoice serialization to dictionary."""
        message = ChatMessage(role="assistant", content="Hello!")
        choice = ChatCompletionChoice(index=0, message=message, finish_reason="stop")
        expected = {
            "index": 0,
            "message": {"role": "assistant", "content": "Hello!"},
            "finish_reason": "stop"
        }
        assert choice.to_dict() == expected
    
    def test_choice_from_dict_valid(self):
        """Test ChatCompletionChoice deserialization from valid dictionary."""
        data = {
            "index": 0,
            "message": {"role": "assistant", "content": "Hello!"},
            "finish_reason": "stop"
        }
        choice = ChatCompletionChoice.from_dict(data)
        assert choice.index == 0
        assert choice.message.role == "assistant"
        assert choice.message.content == "Hello!"
        assert choice.finish_reason == "stop"


class TestChatCompletionRequest:
    """Test cases for ChatCompletionRequest model."""
    
    def test_request_creation_valid(self):
        """Test creating a valid ChatCompletionRequest."""
        messages = [ChatMessage(role="user", content="Hello!")]
        request = ChatCompletionRequest(messages=messages)
        assert request.messages == messages
        assert request.stream is False
        assert request.max_tokens == 4096
        assert request.temperature == 0.7
        assert request.allowed_models == ["gpt-4o-mini"]
    
    def test_request_creation_with_custom_params(self):
        """Test creating ChatCompletionRequest with custom parameters."""
        messages = [ChatMessage(role="user", content="Hello!")]
        request = ChatCompletionRequest(
            messages=messages,
            stream=True,
            max_tokens=1000,
            temperature=0.5,
            allowed_models=["gpt-4", "gpt-3.5-turbo"]
        )
        assert request.stream is True
        assert request.max_tokens == 1000
        assert request.temperature == 0.5
        assert request.allowed_models == ["gpt-4", "gpt-3.5-turbo"]
    
    def test_request_empty_messages(self):
        """Test that empty messages raises ValueError."""
        with pytest.raises(ValueError, match="messages cannot be empty"):
            ChatCompletionRequest(messages=[])
    
    def test_request_invalid_messages_type(self):
        """Test that non-list messages raises ValueError."""
        with pytest.raises(ValueError, match="messages must be a list"):
            ChatCompletionRequest(messages="not a list")
    
    def test_request_invalid_message_items(self):
        """Test that non-ChatMessage items raise ValueError."""
        with pytest.raises(ValueError, match="must be a ChatMessage instance"):
            ChatCompletionRequest(messages=["not a message"])
    
    def test_request_invalid_max_tokens(self):
        """Test that invalid max_tokens raises ValueError."""
        messages = [ChatMessage(role="user", content="Hello!")]
        with pytest.raises(ValueError, match="max_tokens must be a positive integer"):
            ChatCompletionRequest(messages=messages, max_tokens=0)
        
        with pytest.raises(ValueError, match="max_tokens must be a positive integer"):
            ChatCompletionRequest(messages=messages, max_tokens=-1)
    
    def test_request_invalid_temperature(self):
        """Test that invalid temperature raises ValueError."""
        messages = [ChatMessage(role="user", content="Hello!")]
        with pytest.raises(ValueError, match="temperature must be a number between 0.0 and 2.0"):
            ChatCompletionRequest(messages=messages, temperature=-0.1)
        
        with pytest.raises(ValueError, match="temperature must be a number between 0.0 and 2.0"):
            ChatCompletionRequest(messages=messages, temperature=2.1)
    
    def test_request_to_dict(self):
        """Test ChatCompletionRequest serialization to dictionary."""
        messages = [ChatMessage(role="user", content="Hello!")]
        request = ChatCompletionRequest(messages=messages, max_tokens=1000, temperature=0.5)
        result = request.to_dict()
        
        expected = {
            "messages": [{"role": "user", "content": "Hello!"}],
            "stream": False,
            "max_tokens": 1000,
            "temperature": 0.5,
            "allowedModels": ["gpt-4o-mini"]
        }
        assert result == expected


class TestChatCompletionResponse:
    """Test cases for ChatCompletionResponse model."""
    
    def test_response_creation_valid(self):
        """Test creating a valid ChatCompletionResponse."""
        message = ChatMessage(role="assistant", content="Hello!")
        choice = ChatCompletionChoice(index=0, message=message, finish_reason="stop")
        usage = ChatCompletionUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        
        response = ChatCompletionResponse(
            id="chatcmpl-123",
            object="chat.completion",
            created=1677652288,
            model="gpt-4o-mini",
            choices=[choice],
            usage=usage
        )
        
        assert response.id == "chatcmpl-123"
        assert response.object == "chat.completion"
        assert response.created == 1677652288
        assert response.model == "gpt-4o-mini"
        assert len(response.choices) == 1
        assert response.usage == usage
    
    def test_response_get_first_choice_content(self):
        """Test getting content from first choice."""
        message = ChatMessage(role="assistant", content="Hello, world!")
        choice = ChatCompletionChoice(index=0, message=message, finish_reason="stop")
        usage = ChatCompletionUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        
        response = ChatCompletionResponse(
            id="chatcmpl-123",
            object="chat.completion",
            created=1677652288,
            model="gpt-4o-mini",
            choices=[choice],
            usage=usage
        )
        
        assert response.get_first_choice_content() == "Hello, world!"
    
    
    def test_response_from_dict_valid(self):
        """Test ChatCompletionResponse deserialization from valid dictionary."""
        data = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-4o-mini",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Hello!"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        
        response = ChatCompletionResponse.from_dict(data)
        assert response.id == "chatcmpl-123"
        assert response.model == "gpt-4o-mini"
        assert len(response.choices) == 1
        assert response.choices[0].message.content == "Hello!"
        assert response.usage.total_tokens == 15


class TestAPIClientChatMethods:
    """Test cases for APIClient chat completion methods."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock APIClient for testing."""
        client = APIClient()
        client._auth_response = Mock()
        client._auth_response.is_expired.return_value = False
        client._auth_response.get_authorization_header.return_value = "Bearer test-token"
        return client
    
    def test_chat_completion_simple(self, mock_client):
        """Test simple chat completion method."""
        # Mock the send_chat_request method
        mock_response = Mock(spec=ChatCompletionResponse)
        mock_response.get_first_choice_content.return_value = "Hello there!"
        
        with patch.object(mock_client, 'send_chat_request', return_value=mock_response) as mock_send:
            result = mock_client.chat_completion("Hello, world!")
            
            # Verify send_chat_request was called with correct parameters
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]  # First positional argument
            
            assert isinstance(call_args, ChatCompletionRequest)
            assert len(call_args.messages) == 1
            assert call_args.messages[0].role == "user"
            assert call_args.messages[0].content == "Hello, world!"
            assert call_args.max_tokens == 4096
            assert call_args.temperature == 0.7
            
            assert result == mock_response
    
    def test_chat_completion_with_custom_params(self, mock_client):
        """Test chat completion with custom parameters."""
        mock_response = Mock(spec=ChatCompletionResponse)
        
        with patch.object(mock_client, 'send_chat_request', return_value=mock_response) as mock_send:
            result = mock_client.chat_completion(
                "Explain quantum physics",
                max_tokens=500,
                temperature=0.3
            )
            
            call_args = mock_send.call_args[0][0]
            assert call_args.max_tokens == 500
            assert call_args.temperature == 0.3
            assert call_args.messages[0].content == "Explain quantum physics"
    
    def test_chat_completion_empty_message(self, mock_client):
        """Test chat completion with empty message raises ValueError."""
        with pytest.raises(ValueError, match="user_message cannot be empty"):
            mock_client.chat_completion("")
        
        with pytest.raises(ValueError, match="user_message cannot be empty"):
            mock_client.chat_completion("   ")
    
    def test_chat_completion_whitespace_stripping(self, mock_client):
        """Test that user message whitespace is stripped."""
        mock_response = Mock(spec=ChatCompletionResponse)
        
        with patch.object(mock_client, 'send_chat_request', return_value=mock_response) as mock_send:
            mock_client.chat_completion("  Hello, world!  ")
            
            call_args = mock_send.call_args[0][0]
            assert call_args.messages[0].content == "Hello, world!"
    
    @patch('src.api.client.requests.Session.request')
    def test_send_chat_request_success(self, mock_request, mock_client):
        """Test successful send_chat_request method."""
        # Mock successful HTTP response
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-4o-mini",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Hello there!"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        mock_request.return_value = mock_response
        
        # Create request
        messages = [ChatMessage(role="user", content="Hello!")]
        request = ChatCompletionRequest(messages=messages)
        
        # Make request
        result = mock_client.send_chat_request(request)
        
        # Verify result
        assert isinstance(result, ChatCompletionResponse)
        assert result.id == "chatcmpl-123"
        assert result.get_first_choice_content() == "Hello there!"
        
        # Verify HTTP request was made correctly
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert 'data' in call_kwargs
        
        # Verify request data
        sent_data = json.loads(call_kwargs['data'])
        assert sent_data['messages'][0]['content'] == "Hello!"
    
    def test_send_chat_request_invalid_request_type(self, mock_client):
        """Test send_chat_request with invalid request type."""
        with pytest.raises(ValueError, match="request must be a ChatCompletionRequest instance"):
            mock_client.send_chat_request("not a request")
    
    @patch('src.api.client.requests.Session.request')
    def test_send_chat_request_http_error(self, mock_request, mock_client):
        """Test send_chat_request with HTTP error."""
        mock_response = Mock(spec=Response)
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_request.return_value = mock_response
        
        messages = [ChatMessage(role="user", content="Hello!")]
        request = ChatCompletionRequest(messages=messages)
        
        with pytest.raises(Exception):  # Should raise some API exception
            mock_client.send_chat_request(request)
    
    @patch('src.api.client.requests.Session.request')
    def test_send_chat_request_invalid_json(self, mock_request, mock_client):
        """Test send_chat_request with invalid JSON response."""
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Invalid JSON response"
        mock_request.return_value = mock_response
        
        messages = [ChatMessage(role="user", content="Hello!")]
        request = ChatCompletionRequest(messages=messages)
        
        with pytest.raises(APIResponseError, match="Invalid JSON response"):
            mock_client.send_chat_request(request)
    
    @patch('src.api.client.requests.Session.request')
    def test_send_chat_request_authentication_required(self, mock_request):
        """Test that send_chat_request requires authentication."""
        # Create client without authentication
        client = APIClient()
        
        # Mock authentication method
        mock_auth_response = Mock()
        mock_auth_response.is_expired.return_value = False
        mock_auth_response.get_authorization_header.return_value = "Bearer test-token"
        
        with patch.object(client, 'authenticate', return_value=mock_auth_response) as mock_auth:
            # Mock successful HTTP response
            mock_response = Mock(spec=Response)
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677652288,
                "model": "gpt-4o-mini",
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": "Hello!"},
                    "finish_reason": "stop"
                }],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
            }
            mock_request.return_value = mock_response
            
            messages = [ChatMessage(role="user", content="Hello!")]
            request = ChatCompletionRequest(messages=messages)
            
            result = client.send_chat_request(request)
            
            # Verify authentication was called
            mock_auth.assert_called_once()
            assert isinstance(result, ChatCompletionResponse)


class TestIntegrationScenarios:
    """Integration test scenarios for chat completion functionality."""
    
    def test_full_chat_completion_workflow(self):
        """Test complete workflow from request creation to response parsing."""
        # Create messages for a multi-turn conversation
        messages = [
            ChatMessage(role="user", content="What is the capital of France?"),
            ChatMessage(role="assistant", content="The capital of France is Paris."),
            ChatMessage(role="user", content="What is its population?")
        ]
        
        # Create request
        request = ChatCompletionRequest(
            messages=messages,
            max_tokens=500,
            temperature=0.5
        )
        
        # Verify request structure
        request_dict = request.to_dict()
        assert len(request_dict['messages']) == 3
        assert request_dict['max_tokens'] == 500
        assert request_dict['temperature'] == 0.5
        
        # Simulate API response
        response_data = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-4o-mini",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Paris has a population of approximately 2.1 million people in the city proper."
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 20,
                "total_tokens": 70
            }
        }
        
        # Parse response
        response = ChatCompletionResponse.from_dict(response_data)
        
        # Verify response
        assert response.id == "chatcmpl-123"
        assert response.model == "gpt-4o-mini"
        assert len(response.choices) == 1
        assert "2.1 million" in response.get_first_choice_content()
        assert response.usage.total_tokens == 70
    
    def test_error_handling_chain(self):
        """Test error handling throughout the chain."""
        # Test invalid message creation
        with pytest.raises(ValueError):
            ChatMessage(role="invalid", content="Hello")
        
        # Test invalid request creation
        with pytest.raises(ValueError):
            ChatCompletionRequest(messages=[])
        
        # Test invalid response parsing
        with pytest.raises(APIResponseError):
            ChatCompletionResponse.from_dict({"invalid": "data"})
    
    def test_convenience_vs_power_user_methods(self):
        """Test that both convenience and power user methods work correctly."""
        client = APIClient()
        
        # Mock authentication
        client._auth_response = Mock()
        client._auth_response.is_expired.return_value = False
        client._auth_response.get_authorization_header.return_value = "Bearer test-token"
        
        # Test convenience method creates correct request
        with patch.object(client, 'send_chat_request') as mock_send:
            client.chat_completion("Hello", max_tokens=100, temperature=0.8)
            
            call_args = mock_send.call_args[0][0]
            assert isinstance(call_args, ChatCompletionRequest)
            assert call_args.max_tokens == 100
            assert call_args.temperature == 0.8
            assert len(call_args.messages) == 1
            assert call_args.messages[0].content == "Hello"
        
        # Test power user method with custom request
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Hello")
        ]
        custom_request = ChatCompletionRequest(
            messages=messages,
            max_tokens=200,
            temperature=0.3,
            allowed_models=["gpt-4"]
        )
        
        with patch.object(client, '_make_authenticated_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "id": "chatcmpl-123",
                "object": "chat.completion", 
                "created": 1677652288,
                "model": "gpt-4",
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": "Hi there!"},
                    "finish_reason": "stop"
                }],
                "usage": {"prompt_tokens": 20, "completion_tokens": 5, "total_tokens": 25}
            }
            mock_request.return_value = mock_response
            
            result = client.send_chat_request(custom_request)
            
            # Verify the request was sent with correct data
            mock_request.assert_called_once()
            call_kwargs = mock_request.call_args[1]
            sent_data = json.loads(call_kwargs['data'])
            
            assert len(sent_data['messages']) == 2
            assert sent_data['messages'][0]['role'] == "system"
            assert sent_data['max_tokens'] == 200
            assert sent_data['temperature'] == 0.3
            assert sent_data['allowedModels'] == ["gpt-4"]
            
            assert isinstance(result, ChatCompletionResponse)
            assert result.model == "gpt-4"