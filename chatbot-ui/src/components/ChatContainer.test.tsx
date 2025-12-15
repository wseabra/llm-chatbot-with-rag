/**
 * Tests for ChatContainer component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ChatContainer from './ChatContainer'
import chatApi from '../services/chatApi'
import { mockFilteredResponse } from '../__mocks__/chatApiMocks'

// Mock the chatApi
vi.mock('../services/chatApi', () => ({
  default: {
    sendMessage: vi.fn()
  }
}))

// Mock child components
vi.mock('./ChatHistory', () => ({
  default: ({ messages, isLoading }: { messages: any[], isLoading: boolean }) => (
    <div data-testid="mock-chat-history">
      <div data-testid="messages-count">{messages.length}</div>
      {isLoading && <div data-testid="mock-loading">Loading...</div>}
    </div>
  )
}))

vi.mock('./ChatInput', () => ({
  default: ({ onSendMessage, disabled }: { onSendMessage: (msg: string) => void, disabled: boolean }) => (
    <div data-testid="mock-chat-input">
      <button 
        onClick={() => onSendMessage('Test message')}
        disabled={disabled}
        data-testid="mock-send-button"
      >
        Send Test Message
      </button>
    </div>
  )
}))

describe('ChatContainer', () => {
  const mockSendMessage = vi.mocked(chatApi.sendMessage)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders chat container with header, content, and footer', () => {
    render(<ChatContainer />)
    
    expect(screen.getByTestId('chat-container')).toBeInTheDocument()
    expect(screen.getByText('AI Assistant')).toBeInTheDocument()
    expect(screen.getByTestId('mock-chat-history')).toBeInTheDocument()
    expect(screen.getByTestId('mock-chat-input')).toBeInTheDocument()
  })

  it('starts with empty message history', () => {
    render(<ChatContainer />)
    
    expect(screen.getByTestId('messages-count')).toHaveTextContent('0')
  })

  it('sends message and updates history', async () => {
    const user = userEvent.setup()
    mockSendMessage.mockResolvedValueOnce(mockFilteredResponse)
    
    render(<ChatContainer />)
    
    const sendButton = screen.getByTestId('mock-send-button')
    await user.click(sendButton)
    
    // Should show loading state
    expect(screen.getByTestId('mock-loading')).toBeInTheDocument()
    
    // Wait for API call to complete
    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith([
        expect.objectContaining({
          role: 'user',
          content: 'Test message'
        })
      ])
    })
    
    // Should have 2 messages (user + assistant)
    await waitFor(() => {
      expect(screen.getByTestId('messages-count')).toHaveTextContent('2')
    })
  })

  it('handles API errors gracefully', async () => {
    const user = userEvent.setup()
    mockSendMessage.mockRejectedValueOnce(new Error('API Error'))
    
    render(<ChatContainer />)
    
    const sendButton = screen.getByTestId('mock-send-button')
    await user.click(sendButton)
    
    // Wait for error to appear
    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument()
    })
    
    expect(screen.getByText(/Failed to send message: API Error/)).toBeInTheDocument()
    expect(screen.getByTestId('retry-button')).toBeInTheDocument()
  })

  it('clears error when retry button is clicked', async () => {
    const user = userEvent.setup()
    mockSendMessage.mockRejectedValueOnce(new Error('API Error'))
    
    render(<ChatContainer />)
    
    // Trigger error
    const sendButton = screen.getByTestId('mock-send-button')
    await user.click(sendButton)
    
    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument()
    })
    
    // Click retry
    const retryButton = screen.getByTestId('retry-button')
    await user.click(retryButton)
    
    expect(screen.queryByTestId('error-message')).not.toBeInTheDocument()
  })

  it('disables input during loading', async () => {
    const user = userEvent.setup()
    // Mock a slow API response
    mockSendMessage.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
    
    render(<ChatContainer />)
    
    const sendButton = screen.getByTestId('mock-send-button')
    await user.click(sendButton)
    
    // Input should be disabled during loading
    expect(sendButton).toBeDisabled()
  })

  it('maintains conversation history across multiple messages', async () => {
    const user = userEvent.setup()
    mockSendMessage
      .mockResolvedValueOnce(mockFilteredResponse)
      .mockResolvedValueOnce(mockFilteredResponse)
    
    render(<ChatContainer />)
    
    const sendButton = screen.getByTestId('mock-send-button')
    
    // Send first message
    await user.click(sendButton)
    await waitFor(() => {
      expect(screen.getByTestId('messages-count')).toHaveTextContent('2')
    })
    
    // Send second message
    await user.click(sendButton)
    await waitFor(() => {
      expect(screen.getByTestId('messages-count')).toHaveTextContent('4')
    })
    
    // Verify API was called with conversation history
    expect(mockSendMessage).toHaveBeenCalledTimes(2)
    expect(mockSendMessage).toHaveBeenLastCalledWith([
      expect.objectContaining({ role: 'user', content: 'Test message' }),
      expect.objectContaining({ role: 'assistant' }),
      expect.objectContaining({ role: 'user', content: 'Test message' })
    ])
  })

  it('handles empty API response gracefully', async () => {
    const user = userEvent.setup()
    mockSendMessage.mockResolvedValueOnce({
      ...mockFilteredResponse,
      choices: []
    })
    
    render(<ChatContainer />)
    
    const sendButton = screen.getByTestId('mock-send-button')
    await user.click(sendButton)
    
    await waitFor(() => {
      // Should only have user message, no assistant response
      expect(screen.getByTestId('messages-count')).toHaveTextContent('1')
    })
  })
})