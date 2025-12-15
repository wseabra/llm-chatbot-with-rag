import React, { useState } from 'react'
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
        if (data.choices && data.choices[0]) {
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: data.choices[0].message.content
          }])
        }
      }
    } catch (error) {
      console.error('Error:', error)
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
                        {message.content}
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