import React, { useState, useRef, ChangeEvent } from 'react'
import SimpleMarkdownRenderer from './components/SimpleMarkdownRenderer'
import './App.css'

type UiMessage = { role: string; content: string; attachments?: string[] }

function App() {
  const [messages, setMessages] = useState<Array<UiMessage>>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [files, setFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || [])
    setFiles(prev => [...prev, ...selected])
    e.target.value = ''
  }

  const clearFiles = () => setFiles([])

  const handleSend = async () => {
    const trimmed = inputValue.trim()
    if (!trimmed) return

    const userMessage: UiMessage = { role: 'user', content: trimmed }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)
    const sentFiles = [...files]

    try {
      // Use unified chat endpoint for all messages
      const form = new FormData()
      const minimalMessages = [...messages, userMessage].map(m => ({ role: m.role, content: m.content }))
      form.append('messages', JSON.stringify(minimalMessages))
      form.append('max_tokens', String(4096))
      form.append('temperature', String(0.7))
      form.append('stream', String(false))
      form.append('allowed_models', 'gpt-4o-mini')
      
      // Add files if any (unified endpoint handles both cases)
      for (const file of sentFiles) {
        form.append('files', file, file.name)
      }

      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        body: form
      })

      if (response.ok) {
        const data = await response.json()
        if (data.choices && data.choices[0] && data.choices[0].message) {
          const assistantMessage: UiMessage = {
            role: 'assistant',
            content: data.choices[0].message.content,
          }
          if (sentFiles.length > 0) {
            assistantMessage.attachments = sentFiles.map(f => f.name)
          }
          setMessages(prev => [...prev, assistantMessage])
        }
        setFiles([])
      } else {
        const errorText = await response.text()
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `Error: HTTP ${response.status} ${response.statusText} - ${errorText}`
        }])
      }
    } catch (error) {
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

  const renderMessageContent = (message: UiMessage) => {
    if (message.role === 'assistant') {
      return <SimpleMarkdownRenderer content={message.content} />
    } else {
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
                    {message.attachments && message.attachments.length > 0 && (
                      <ul className="message-attachments">
                        {message.attachments.map((name, i) => (
                          <li key={`${name}-${i}`}>{name}</li>
                        ))}
                      </ul>
                    )}
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
              <div className="upload-area" data-testid="upload-area">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="upload-button"
                  data-testid="upload-button"
                >
                  <span className="upload-icon" aria-hidden>📎</span>
                  Attach files
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                  accept=".txt,.md,.pdf"
                />
                {files.length > 0 && (
                  <div className="uploaded-files-inline">
                    <span className="attached-label">Attached:</span>
                    {files.map((f, i) => (
                      <span key={`${f.name}-${i}`} className="file-chip">
                        {f.name}
                      </span>
                    ))}
                    <button
                      type="button"
                      onClick={clearFiles}
                      className="clear-files"
                    >
                      Clear
                    </button>
                  </div>
                )}
              </div>

              <div className="input-row">
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
    </div>
  )
}

export default App