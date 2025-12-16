"""
Simple provider configuration.

Choose your provider here. This is the only file you need to modify
to switch between different LLM providers.
"""

import os
from .flow_provider import FlowProvider
from .openai_provider import OpenAIProvider


def get_llm_provider():
    """
    Get the configured LLM provider.
    
    To use a different provider:
    1. Uncomment the provider you want to use
    2. Make sure you have the required API keys set
    3. Install any required packages
    
    Returns:
        LLMProvider: The configured provider instance
    """
    
    # Default: Use CI&T Flow
    return FlowProvider()
    
    # To use OpenAI instead:
    # return OpenAIProvider()
    
    # To use OpenAI with explicit API key:
    # return OpenAIProvider(api_key="your_api_key_here")
    