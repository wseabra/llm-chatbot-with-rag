/**
 * Tests for ChatHistory component
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import ChatHistory from './ChatHistory'
import { mockConversation } from '../__mocks__/chatApiMocks'

// Mock the ChatMessage component
vi.mock('./ChatMessage', () => ({
  default: ({ message }: { message: any }) => (
    <div data-testid={`mock-message-${message.role}`}>
      {message.content}
    </div>
  )
}))

describe('ChatHistory', () => {
  it('renders empty state when no messages', () => {
    render(<ChatHistory messages={[]} />)
    
    expect(screen.getByTestId('empty-state')).toBeInTheDocument()
    expect(screen.getByText('Start a conversation by typing a message below.')).toBeInTheDocument()
  })

  it('renders messages when provided', () => {
    render(<ChatHistory messages={mockConversation} />)
    
    expect(screen.queryByTestId('empty-state')).not.toBeInTheDocument()
    expect(screen.getAllByTestId(/mock-message-/)).toHaveLength(4)
    expect(screen.getByTestId('mock-message-user')).toBeInTheDocument()
    expect(screen.getByTestId('mock-message-assistant')).toBeInTheDocument()
  })

  it('shows loading indicator when isLoading is true', () => {
    render(<ChatHistory messages={mockConversation} isLoading={true} />)
    
    expect(screen.getByTestId('loading-message')).toBeInTheDocument()
    expect(screen.getByText('', { selector: '.typing-indicator' })).toBeInTheDocument()
  })

  it('does not show loading indicator when isLoading is false', () => {
    render(<ChatHistory messages={mockConversation} isLoading={false} />)
    
    expect(screen.queryByTestId('loading-message')).not.toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<ChatHistory messages={[]} className="custom-class" />)
    
    const historyElement = screen.getByTestId('chat-history')
    expect(historyElement).toHaveClass('custom-class')
  })

  it('renders correct number of messages', () => {
    const messages = mockConversation.slice(0, 2)
    render(<ChatHistory messages={messages} />)
    
    expect(screen.getAllByTestId(/mock-message-/)).toHaveLength(2)
  })

  it('generates unique keys for messages', () => {
    // Test that messages with same content but different timestamps get unique keys
    const duplicateMessages = [
      { role: 'user' as const, content: 'Hello', timestamp: new Date('2024-01-01T10:00:00Z') },
      { role: 'user' as const, content: 'Hello', timestamp: new Date('2024-01-01T10:01:00Z') }
    ]
    
    render(<ChatHistory messages={duplicateMessages} />)
    
    expect(screen.getAllByTestId('mock-message-user')).toHaveLength(2)
  })
})