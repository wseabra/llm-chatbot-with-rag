/**
 * Markdown renderer component using the 'marked' library
 * Provides robust markdown parsing with security sanitization
 */

import React, { memo, useMemo } from 'react'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import '../styles/markdown.css'

interface MarkdownRendererProps {
  content: string
  className?: string
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = memo(({ content, className = '' }) => {
  const htmlContent = useMemo(() => {
    if (!content) return ''
    
    try {
      // Ensure content is a string and not an object
      let markdownContent: string
      
      if (typeof content === 'string') {
        markdownContent = content
      } else if (typeof content === 'object') {
        // If it's an object, try to stringify it or extract meaningful content
        console.warn('MarkdownRenderer received object instead of string:', content)
        markdownContent = JSON.stringify(content, null, 2)
      } else {
        markdownContent = String(content)
      }
      
      // Configure marked with simple options
      marked.setOptions({
        breaks: true,
        gfm: true,
        headerIds: false,
        mangle: false,
      })
      
      // Parse markdown to HTML
      let rawHtml: string
      
      // Handle both sync and async versions of marked
      const result = marked.parse(markdownContent)
      if (typeof result === 'string') {
        rawHtml = result
      } else if (result && typeof result.then === 'function') {
        // If it's a Promise, we can't handle it in useMemo, return original content
        console.warn('Marked returned a Promise, falling back to plain text')
        return markdownContent
      } else {
        rawHtml = String(result)
      }
      
      // Sanitize HTML to prevent XSS attacks
      const cleanHtml = DOMPurify.sanitize(rawHtml, {
        ALLOWED_TAGS: [
          'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
          'p', 'br', 'strong', 'em', 'code', 'pre',
          'ul', 'ol', 'li', 'blockquote', 'hr',
          'table', 'thead', 'tbody', 'tr', 'th', 'td',
          'a', 'div', 'span'
        ],
        ALLOWED_ATTR: [
          'class', 'href', 'target', 'rel', 'title', 'style'
        ],
        ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i
      })
      
      return cleanHtml
    } catch (error) {
      console.error('Error parsing markdown:', error, 'Content:', content)
      // Fallback to plain text
      return typeof content === 'string' ? content : String(content)
    }
  }, [content])

  return (
    <div 
      className={`markdown-renderer ${className}`}
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  )
})

MarkdownRenderer.displayName = 'MarkdownRenderer'

export default MarkdownRenderer