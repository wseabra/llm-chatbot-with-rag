"""
Simple tests for the LLM provider system.
"""

import pytest
from src.llm_providers.base import LLMProvider, LLMRequest, LLMResponse, LLMMessage, LLMChoice, LLMUsage
from src.llm_providers.exceptions import LLMProviderError


class MockProvider(LLMProvider):
    """Mock provider for testing."""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
    
    async def chat_completion(self, request: LLMRequest) -> LLMResponse:
        if self.should_fail:
            raise LLMProviderError("Mock failure")
        
        choice = LLMChoice(
            message=LLMMessage(role="assistant", content="Mock response"),
            finish_reason="stop"
        )
        
        usage = LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        
        return LLMResponse(
            id="mock-123",
            model="mock-model",
            choices=[choice],
            usage=usage
        )
    
    async def health_check(self) -> bool:
        return not self.should_fail


class TestLLMProviderBase:
    """Test the base classes."""
    
    def test_llm_message_creation(self):
        """Test LLMMessage creation."""
        message = LLMMessage(role="user", content="Hello")
        assert message.role == "user"
        assert message.content == "Hello"
    
    def test_llm_message_validation(self):
        """Test LLMMessage validation."""
        with pytest.raises(ValueError):
            LLMMessage(role="invalid", content="Hello")
        
        with pytest.raises(ValueError):
            LLMMessage(role="user", content="")
    
    def test_llm_request_creation(self):
        """Test LLMRequest creation."""
        messages = [LLMMessage(role="user", content="Hello")]
        request = LLMRequest(messages=messages)
        
        assert len(request.messages) == 1
        assert request.max_tokens == 4096
        assert request.temperature == 0.7
    
    def test_llm_request_validation(self):
        """Test LLMRequest validation."""
        with pytest.raises(ValueError):
            LLMRequest(messages=[])
    
    def test_llm_response_get_content(self):
        """Test LLMResponse get_content method."""
        choice = LLMChoice(
            message=LLMMessage(role="assistant", content="Test response"),
            finish_reason="stop"
        )
        usage = LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        
        response = LLMResponse(
            id="test-123",
            model="test-model",
            choices=[choice],
            usage=usage
        )
        
        assert response.get_content() == "Test response"


class TestMockProvider:
    """Test the mock provider."""
    
    @pytest.mark.asyncio
    async def test_successful_completion(self):
        """Test successful chat completion."""
        provider = MockProvider()
        request = LLMRequest(
            messages=[LLMMessage(role="user", content="Hello")]
        )
        
        response = await provider.chat_completion(request)
        
        assert response.id == "mock-123"
        assert response.model == "mock-model"
        assert len(response.choices) == 1
        assert response.get_content() == "Mock response"
    
    @pytest.mark.asyncio
    async def test_provider_failure(self):
        """Test provider failure handling."""
        provider = MockProvider(should_fail=True)
        request = LLMRequest(
            messages=[LLMMessage(role="user", content="Hello")]
        )
        
        with pytest.raises(LLMProviderError):
            await provider.chat_completion(request)
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check."""
        healthy_provider = MockProvider(should_fail=False)
        unhealthy_provider = MockProvider(should_fail=True)
        
        assert await healthy_provider.health_check() == True
        assert await unhealthy_provider.health_check() == False


class TestProviderConfig:
    """Test provider configuration."""
    
    def test_import_provider_config(self):
        """Test that provider config can be imported."""
        from src.llm_providers.provider_config import get_llm_provider
        
        provider = get_llm_provider()
        assert isinstance(provider, LLMProvider)
    
    def test_import_dependencies(self):
        """Test that dependencies can be imported."""
        from src.llm_providers.dependencies import get_llm_provider_dependency
        
        # Just test that it imports without error
        assert callable(get_llm_provider_dependency)


if __name__ == "__main__":
    pytest.main([__file__])