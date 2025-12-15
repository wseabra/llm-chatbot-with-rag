/**
 * Simple fallback markdown renderer without external dependencies
 * Use this if the marked library is causing issues
 */

import React, { memo } from 'react'
import '../styles/markdown.css'

interface SimpleMarkdownRendererProps {
  content: string
  className?: string
}

const SimpleMarkdownRenderer: React.FC<SimpleMarkdownRendererProps> = memo(({ content, className = '' }) => {
  if (!content || typeof content !== 'string') {
    console.warn('SimpleMarkdownRenderer received invalid content:', content)
    return <div className={`markdown-renderer ${className}`}>{String(content || '')}</div>
  }

  // Simple markdown parsing for basic elements
  const parseMarkdown = (text: string): JSX.Element[] => {
    const lines = text.split('\n')
    const elements: JSX.Element[] = []
    let key = 0

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      const trimmedLine = line.trim()

      if (!trimmedLine) {
        elements.push(<br key={key++} />)
        continue
      }

      // Headers
      if (trimmedLine.startsWith('#')) {
        const headerMatch = trimmedLine.match(/^(#{1,6})\s+(.+)/)
        if (headerMatch) {
          const level = headerMatch[1].length as 1 | 2 | 3 | 4 | 5 | 6
          const text = headerMatch[2]
          const HeaderTag = `h${level}` as keyof JSX.IntrinsicElements
          elements.push(
            <HeaderTag key={key++} className={`markdown-h${level}`}>
              {parseInlineElements(text)}
            </HeaderTag>
          )
          continue
        }
      }

      // Ordered lists
      if (trimmedLine.match(/^\d+\.\s+/)) {
        const listItems: string[] = []
        while (i < lines.length && lines[i].trim().match(/^\d+\.\s+/)) {
          const itemText = lines[i].trim().replace(/^\d+\.\s+/, '')
          listItems.push(itemText)
          i++
        }
        i-- // Adjust for the outer loop increment

        elements.push(
          <ol key={key++} className="markdown-ol">
            {listItems.map((item, idx) => (
              <li key={idx} className="markdown-li">
                {parseInlineElements(item)}
              </li>
            ))}
          </ol>
        )
        continue
      }

      // Unordered lists
      if (trimmedLine.match(/^[-*+]\s+/)) {
        const listItems: string[] = []
        while (i < lines.length && lines[i].trim().match(/^[-*+]\s+/)) {
          const itemText = lines[i].trim().substring(2)
          listItems.push(itemText)
          i++
        }
        i-- // Adjust for the outer loop increment

        elements.push(
          <ul key={key++} className="markdown-ul">
            {listItems.map((item, idx) => (
              <li key={idx} className="markdown-li">
                {parseInlineElements(item)}
              </li>
            ))}
          </ul>
        )
        continue
      }

      // Code blocks
      if (trimmedLine.startsWith('```')) {
        const language = trimmedLine.substring(3).trim()
        const codeLines: string[] = []
        i++ // Move past the opening ```
        
        while (i < lines.length && !lines[i].trim().startsWith('```')) {
          codeLines.push(lines[i])
          i++
        }
        
        elements.push(
          <pre key={key++} className="code-block" data-language={language || 'text'}>
            <code>{codeLines.join('\n')}</code>
          </pre>
        )
        continue
      }

      // Blockquotes
      if (trimmedLine.startsWith('>')) {
        const quoteLines: string[] = []
        while (i < lines.length && lines[i].trim().startsWith('>')) {
          quoteLines.push(lines[i].trim().substring(1).trim())
          i++
        }
        i-- // Adjust for the outer loop increment

        elements.push(
          <blockquote key={key++} className="markdown-blockquote">
            <p className="markdown-p">{parseInlineElements(quoteLines.join(' '))}</p>
          </blockquote>
        )
        continue
      }

      // Regular paragraphs
      elements.push(
        <p key={key++} className="markdown-p">
          {parseInlineElements(trimmedLine)}
        </p>
      )
    }

    return elements
  }

  const parseInlineElements = (text: string): (string | JSX.Element)[] => {
    const elements: (string | JSX.Element)[] = []
    let remaining = text
    let key = 0

    // Process inline elements
    while (remaining) {
      // Bold text **text**
      const boldMatch = remaining.match(/^(.*?)\*\*(.*?)\*\*(.*)$/)
      if (boldMatch) {
        if (boldMatch[1]) elements.push(boldMatch[1])
        elements.push(<strong key={key++} className="markdown-strong">{boldMatch[2]}</strong>)
        remaining = boldMatch[3]
        continue
      }

      // Italic text *text*
      const italicMatch = remaining.match(/^(.*?)\*(.*?)\*(.*)$/)
      if (italicMatch) {
        if (italicMatch[1]) elements.push(italicMatch[1])
        elements.push(<em key={key++} className="markdown-em">{italicMatch[2]}</em>)
        remaining = italicMatch[3]
        continue
      }

      // Inline code `code`
      const codeMatch = remaining.match(/^(.*?)`([^`]+)`(.*)$/)
      if (codeMatch) {
        if (codeMatch[1]) elements.push(codeMatch[1])
        elements.push(<code key={key++} className="inline-code">{codeMatch[2]}</code>)
        remaining = codeMatch[3]
        continue
      }

      // Links [text](url)
      const linkMatch = remaining.match(/^(.*?)\[([^\]]+)\]\(([^)]+)\)(.*)$/)
      if (linkMatch) {
        if (linkMatch[1]) elements.push(linkMatch[1])
        elements.push(
          <a 
            key={key++} 
            href={linkMatch[3]} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="markdown-link"
          >
            {linkMatch[2]}
          </a>
        )
        remaining = linkMatch[4]
        continue
      }

      // No more matches, add remaining text
      elements.push(remaining)
      break
    }

    return elements
  }

  return (
    <div className={`markdown-renderer ${className}`}>
      {parseMarkdown(content)}
    </div>
  )
})

SimpleMarkdownRenderer.displayName = 'SimpleMarkdownRenderer'

export default SimpleMarkdownRenderer