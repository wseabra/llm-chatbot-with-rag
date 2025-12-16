/**
 * Chat API service for communicating with the FastAPI backend
 * Uses the unified chat endpoint for all interactions
 */

import { ChatMessage, ChatResponse, ChatApiResponse } from '../types/chat'

const API_BASE_URL = 'http://localhost:8000'

class ChatApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Send a chat message with optional file uploads using the unified endpoint
   */
  async sendMessage(messages: ChatMessage[], files: File[] = []): Promise<ChatResponse> {
    try {
      const form = new FormData()
      
      // Prepare minimal message format
      const minimalMessages = messages.map(m => ({ 
        role: m.role, 
        content: m.content 
      }))
      
      // Add form data
      form.append('messages', JSON.stringify(minimalMessages))
      form.append('max_tokens', String(4096))
      form.append('temperature', String(0.7))
      form.append('stream', String(false))
      form.append('allowed_models', 'gpt-4o-mini')

      // Add files if provided
      for (const file of files) {
        form.append('files', file, file.name)
      }

      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        body: form,
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

      return {
        id: apiResponse.id,
        model: apiResponse.model,
        choices: apiResponse.choices,
        usage: apiResponse.usage,
        created: apiResponse.created,
      }
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to send message: ${error.message}`)
      }
      throw new Error('Failed to send message: Unknown error')
    }
  }

  /**
   * Check if the API service is healthy
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

export const chatApi = new ChatApiService()
export default chatApi