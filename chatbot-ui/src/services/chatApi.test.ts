/**
 * Tests for simplified ChatAPI service
 * Tests the unified chat endpoint
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import chatApi from './chatApi'
import { 
  mockUserMessage, 
  mockApiResponse, 
  mockFilteredResponse,
  mockErrorResponse,
  createMockFetchResponse,
  createMockFetchError
} from '../__mocks__/chatApiMocks'

// Mock fetch globally
global.fetch = vi.fn()

describe('ChatAPI Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('sendMessage', () => {
    it('should send message without files using unified endpoint', async () => {
      // Mock successful API response with RAG metadata
      vi.mocked(fetch).mockResolvedValueOnce(
        createMockFetchResponse(mockApiResponse)
      )

      const result = await chatApi.sendMessage([mockUserMessage])

      // Verify fetch was called with FormData to unified endpoint
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/chat', {
        method: 'POST',
        body: expect.any(FormData),
      })

      // Verify RAG metadata is filtered out
      expect(result).toEqual(mockFilteredResponse)
      expect(result).not.toHaveProperty('rag_metadata')
    })

    it('should send message with files using unified endpoint', async () => {
      const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' })
      
      vi.mocked(fetch).mockResolvedValueOnce(
        createMockFetchResponse(mockApiResponse)
      )

      const result = await chatApi.sendMessage([mockUserMessage], [mockFile])

      // Verify fetch was called with FormData including files
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/chat', {
        method: 'POST',
        body: expect.any(FormData),
      })

      expect(result).toEqual(mockFilteredResponse)
    })

    it('should handle API errors gracefully', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(
        createMockFetchResponse(mockErrorResponse, false, 400)
      )

      await expect(chatApi.sendMessage([mockUserMessage]))
        .rejects.toThrow('Failed to send message: Invalid request parameters')
    })

    it('should handle network errors', async () => {
      vi.mocked(fetch).mockRejectedValueOnce(createMockFetchError())

      await expect(chatApi.sendMessage([mockUserMessage]))
        .rejects.toThrow('Failed to send message: Network error')
    })

    it('should handle empty response body', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.reject(new Error('No JSON')),
      } as Response)

      await expect(chatApi.sendMessage([mockUserMessage]))
        .rejects.toThrow('Failed to send message: HTTP 500: Internal Server Error')
    })

    it('should handle unknown errors', async () => {
      vi.mocked(fetch).mockRejectedValueOnce('Unknown error')

      await expect(chatApi.sendMessage([mockUserMessage]))
        .rejects.toThrow('Failed to send message: Unknown error')
    })
  })

  describe('checkHealth', () => {
    it('should return true when API is healthy', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(
        createMockFetchResponse({ status: 'healthy' })
      )

      const result = await chatApi.checkHealth()
      
      expect(result).toBe(true)
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/health')
    })

    it('should return false when API is unhealthy', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(
        createMockFetchResponse({}, false, 503)
      )

      const result = await chatApi.checkHealth()
      
      expect(result).toBe(false)
    })

    it('should return false on network error', async () => {
      vi.mocked(fetch).mockRejectedValueOnce(createMockFetchError())

      const result = await chatApi.checkHealth()
      
      expect(result).toBe(false)
    })
  })
})