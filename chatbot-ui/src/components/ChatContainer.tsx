import React, { useState, useCallback } from 'react'
import ChatHistory from './ChatHistory'
import ChatInput from './ChatInput'
import chatApi from '../services/chatApi'
import { ChatMessage, ChatState, ChatError } from '../types/chat'

const ChatContainer: React.FC = () => {
  const [chatState, setChatState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null
  })

  const addMessage = useCallback((message: ChatMessage) => {
    setChatState(prev => ({
      ...prev,
      messages: [...prev.messages, { ...message, timestamp: new Date() }]
    }))
  }, [])

  const setLoading = useCallback((loading: boolean) => {
    setChatState(prev => ({
      ...prev,
      isLoading: loading
    }))
  }, [])

  const setError = useCallback((error: ChatError | null) => {
    setChatState(prev => ({
      ...prev,
      error
    }))
  }, [])

  const handleSendMessage = useCallback(async (content: string, files?: File[]) => {
    try {
      setError(null)
      
      const userMessage: ChatMessage = {
        role: 'user',
        content,
        timestamp: new Date()
      }
      addMessage(userMessage)
      setLoading(true)
      
      const messagesToSend = [...chatState.messages, userMessage]
      
      const response = files && files.length > 0
        ? await chatApi.sendMessageWithUploads(messagesToSend, files)
        : await chatApi.sendMessage(messagesToSend)
      
      if (response.choices && response.choices.length > 0) {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: response.choices[0].message.content,
          timestamp: new Date()
        }
        addMessage(assistantMessage)
      }
    } catch (error) {
      const chatError: ChatError = {
        message: error instanceof Error ? error.message : 'An unexpected error occurred',
        code: 'SEND_MESSAGE_ERROR'
      }
      setError(chatError)
    } finally {
      setLoading(false)
    }
  }, [chatState.messages, addMessage, setLoading, setError])

  const handleRetry = useCallback(() => {
    setError(null)
  }, [setError])

  return (
    <div className="chat-container" data-testid="chat-container">
      <div className="chat-header">
        <h1>AI Assistant</h1>
      </div>
      
      <div className="chat-content">
        <ChatHistory 
          messages={chatState.messages}
          isLoading={chatState.isLoading}
        />
        
        {chatState.error && (
          <div className="error-message" data-testid="error-message">
            <div className="error-content">
              <p>{chatState.error.message}</p>
              <button 
                onClick={handleRetry}
                className="retry-button"
                data-testid="retry-button"
              >
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>
      
      <div className="chat-footer">
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={chatState.isLoading}
          placeholder="Type your message..."
        />
      </div>
    </div>
  )
}

export default ChatContainer