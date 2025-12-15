/**
 * Chat API service for communicating with the FastAPI backend
 * Filters out RAG metadata to keep it transparent to the user
 */

import { ChatMessage, ChatRequest, ChatResponse, ChatApiResponse } from '../types/chat'

const API_BASE_URL = 'http://localhost:8000'

class ChatApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

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
      
      return {
        id: apiResponse.id,
        model: apiResponse.model,
        choices: apiResponse.choices,
        usage: apiResponse.usage,
        created: apiResponse.created
      }
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to send message: ${error.message}`)
      }
      throw new Error('Failed to send message: Unknown error')
    }
  }

  async sendMessageWithUploads(messages: ChatMessage[], files: File[]): Promise<ChatResponse> {
    try {
      const form = new FormData()
      const minimalMessages = messages.map(m => ({ role: m.role, content: m.content }))
      form.append('messages', JSON.stringify(minimalMessages))
      form.append('max_tokens', String(4096))
      form.append('temperature', String(0.7))
      form.append('stream', String(false))
      form.append('allowed_models', 'gpt-4o-mini')

      for (const file of files) {
        form.append('files', file, file.name)
      }

      const response = await fetch(`${this.baseUrl}/chat/uploaded`, {
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