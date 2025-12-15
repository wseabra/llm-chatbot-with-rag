/**
 * Chat API service for communicating with the FastAPI backend
 * Filters out RAG metadata to keep it transparent to the user
 */

import { ChatMessage, ChatRequest, ChatResponse, ChatApiResponse, ChatError } from '../types/chat'

const API_BASE_URL = 'http://localhost:8000'

class ChatApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Send a chat request to the advanced chat endpoint
   * Filters out RAG metadata from the response
   */
  async sendMessage(messages: ChatMessage[]): Promise<ChatResponse> {
    try {
      const request: ChatRequest = {
        messages,
        max_tokens: 4096,
        temperature: 0.7,
        stream: false,
        allowed_models: ['gpt-4o-mini']
      }

      const response = await fetch(`${this.baseUrl}/chat/advanced`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(
          errorData.detail?.message || 
          errorData.message || 
          `HTTP ${response.status}: ${response.statusText}`
        )
      }

      const apiResponse: ChatApiResponse = await response.json()
      
      // Filter out RAG metadata - user doesn't need to know about it
      const filteredResponse: ChatResponse = {
        id: apiResponse.id,
        model: apiResponse.model,
        choices: apiResponse.choices,
        usage: apiResponse.usage,
        created: apiResponse.created
        // rag_metadata is intentionally omitted
      }

      return filteredResponse
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to send message: ${error.message}`)
      }
      throw new Error('Failed to send message: Unknown error')
    }
  }

  /**
   * Check if the API is available
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`)
      return response.ok
    } catch {
      return false
    }
  }
}

// Export singleton instance
export const chatApi = new ChatApiService()
export default chatApi