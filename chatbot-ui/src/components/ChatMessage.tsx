/**
 * Individual chat message component
 * Displays user and assistant messages with proper styling
 */

import React from 'react'
import { ChatMessage as ChatMessageType } from '../types/chat'

interface ChatMessageProps {
  message: ChatMessageType
  className?: string
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, className = '' }) => {
  const isUser = message.role === 'user'
  const isAssistant = message.role === 'assistant'
  
  // Don't render system messages in the UI
  if (message.role === 'system') {
    return null
  }

  const formatTimestamp = (timestamp?: Date) => {
    if (!timestamp) return ''
    return timestamp.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div 
      className={`chat-message ${isUser ? 'user' : 'assistant'} ${className}`}
      data-testid={`message-${message.role}`}
    >
      <div className="message-content">
        <div className="message-text">
          {message.content}
        </div>
        {message.timestamp && (
          <div className="message-timestamp">
            {formatTimestamp(message.timestamp)}
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatMessage