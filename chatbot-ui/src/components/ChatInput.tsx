/**
 * Chat input component with text field and send button
 * Handles Enter key press and message validation
 */

import React, { useState, KeyboardEvent, ChangeEvent, useRef } from 'react'
import UploadedFilesList from './UploadedFilesList'

interface ChatInputProps {
  onSendMessage: (message: string, files?: File[]) => void
  disabled?: boolean
  placeholder?: string
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  disabled = false,
  placeholder = "Type your message..." 
}) => {
  const [message, setMessage] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSend = () => {
    const trimmedMessage = message.trim()
    if (trimmedMessage && !disabled) {
      onSendMessage(trimmedMessage, files)
      setMessage('')
      setFiles([])
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

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || [])
    setFiles(prev => [...prev, ...selected])
    e.target.value = ''
  }

  const clearFiles = () => setFiles([])

  const openFilePicker = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="chat-input" data-testid="chat-input">
      <div className="input-container">
        <div className="uploads-row" style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, background: '#eef6ff', padding: 8, borderRadius: 6 }}>
          <button
          type="button"
            onClick={openFilePicker}
            className="upload-button"
            data-testid="upload-button"
            style={{
              border: '2px solid #007acc',
              padding: '8px 12px',
              borderRadius: 6,
              background: '#ffffff',
              color: '#007acc',
              cursor: 'pointer',
              fontWeight: 600
            }}
          >
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
          <UploadedFilesList files={files} onClear={clearFiles} />
    </div>
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