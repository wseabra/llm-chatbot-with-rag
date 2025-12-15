/**
 * Chat history component that displays all messages
 * Handles auto-scrolling to latest message
 */

import React, { useEffect, useRef } from 'react'
import ChatMessage from './ChatMessage'
import { ChatMessage as ChatMessageType } from '../types/chat'

interface ChatHistoryProps {
  messages: ChatMessageType[]
  isLoading?: boolean
  className?: string
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ 
  messages, 
  isLoading = false,
  className = '' 
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div 
      className={`chat-history ${className}`}
      data-testid="chat-history"
    >
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state" data-testid="empty-state">
            <p>Start a conversation by typing a message below.</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <ChatMessage
              key={`${message.role}-${index}-${message.timestamp?.getTime() || Date.now()}`}
              message={message}
            />
          ))
        )}
        
        {isLoading && (
          <div className="loading-message" data-testid="loading-message">
            <div className="chat-message assistant">
              <div className="message-content">
                <div className="message-text">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}

export default ChatHistory