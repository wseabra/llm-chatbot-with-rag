/**
 * Chat input component with text field and send button
 * Handles Enter key press and message validation
 */

import React, { useState, KeyboardEvent } from 'react'

interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  disabled = false,
  placeholder = "Type your message..." 
}) => {
  const [message, setMessage] = useState('')

  const handleSend = () => {
    const trimmedMessage = message.trim()
    if (trimmedMessage && !disabled) {
      onSendMessage(trimmedMessage)
      setMessage('')
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value)
  }

  return (
    <div className="chat-input" data-testid="chat-input">
      <div className="input-container">
        <textarea
          value={message}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled}
          className="message-input"
          data-testid="message-input"
          rows={1}
          style={{ resize: 'none' }}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          className="send-button"
          data-testid="send-button"
          type="button"
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default ChatInput