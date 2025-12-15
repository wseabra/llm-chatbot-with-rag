/**
 * Tests for ChatInput component
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ChatInput from './ChatInput'

describe('ChatInput', () => {
  const mockOnSendMessage = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders input field and send button', () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} />)
    
    expect(screen.getByTestId('message-input')).toBeInTheDocument()
    expect(screen.getByTestId('send-button')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument()
  })

  it('calls onSendMessage when send button is clicked', async () => {
    const user = userEvent.setup()
    render(<ChatInput onSendMessage={mockOnSendMessage} />)
    
    const input = screen.getByTestId('message-input')
    const sendButton = screen.getByTestId('send-button')
    
    await user.type(input, 'Hello world')
    await user.click(sendButton)
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('Hello world')
  })

  it('calls onSendMessage when Enter key is pressed', async () => {
    const user = userEvent.setup()
    render(<ChatInput onSendMessage={mockOnSendMessage} />)
    
    const input = screen.getByTestId('message-input')
    
    await user.type(input, 'Hello world')
    await user.keyboard('{Enter}')
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('Hello world')
  })

  it('does not send message when Shift+Enter is pressed', async () => {
    const user = userEvent.setup()
    render(<ChatInput onSendMessage={mockOnSendMessage} />)
    
    const input = screen.getByTestId('message-input')
    
    await user.type(input, 'Hello world')
    await user.keyboard('{Shift>}{Enter}{/Shift}')
    
    expect(mockOnSendMessage).not.toHaveBeenCalled()
  })

  it('clears input after sending message', async () => {
    const user = userEvent.setup()
    render(<ChatInput onSendMessage={mockOnSendMessage} />)
    
    const input = screen.getByTestId('message-input') as HTMLTextAreaElement
    
    await user.type(input, 'Hello world')
    await user.keyboard('{Enter}')
    
    expect(input.value).toBe('')
  })

  it('trims whitespace from messages', async () => {
    const user = userEvent.setup()
    render(<ChatInput onSendMessage={mockOnSendMessage} />)
    
    const input = screen.getByTestId('message-input')
    const sendButton = screen.getByTestId('send-button')
    
    await user.type(input, '  Hello world  ')
    await user.click(sendButton)
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('Hello world')
  })

  it('does not send empty or whitespace-only messages', async () => {
    const user = userEvent.setup()
    render(<ChatInput onSendMessage={mockOnSendMessage} />)
    
    const input = screen.getByTestId('message-input')
    const sendButton = screen.getByTestId('send-button')
    
    // Try empty message
    await user.click(sendButton)
    expect(mockOnSendMessage).not.toHaveBeenCalled()
    
    // Try whitespace-only message
    await user.type(input, '   ')
    await user.click(sendButton)
    expect(mockOnSendMessage).not.toHaveBeenCalled()
  })

  it('disables input and button when disabled prop is true', () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} disabled={true} />)
    
    const input = screen.getByTestId('message-input')
    const sendButton = screen.getByTestId('send-button')
    
    expect(input).toBeDisabled()
    expect(sendButton).toBeDisabled()
  })

  it('does not send message when disabled', async () => {
    const user = userEvent.setup()
    render(<ChatInput onSendMessage={mockOnSendMessage} disabled={true} />)
    
    const input = screen.getByTestId('message-input')
    
    // Try to type (should not work when disabled)
    await user.type(input, 'Hello world')
    await user.keyboard('{Enter}')
    
    expect(mockOnSendMessage).not.toHaveBeenCalled()
  })

  it('uses custom placeholder', () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} placeholder="Custom placeholder" />)
    
    expect(screen.getByPlaceholderText('Custom placeholder')).toBeInTheDocument()
  })

  it('disables send button when input is empty', () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} />)
    
    const sendButton = screen.getByTestId('send-button')
    expect(sendButton).toBeDisabled()
  })

  it('enables send button when input has content', async () => {
    const user = userEvent.setup()
    render(<ChatInput onSendMessage={mockOnSendMessage} />)
    
    const input = screen.getByTestId('message-input')
    const sendButton = screen.getByTestId('send-button')
    
    await user.type(input, 'Hello')
    
    expect(sendButton).not.toBeDisabled()
  })
})