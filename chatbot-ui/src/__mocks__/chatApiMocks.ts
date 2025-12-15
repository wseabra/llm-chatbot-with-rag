/**
 * Mock data and utilities for testing chat functionality
 */

import { ChatMessage, ChatResponse, ChatApiResponse } from '../types/chat'

export const mockUserMessage: ChatMessage = {
  role: 'user',
  content: 'Hello, how are you?',
  timestamp: new Date('2024-01-01T10:00:00Z')
}

export const mockAssistantMessage: ChatMessage = {
  role: 'assistant',
  content: 'Hello! I\'m doing well, thank you for asking. How can I help you today?',
  timestamp: new Date('2024-01-01T10:00:01Z')
}

export const mockConversation: ChatMessage[] = [
  mockUserMessage,
  mockAssistantMessage,
  {
    role: 'user',
    content: 'Can you help me with React?',
    timestamp: new Date('2024-01-01T10:01:00Z')
  },
  {
    role: 'assistant',
    content: 'Of course! I\'d be happy to help you with React. What specific aspect would you like to learn about?',
    timestamp: new Date('2024-01-01T10:01:01Z')
  }
]

// Mock API response with RAG metadata (that gets filtered out)
export const mockApiResponse: ChatApiResponse = {
  id: 'chatcmpl-123',
  model: 'gpt-4o-mini',
  choices: [
    {
      message: mockAssistantMessage,
      finish_reason: 'stop'
    }
  ],
  usage: {
    prompt_tokens: 10,
    completion_tokens: 20,
    total_tokens: 30
  },
  created: 1704110401,
  rag_metadata: {
    rag_enabled: true,
    sources_used: 2,
    context_provided: true,
    sources: ['doc1.pdf', 'doc2.txt'],
    similarity_scores: [0.85, 0.78],
    similarity_threshold: 0.7
  }
}

// Expected filtered response (no RAG metadata)
export const mockFilteredResponse: ChatResponse = {
  id: 'chatcmpl-123',
  model: 'gpt-4o-mini',
  choices: [
    {
      message: mockAssistantMessage,
      finish_reason: 'stop'
    }
  ],
  usage: {
    prompt_tokens: 10,
    completion_tokens: 20,
    total_tokens: 30
  },
  created: 1704110401
}

export const mockErrorResponse = {
  detail: {
    status: 'error',
    message: 'Invalid request parameters',
    error: 'Message content cannot be empty'
  }
}

// Mock fetch responses
export const createMockFetchResponse = (data: any, ok: boolean = true, status: number = 200) => {
  return Promise.resolve({
    ok,
    status,
    statusText: ok ? 'OK' : 'Error',
    json: () => Promise.resolve(data),
  } as Response)
}

export const createMockFetchError = () => {
  return Promise.reject(new Error('Network error'))
}