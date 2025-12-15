/**
 * Tests for ChatMessage component
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ChatMessage from './ChatMessage'
import { mockUserMessage, mockAssistantMessage } from '../__mocks__/chatApiMocks'

describe('ChatMessage', () => {
  it('renders user message correctly', () => {
    render(<ChatMessage message={mockUserMessage} />)
    
    expect(screen.getByTestId('message-user')).toBeInTheDocument()
    expect(screen.getByText(mockUserMessage.content)).toBeInTheDocument()
    expect(screen.getByText('10:00 AM')).toBeInTheDocument()
  })

  it('renders assistant message correctly', () => {
    render(<ChatMessage message={mockAssistantMessage} />)
    
    expect(screen.getByTestId('message-assistant')).toBeInTheDocument()
    expect(screen.getByText(mockAssistantMessage.content)).toBeInTheDocument()
    expect(screen.getByText('10:00 AM')).toBeInTheDocument()
  })

  it('does not render system messages', () => {
    const systemMessage = {
      role: 'system' as const,
      content: 'You are a helpful assistant',
      timestamp: new Date()
    }
    
    const { container } = render(<ChatMessage message={systemMessage} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders message without timestamp', () => {
    const messageWithoutTimestamp = {
      ...mockUserMessage,
      timestamp: undefined
    }
    
    render(<ChatMessage message={messageWithoutTimestamp} />)
    
    expect(screen.getByTestId('message-user')).toBeInTheDocument()
    expect(screen.getByText(messageWithoutTimestamp.content)).toBeInTheDocument()
    expect(screen.queryByText('10:00 AM')).not.toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<ChatMessage message={mockUserMessage} className="custom-class" />)
    
    const messageElement = screen.getByTestId('message-user')
    expect(messageElement).toHaveClass('custom-class')
  })

  it('applies correct CSS classes for user messages', () => {
    render(<ChatMessage message={mockUserMessage} />)
    
    const messageElement = screen.getByTestId('message-user')
    expect(messageElement).toHaveClass('chat-message', 'user')
  })

  it('applies correct CSS classes for assistant messages', () => {
    render(<ChatMessage message={mockAssistantMessage} />)
    
    const messageElement = screen.getByTestId('message-assistant')
    expect(messageElement).toHaveClass('chat-message', 'assistant')
  })
})