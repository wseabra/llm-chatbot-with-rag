"""
Example usage of the API module.

This script demonstrates how to use the APIClient to perform health checks,
authenticate with the API, handle different types of errors, and use the
chat completion functionality.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flowApi import (
    APIClient,
    HealthResponse,
    AuthResponse,
    ChatMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    APIConnectionError,
    APITimeoutError,
    APIHTTPError,
    APIResponseError,
    APIAuthenticationError,
    APIConfigurationError
)


def main():
    """
    Demonstrate API client usage with proper error handling.
    """
    print("API Client Usage Example")
    print("=" * 40)
    
    # Example 1: Basic usage with context manager
    print("\n1. Basic Health Check (with context manager):")
    try:
        with APIClient() as client:
            health = client.health_check()
            print(f"   Status: {health}")
            print(f"   Result: {health.result}")
            print(f"   Timestamp: {health.timestamp}")
            
    except APIConnectionError as e:
        print(f"   Connection Error: {e}")
    except APITimeoutError as e:
        print(f"   Timeout Error: {e}")
    except APIHTTPError as e:
        print(f"   HTTP Error: {e}")
    except APIResponseError as e:
        print(f"   Response Error: {e}")
    
    # Example 2: Authentication workflow
    print("\n2. Authentication Workflow:")
    try:
        with APIClient() as client:
            # Authenticate with the API
            auth_response = client.authenticate()
            print(f"   Authentication successful!")
            print(f"   Token expires in: {auth_response.expires_in} seconds")
            print(f"   Time until expiry: {auth_response.time_until_expiry():.1f} seconds")
            print(f"   Is authenticated: {client.is_authenticated()}")
            
            # Get auth info
            auth_info = client.get_auth_info()
            if auth_info:
            
            # Test basic health check (always unauthenticated)
            health = client.health_check()
            print(f"   Health check result: {health.result}")
            
    except APIConfigurationError as e:
        print(f"   Configuration Error: {e}")
        print("   Make sure CLIENT_ID and CLIENT_SECRET are set in your .env file")
    except APIAuthenticationError as e:
        print(f"   Authentication Error: {e}")
    except APIConnectionError as e:
        print(f"   Connection Error: {e}")
    except APITimeoutError as e:
        print(f"   Timeout Error: {e}")
    except APIHTTPError as e:
        print(f"   HTTP Error: {e}")
    except APIResponseError as e:
        print(f"   Response Error: {e}")
    
    # Example 3: Simple Chat Completion
    print("\n3. Simple Chat Completion:")
    try:
        with APIClient() as client:
            # Simple, single-line usage
            response = client.chat_completion("Give me a list of the days of the week.")
            print(f"   AI Response: {response.get_first_choice_content()}")
            print(f"   Response ID: {response.id}")
            print(f"   Model used: {response.model}")
            print(f"   Token usage: {response.usage}")
            
    except APIConfigurationError as e:
        print(f"   Configuration Error: {e}")
        print("   Make sure CLIENT_ID and CLIENT_SECRET are set in your .env file")
    except APIAuthenticationError as e:
        print(f"   Authentication Error: {e}")
    except APIConnectionError as e:
        print(f"   Connection Error: {e}")
    except Exception as e:
        print(f"   Chat completion error: {e}")
    
    # Example 4: Chat Completion with Custom Parameters
    print("\n4. Chat Completion with Custom Parameters:")
    try:
        with APIClient() as client:
            # Overriding default parameters
            response = client.chat_completion(
                "Explain quantum computing in simple terms.",
                max_tokens=500,
                temperature=0.5
            )
            print(f"   AI Response: {response.get_first_choice_content()}")
            print(f"   Tokens used: {response.usage.total_tokens}")
            
    except Exception as e:
        print(f"   Custom parameters chat error: {e}")
    
    # Example 5: Advanced Multi-turn Conversation
    print("\n5. Advanced Multi-turn Conversation:")
    try:
        with APIClient() as client:
            # Advanced usage for multi-turn conversation
            messages = [
                ChatMessage(role="user", content="What is the capital of France?"),
                ChatMessage(role="assistant", content="The capital of France is Paris."),
                ChatMessage(role="user", content="What is its population?")
            ]
            full_request = ChatCompletionRequest(messages=messages)
            response = client.send_chat_request(full_request)
            
            print(f"   Conversation context: {len(messages)} messages")
            print(f"   AI Response: {response.get_first_choice_content()}")
            print(f"   Finish reason: {response.choices[0].finish_reason}")
            
    except Exception as e:
        print(f"   Multi-turn conversation error: {e}")
    
    # Example 6: Custom configuration
    print("\n6. Custom Configuration:")
    try:
        client = APIClient(
            base_url="https://flow.ciandt.com",
            timeout=60
        )
        
        health = client.health_check()
        print(f"   Health check successful: {health.result}")
        
        # Convert to dictionary for JSON serialization
        health_dict = health.to_dict()
        print(f"   As dict: {health_dict}")
        
        # Don't forget to close when not using context manager
        client.close()
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 40)
    print("Example completed!")


def demonstrate_chat_models():
    """
    Demonstrate chat completion models and their usage.
    """
    print("\nChat Completion Models Demonstration")
    print("-" * 40)
    
    # Example 1: Creating and validating ChatMessage
    print("1. ChatMessage Creation and Validation:")
    try:
        # Valid message
        user_msg = ChatMessage(role="user", content="Hello, AI!")
        print(f"   ✓ User message: {user_msg}")
        
        assistant_msg = ChatMessage(role="assistant", content="Hello! How can I help you?")
        print(f"   ✓ Assistant message: {assistant_msg}")
        
        # Convert to dict
        msg_dict = user_msg.to_dict()
        print(f"   ✓ Message as dict: {msg_dict}")
        
        # Create from dict
        recreated_msg = ChatMessage.from_dict(msg_dict)
        print(f"   ✓ Recreated from dict: {recreated_msg}")
        
    except (ValueError, APIResponseError) as e:
        print(f"   ✗ Validation error: {e}")
    
    # Example 2: Creating ChatCompletionRequest
    print("\n2. ChatCompletionRequest Creation:")
    try:
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="What is machine learning?")
        ]
        
        # Default parameters
        request = ChatCompletionRequest(messages=messages)
        print(f"   ✓ Default request: {request}")
        
        # Custom parameters
        custom_request = ChatCompletionRequest(
            messages=messages,
            max_tokens=1000,
            temperature=0.3,
            allowed_models=["gpt-4", "gpt-3.5-turbo"]
        )
        print(f"   ✓ Custom request: {custom_request}")
        
        # Convert to dict for API
        request_dict = custom_request.to_dict()
        print(f"   ✓ Request dict keys: {list(request_dict.keys())}")
        
    except (ValueError, APIResponseError) as e:
        print(f"   ✗ Request creation error: {e}")
    
    # Example 3: Simulating API Response
    print("\n3. ChatCompletionResponse Parsing:")
    try:
        # Simulate API response data
        response_data = {
            "id": "chatcmpl-123456",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-4o-mini",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed."
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 25,
                "completion_tokens": 30,
                "total_tokens": 55
            }
        }
        
        # Parse response
        response = ChatCompletionResponse.from_dict(response_data)
        print(f"   ✓ Response parsed: {response}")
        print(f"   ✓ AI answer: {response.get_first_choice_content()}")
        print(f"   ✓ Usage: {response.usage}")
        
        # Convert back to dict
        response_dict = response.to_dict()
        print(f"   ✓ Response serialized back to dict successfully")
        
    except APIResponseError as e:
        print(f"   ✗ Response parsing error: {e}")


def demonstrate_error_handling():
    """
    Demonstrate comprehensive error handling for chat completions.
    """
    print("\nError Handling Demonstration")
    print("-" * 40)
    
    # Example 1: Invalid message creation
    print("1. Invalid Message Creation:")
    try:
        ChatMessage(role="invalid_role", content="Hello")
        print("   ✗ Should have failed!")
    except (ValueError, APIResponseError) as e:
        print(f"   ✓ Caught invalid role: {e}")
    
    try:
        ChatMessage(role="user", content="")
        print("   ✗ Should have failed!")
    except (ValueError, APIResponseError) as e:
        print(f"   ✓ Caught empty content: {e}")
    
    # Example 2: Invalid request creation
    print("\n2. Invalid Request Creation:")
    try:
        ChatCompletionRequest(messages=[])
        print("   ✗ Should have failed!")
    except (ValueError, APIResponseError) as e:
        print(f"   ✓ Caught empty messages: {e}")
    
    try:
        ChatCompletionRequest(
            messages=[ChatMessage(role="user", content="Hello")],
            max_tokens=-1
        )
        print("   ✗ Should have failed!")
    except (ValueError, APIResponseError) as e:
        print(f"   ✓ Caught invalid max_tokens: {e}")
    
    try:
        ChatCompletionRequest(
            messages=[ChatMessage(role="user", content="Hello")],
            temperature=3.0
        )
        print("   ✗ Should have failed!")
    except (ValueError, APIResponseError) as e:
        print(f"   ✓ Caught invalid temperature: {e}")
    
    # Example 3: Invalid response parsing
    print("\n3. Invalid Response Parsing:")
    try:
        ChatCompletionResponse.from_dict({"invalid": "data"})
        print("   ✗ Should have failed!")
    except APIResponseError as e:
        print(f"   ✓ Caught invalid response format: {e}")
    
    try:
        ChatCompletionResponse.from_dict({
            "id": "test",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-4",
            "choices": [],  # Empty choices should fail
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        })
        print("   ✗ Should have failed!")
    except (ValueError, APIResponseError) as e:
        print(f"   ✓ Caught empty choices: {e}")


def demonstrate_convenience_vs_power():
    """
    Demonstrate the difference between convenience and power user methods.
    """
    print("\nConvenience vs Power User Methods")
    print("-" * 40)
    
    try:
        with APIClient() as client:
            print("1. Convenience Method (chat_completion):")
            print("   - Simple, single-turn conversations")
            print("   - Default parameters with easy overrides")
            print("   - Automatic request construction")
            
            # This would make an actual API call if credentials are available
            # response = client.chat_completion("What is Python?")
            # print(f"   Response: {response.get_first_choice_content()}")
            
            print("\n2. Power User Method (send_chat_request):")
            print("   - Full control over all parameters")
            print("   - Multi-turn conversations")
            print("   - Custom model selection")
            
            # Create a complex request
            messages = [
                ChatMessage(role="system", content="You are a Python expert."),
                ChatMessage(role="user", content="What is Python?"),
                ChatMessage(role="assistant", content="Python is a programming language."),
                ChatMessage(role="user", content="What are its main features?")
            ]
            
            advanced_request = ChatCompletionRequest(
                messages=messages,
                max_tokens=200,
                temperature=0.2,
                allowed_models=["gpt-4"]
            )
            
            print(f"   ✓ Advanced request created: {advanced_request}")
            print(f"   ✓ Message count: {len(advanced_request.messages)}")
            print(f"   ✓ Custom parameters: max_tokens={advanced_request.max_tokens}, temp={advanced_request.temperature}")
            
            # This would make an actual API call if credentials are available
            # response = client.send_chat_request(advanced_request)
            # print(f"   Response: {response.get_first_choice_content()}")
            
    except Exception as e:
        print(f"   Demo error (expected if no credentials): {e}")


def demonstrate_real_world_scenarios():
    """
    Demonstrate real-world usage scenarios.
    """
    print("\nReal-World Usage Scenarios")
    print("-" * 40)
    
    print("1. Customer Support Chatbot:")
    try:
        # Simulate a customer support conversation
        messages = [
            ChatMessage(role="system", content="You are a helpful customer support agent."),
            ChatMessage(role="user", content="I'm having trouble with my order."),
            ChatMessage(role="assistant", content="I'd be happy to help! Can you provide your order number?"),
            ChatMessage(role="user", content="It's ORDER-12345")
        ]
        
        request = ChatCompletionRequest(
            messages=messages,
            max_tokens=150,
            temperature=0.3  # Lower temperature for more consistent responses
        )
        
        print(f"   ✓ Support conversation request: {len(request.messages)} messages")
        print(f"   ✓ Configured for consistent responses (temp={request.temperature})")
        
    except Exception as e:
        print(f"   Error in support scenario: {e}")
    
    print("\n2. Creative Writing Assistant:")
    try:
        # Creative writing with higher temperature
        creative_request = ChatCompletionRequest(
            messages=[ChatMessage(role="user", content="Write a short story about a robot learning to paint.")],
            max_tokens=500,
            temperature=0.8  # Higher temperature for creativity
        )
        
        print(f"   ✓ Creative writing request configured")
        print(f"   ✓ Higher temperature for creativity (temp={creative_request.temperature})")
        print(f"   ✓ More tokens for longer response (max_tokens={creative_request.max_tokens})")
        
    except Exception as e:
        print(f"   Error in creative scenario: {e}")
    
    print("\n3. Code Review Assistant:")
    try:
        # Code review with system prompt
        code_review_messages = [
            ChatMessage(role="system", content="You are an expert code reviewer. Provide constructive feedback."),
            ChatMessage(role="user", content="Please review this Python function:\n\ndef add_numbers(a, b):\n    return a + b")
        ]
        
        code_request = ChatCompletionRequest(
            messages=code_review_messages,
            max_tokens=300,
            temperature=0.1  # Very low temperature for technical accuracy
        )
        
        print(f"   ✓ Code review request configured")
        print(f"   ✓ System prompt for expert behavior")
        print(f"   ✓ Low temperature for technical accuracy (temp={code_request.temperature})")
        
    except Exception as e:
        print(f"   Error in code review scenario: {e}")


if __name__ == "__main__":
    main()
    demonstrate_chat_models()
    demonstrate_error_handling()
    demonstrate_convenience_vs_power()
    demonstrate_real_world_scenarios()