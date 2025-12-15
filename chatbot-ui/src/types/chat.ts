/**
 * Chat-related TypeScript interfaces and types
 * RAG metadata is filtered out and not exposed to the UI
 */

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
  timestamp?: Date
}

export interface ChatChoice {
  message: ChatMessage
  finish_reason: string
}

export interface ChatUsage {
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
}

// Full API response (includes RAG metadata that we filter out)
export interface ChatApiResponse {
  id: string
  model: string
  choices: ChatChoice[]
  usage: ChatUsage
  created: number
  rag_metadata?: {
    rag_enabled: boolean
    sources_used: number
    context_provided: boolean
    sources?: string[]
    similarity_scores?: number[]
    similarity_threshold?: number
  }
}

// Filtered response for UI (no RAG metadata)
export interface ChatResponse {
  id: string
  model: string
  choices: ChatChoice[]
  usage: ChatUsage
  created: number
}

export interface ChatRequest {
  messages: ChatMessage[]
  max_tokens?: number
  temperature?: number
  stream?: boolean
  allowed_models?: string[]
}

export interface ChatError {
  message: string
  status?: number
  code?: string
}

export interface ChatState {
  messages: ChatMessage[]
  isLoading: boolean
  error: ChatError | null
}