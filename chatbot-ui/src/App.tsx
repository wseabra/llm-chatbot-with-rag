import React, { useState } from 'react'
import SimpleMarkdownRenderer from './components/SimpleMarkdownRenderer'
import './App.css'

function App() {
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSend = async () => {
    if (!inputValue.trim()) return
    
    const userMessage = { role: 'user', content: inputValue.trim() }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/chat/advanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          max_tokens: 4096,
          temperature: 0.7,
          stream: false,
          allowed_models: ['gpt-4o-mini']
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('API Response:', data) // Debug log
        
        if (data.choices && data.choices[0] && data.choices[0].message) {
          const assistantContent = data.choices[0].message.content
          console.log('Assistant content:', assistantContent, 'Type:', typeof assistantContent) // Debug log
          
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: assistantContent
          }])
        } else {
          console.error('Unexpected API response structure:', data)
        }
      } else {
        console.error('API request failed:', response.status, response.statusText)
        const errorText = await response.text()
        console.error('Error response:', errorText)
      }
    } catch (error) {
      console.error('Error:', error)
      // Add error message to chat
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const renderMessageContent = (message: {role: string, content: string}) => {
    console.log('Rendering message:', message.role, 'Content:', message.content, 'Type:', typeof message.content) // Debug log
    
    if (message.role === 'assistant') {
      // Use simple markdown renderer for assistant messages
      return <SimpleMarkdownRenderer content={message.content} />
    } else {
      // Plain text for user messages
      return message.content
    }
  }

  return (
    <div className="App">
      <div className="chat-container">
        <div className="chat-header">
          <h1>AI Assistant</h1>
        </div>
        
        <div className="chat-content">
          <div className="chat-history">
            {messages.length === 0 ? (
              <div className="empty-state">
                <p>Start a conversation by typing a message below.</p>
              </div>
            ) : (
              <div className="messages-container">
                {messages.map((message, index) => (
                  <div key={index} className={`chat-message ${message.role}`}>
                    <div className="message-content">
                      <div className="message-text">
                        {renderMessageContent(message)}
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
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
                )}
              </div>
            )}
          </div>
        </div>
        
        <div className="chat-footer">
          <div className="chat-input">
            <div className="input-container">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="message-input"
                disabled={isLoading}
                rows={1}
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !inputValue.trim()}
                className="send-button"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App