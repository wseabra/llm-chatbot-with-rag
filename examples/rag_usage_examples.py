#!/usr/bin/env python3
"""
RAG Usage Examples

This script demonstrates how to use the RAG-enhanced chat endpoints
with practical examples.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

import httpx

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class RAGChatClient:
    """Client for interacting with RAG-enhanced chat endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the client."""
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def simple_chat(self, message: str, **kwargs) -> Dict[str, Any]:
        """
        Send a simple chat message with RAG enhancement.
        
        Args:
            message: User message
            **kwargs: Additional parameters (max_tokens, temperature)
            
        Returns:
            Chat response with RAG metadata
        """
        payload = {
            "message": message,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        response = await self.client.post(
            f"{self.base_url}/chat/completion",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def advanced_chat(self, messages: list, **kwargs) -> Dict[str, Any]:
        """
        Send an advanced chat conversation with RAG enhancement.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters
            
        Returns:
            Chat response with RAG metadata
        """
        payload = {
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": kwargs.get("stream", False)
        }
        
        response = await self.client.post(
            f"{self.base_url}/chat/advanced",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def get_rag_status(self) -> Dict[str, Any]:
        """Get RAG system status."""
        response = await self.client.get(f"{self.base_url}/rag/status")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()


async def example_1_simple_questions():
    """Example 1: Simple questions with RAG enhancement."""
    print("🔍 Example 1: Simple Questions with RAG Enhancement")
    print("=" * 60)
    
    client = RAGChatClient()
    
    try:
        # Check RAG status first
        status = await client.get_rag_status()
        print(f"RAG Status: {status.get('status', 'unknown')}")
        print(f"RAG Available: {status.get('is_available', False)}")
        print(f"RAG Ready: {status.get('is_ready', False)}")
        
        if not status.get('is_ready', False):
            print("⚠️  RAG system is not ready. Responses will not include context.")
        
        print()
        
        # Test questions
        questions = [
            "What is this company about?",
            "What services do you offer?",
            "How can I get started?",
            "What are the main features?",
            "Tell me about the technical architecture"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"Question {i}: {question}")
            
            try:
                response = await client.simple_chat(question)
                
                # Extract response details
                content = response.get('content', 'No content')
                rag_metadata = response.get('rag_metadata', {})
                
                print(f"Answer: {content[:200]}{'...' if len(content) > 200 else ''}")
                
                # Show RAG metadata
                if rag_metadata.get('rag_enabled'):
                    sources_used = rag_metadata.get('sources_used', 0)
                    context_provided = rag_metadata.get('context_provided', False)
                    
                    print(f"RAG Info: {sources_used} sources used, context provided: {context_provided}")
                    
                    if 'sources' in rag_metadata:
                        sources = rag_metadata['sources'][:3]  # Show first 3 sources
                        print(f"Sources: {', '.join(sources)}")
                else:
                    print("RAG Info: No RAG enhancement (system not available or no relevant context)")
                
                print("-" * 40)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                print("-" * 40)
    
    finally:
        await client.close()


async def example_2_conversation_context():
    """Example 2: Multi-turn conversation with context."""
    print("\n💬 Example 2: Multi-turn Conversation with Context")
    print("=" * 60)
    
    client = RAGChatClient()
    
    try:
        # Build a conversation
        conversation = [
            {"role": "user", "content": "What is this company about?"}
        ]
        
        print("Starting conversation...")
        
        # First message
        response = await client.advanced_chat(conversation)
        assistant_response = response['choices'][0]['message']['content']
        
        print(f"User: {conversation[0]['content']}")
        print(f"Assistant: {assistant_response[:300]}{'...' if len(assistant_response) > 300 else ''}")
        
        # Show RAG info
        rag_metadata = response.get('rag_metadata', {})
        if rag_metadata.get('context_provided'):
            print(f"RAG: Used {rag_metadata.get('sources_used', 0)} sources")
        
        print()
        
        # Add assistant response to conversation
        conversation.append({"role": "assistant", "content": assistant_response})
        
        # Follow-up questions
        follow_ups = [
            "Can you tell me more about the technical details?",
            "What are the pricing options?",
            "How do I get support?"
        ]
        
        for follow_up in follow_ups:
            conversation.append({"role": "user", "content": follow_up})
            
            response = await client.advanced_chat(conversation)
            assistant_response = response['choices'][0]['message']['content']
            
            print(f"User: {follow_up}")
            print(f"Assistant: {assistant_response[:200]}{'...' if len(assistant_response) > 200 else ''}")
            
            # Show RAG info
            rag_metadata = response.get('rag_metadata', {})
            if rag_metadata.get('context_provided'):
                print(f"RAG: Used {rag_metadata.get('sources_used', 0)} sources")
            
            print()
            
            # Add to conversation
            conversation.append({"role": "assistant", "content": assistant_response})
    
    finally:
        await client.close()


async def example_3_different_query_types():
    """Example 3: Different types of queries to test RAG."""
    print("\n🎯 Example 3: Different Query Types")
    print("=" * 60)
    
    client = RAGChatClient()
    
    try:
        # Different types of queries
        query_types = [
            ("Factual", "What is the company name and what do they do?"),
            ("Technical", "What technologies are used in the system?"),
            ("Process", "How does the onboarding process work?"),
            ("Comparison", "What makes this different from competitors?"),
            ("Specific", "What are the system requirements?"),
            ("General", "Tell me everything about this company"),
            ("Unrelated", "What's the weather like today?")  # Should get no context
        ]
        
        for query_type, query in query_types:
            print(f"{query_type} Query: {query}")
            
            try:
                response = await client.simple_chat(query)
                
                content = response.get('content', 'No content')
                rag_metadata = response.get('rag_metadata', {})
                
                print(f"Response: {content[:150]}{'...' if len(content) > 150 else ''}")
                
                # Analyze RAG effectiveness
                if rag_metadata.get('rag_enabled'):
                    sources_used = rag_metadata.get('sources_used', 0)
                    context_provided = rag_metadata.get('context_provided', False)
                    
                    if context_provided:
                        similarity_scores = rag_metadata.get('similarity_scores', [])
                        avg_score = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
                        print(f"RAG: {sources_used} sources, avg similarity: {avg_score:.3f}")
                    else:
                        print("RAG: No relevant context found")
                else:
                    print("RAG: System not available")
                
                print("-" * 50)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                print("-" * 50)
    
    finally:
        await client.close()


async def example_4_parameter_testing():
    """Example 4: Testing different parameters."""
    print("\n⚙️ Example 4: Parameter Testing")
    print("=" * 60)
    
    client = RAGChatClient()
    
    try:
        base_question = "What are the main features of this system?"
        
        # Test different temperatures
        temperatures = [0.1, 0.5, 0.9]
        
        for temp in temperatures:
            print(f"Temperature: {temp}")
            
            response = await client.simple_chat(
                base_question,
                temperature=temp,
                max_tokens=200
            )
            
            content = response.get('content', 'No content')
            rag_metadata = response.get('rag_metadata', {})
            
            print(f"Response: {content}")
            
            if rag_metadata.get('context_provided'):
                print(f"RAG: {rag_metadata.get('sources_used', 0)} sources used")
            
            print("-" * 40)
    
    finally:
        await client.close()


async def main():
    """Run all examples."""
    print("RAG Usage Examples")
    print("=" * 60)
    print("This script demonstrates various ways to use the RAG-enhanced chat API.")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print()
    
    try:
        # Test server connectivity
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health/simple")
            response.raise_for_status()
            print("✅ Server is running and accessible")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please start the server with: python -m uvicorn src.main:app --reload")
        return
    
    # Run examples
    await example_1_simple_questions()
    await example_2_conversation_context()
    await example_3_different_query_types()
    await example_4_parameter_testing()
    
    print("\n🎉 All examples completed!")
    print("\nNext steps:")
    print("1. Try your own questions with the API")
    print("2. Add more documents to the RAG folder")
    print("3. Experiment with different RAG parameters")
    print("4. Integrate RAG into your own applications")


if __name__ == "__main__":
    asyncio.run(main())