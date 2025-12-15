/**
 * Integration tests for the complete chat application
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'
import chatApi from './services/chatApi'
import { mockFilteredResponse } from './__mocks__/chatApiMocks'

// Mock the chatApi
vi.mock('./services/chatApi', () => ({
  default: {
    sendMessage: vi.fn()
  }
}))

describe('App Integration Tests', () => {
  const mockSendMessage = vi.mocked(chatApi.sendMessage)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the complete chat interface', () => {
    render(<App />)
    
    // Check for main components
    expect(screen.getByText('AI Assistant')).toBeInTheDocument()
    expect(screen.getByText('Start a conversation by typing a message below.')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
  })

  it('handles complete conversation flow', async () => {
    const user = userEvent.setup()
    mockSendMessage.mockResolvedValueOnce(mockFilteredResponse)
    
    render(<App />)
    
    // Type a message
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Hello, how are you?')
    
    // Send the message
    const sendButton = screen.getByRole('button', { name: /send/i })
    await user.click(sendButton)
    
    // Verify API was called
    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith([
        expect.objectContaining({
          role: 'user',
          content: 'Hello, how are you?'
        })
      ])
    })
    
    // Verify messages appear in the UI
    await waitFor(() => {
      expect(screen.getByText('Hello, how are you?')).toBeInTheDocument()
      expect(screen.getByText(mockFilteredResponse.choices[0].message.content)).toBeInTheDocument()
    })
    
    // Verify input is cleared
    expect(input).toHaveValue('')
  })

  it('handles keyboard interaction (Enter key)', async () => {
    const user = userEvent.setup()
    mockSendMessage.mockResolvedValueOnce(mockFilteredResponse)
    
    render(<App />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Test message{Enter}')
    
    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith([
        expect.objectContaining({
          role: 'user',
          content: 'Test message'
        })
      ])
    })
  })

  it('shows loading state during API call', async () => {
    const user = userEvent.setup()
    // Mock a delayed response
    mockSendMessage.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve(mockFilteredResponse), 100))
    )
    
    render(<App />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    await user.type(input, 'Test message')
    await user.click(sendButton)
    
    // Should show loading state
    expect(screen.getByTestId('loading-message')).toBeInTheDocument()
    expect(sendButton).toBeDisabled()
    expect(input).toBeDisabled()
    
    // Wait for response
    await waitFor(() => {
      expect(screen.queryByTestId('loading-message')).not.toBeInTheDocument()
    })
    
    expect(sendButton).not.toBeDisabled()
    expect(input).not.toBeDisabled()
  })

  it('displays error message when API fails', async () => {
    const user = userEvent.setup()
    mockSendMessage.mockRejectedValueOnce(new Error('Network error'))
    
    render(<App />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Test message')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to send message: Network error/)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument()
    })
  })

  it('clears error when retry button is clicked', async () => {
    const user = userEvent.setup()
    mockSendMessage.mockRejectedValueOnce(new Error('Network error'))
    
    render(<App />)
    
    // Trigger error
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Test message')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to send message: Network error/)).toBeInTheDocument()
    })
    
    // Click retry
    const retryButton = screen.getByRole('button', { name: /try again/i })
    await user.click(retryButton)
    
    expect(screen.queryByText(/Failed to send message: Network error/)).not.toBeInTheDocument()
  })

  it('maintains conversation context across multiple messages', async () => {
    const user = userEvent.setup()
    mockSendMessage
      .mockResolvedValueOnce(mockFilteredResponse)
      .mockResolvedValueOnce({
        ...mockFilteredResponse,
        choices: [{
          message: { role: 'assistant', content: 'Second response' },
          finish_reason: 'stop'
        }]
      })
    
    render(<App />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    
    // Send first message
    await user.type(input, 'First message')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      expect(screen.getByText('First message')).toBeInTheDocument()
    })
    
    // Send second message
    await user.type(input, 'Second message')
    await user.keyboard('{Enter}')
    
    // Verify second API call includes conversation history
    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenLastCalledWith([
        expect.objectContaining({ role: 'user', content: 'First message' }),
        expect.objectContaining({ role: 'assistant' }),
        expect.objectContaining({ role: 'user', content: 'Second message' })
      ])
    })
  })

  it('prevents sending empty messages', async () => {
    const user = userEvent.setup()
    
    render(<App />)
    
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    // Button should be disabled when input is empty
    expect(sendButton).toBeDisabled()
    
    // Try to send empty message
    await user.click(sendButton)
    
    expect(mockSendMessage).not.toHaveBeenCalled()
  })

  it('trims whitespace from messages', async () => {
    const user = userEvent.setup()
    mockSendMessage.mockResolvedValueOnce(mockFilteredResponse)
    
    render(<App />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, '  Hello world  ')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith([
        expect.objectContaining({
          role: 'user',
          content: 'Hello world'
        })
      ])
    })
  })
})