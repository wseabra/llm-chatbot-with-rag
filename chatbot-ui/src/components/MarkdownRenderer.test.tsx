/**
 * Tests for MarkdownRenderer component using 'marked' library
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import MarkdownRenderer from './MarkdownRenderer'

// Mock DOMPurify
vi.mock('dompurify', () => ({
  default: {
    sanitize: vi.fn((html) => html) // Return HTML as-is for testing
  }
}))

describe('MarkdownRenderer with marked library', () => {
  it('renders plain text correctly', () => {
    render(<MarkdownRenderer content="Hello world" />)
    
    expect(screen.getByText('Hello world')).toBeInTheDocument()
  })

  it('renders headings correctly', () => {
    const markdown = `# Heading 1
## Heading 2
### Heading 3`
    
    render(<MarkdownRenderer content={markdown} />)
    
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Heading 1')
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Heading 2')
    expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('Heading 3')
    
    // Check custom classes
    expect(screen.getByRole('heading', { level: 1 })).toHaveClass('markdown-h1')
    expect(screen.getByRole('heading', { level: 2 })).toHaveClass('markdown-h2')
    expect(screen.getByRole('heading', { level: 3 })).toHaveClass('markdown-h3')
  })

  it('renders unordered lists correctly', () => {
    const markdown = `- Item 1
- Item 2
- Item 3`
    
    render(<MarkdownRenderer content={markdown} />)
    
    const list = screen.getByRole('list')
    expect(list.tagName).toBe('UL')
    expect(list).toHaveClass('markdown-ul')
    expect(screen.getByText('Item 1')).toBeInTheDocument()
    expect(screen.getByText('Item 2')).toBeInTheDocument()
    expect(screen.getByText('Item 3')).toBeInTheDocument()
  })

  it('renders ordered lists with repeated "1." correctly', () => {
    const markdown = `1. onions
1. tomatoes
1. cheese`
    
    render(<MarkdownRenderer content={markdown} />)
    
    const list = screen.getByRole('list')
    expect(list.tagName).toBe('OL')
    expect(list).toHaveClass('markdown-ol')
    
    const listItems = screen.getAllByRole('listitem')
    expect(listItems).toHaveLength(3)
    expect(listItems[0]).toHaveTextContent('onions')
    expect(listItems[1]).toHaveTextContent('tomatoes')
    expect(listItems[2]).toHaveTextContent('cheese')
    
    // Verify all items have the correct class
    listItems.forEach(item => {
      expect(item).toHaveClass('markdown-li')
    })
  })

  it('renders ordered lists with sequential numbers correctly', () => {
    const markdown = `1. First item
2. Second item
3. Third item`
    
    render(<MarkdownRenderer content={markdown} />)
    
    const list = screen.getByRole('list')
    expect(list.tagName).toBe('OL')
    expect(list).toHaveClass('markdown-ol')
    expect(screen.getByText('First item')).toBeInTheDocument()
    expect(screen.getByText('Second item')).toBeInTheDocument()
    expect(screen.getByText('Third item')).toBeInTheDocument()
  })

  it('renders inline code correctly', () => {
    const markdown = 'Here is some `inline code` in text'
    
    render(<MarkdownRenderer content={markdown} />)
    
    const codeElement = screen.getByText('inline code')
    expect(codeElement).toBeInTheDocument()
    expect(codeElement.tagName).toBe('CODE')
    expect(codeElement).toHaveClass('inline-code')
  })

  it('renders code blocks correctly', () => {
    const markdown = '```javascript\nconst hello = "world";\nconsole.log(hello);\n```'
    
    render(<MarkdownRenderer content={markdown} />)
    
    const codeBlock = screen.getByText('const hello = "world";\nconsole.log(hello);')
    expect(codeBlock).toBeInTheDocument()
    expect(codeBlock.closest('pre')).toHaveClass('code-block')
    expect(codeBlock.closest('pre')).toHaveAttribute('data-language', 'javascript')
    expect(codeBlock).toHaveClass('language-javascript')
  })

  it('renders links with proper security attributes', () => {
    const markdown = '[Google](https://google.com)'
    
    render(<MarkdownRenderer content={markdown} />)
    
    const link = screen.getByRole('link', { name: 'Google' })
    expect(link).toHaveAttribute('href', 'https://google.com')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    expect(link).toHaveClass('markdown-link')
  })

  it('renders blockquotes correctly', () => {
    const markdown = '> This is a blockquote\n> with multiple lines'
    
    render(<MarkdownRenderer content={markdown} />)
    
    const blockquote = document.querySelector('blockquote')
    expect(blockquote).toBeInTheDocument()
    expect(blockquote).toHaveClass('markdown-blockquote')
    expect(blockquote).toHaveTextContent('This is a blockquote with multiple lines')
  })

  it('renders tables correctly', () => {
    const markdown = `| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |`
    
    render(<MarkdownRenderer content={markdown} />)
    
    expect(screen.getByRole('table')).toBeInTheDocument()
    expect(screen.getByRole('table')).toHaveClass('markdown-table')
    expect(screen.getByRole('columnheader', { name: 'Header 1' })).toBeInTheDocument()
    expect(screen.getByRole('cell', { name: 'Cell 1' })).toBeInTheDocument()
    
    // Check table wrapper
    const tableWrapper = screen.getByRole('table').closest('.table-wrapper')
    expect(tableWrapper).toBeInTheDocument()
  })

  it('renders bold and italic text correctly', () => {
    const markdown = 'This is **bold** and this is *italic* text'
    
    render(<MarkdownRenderer content={markdown} />)
    
    const boldElement = screen.getByText('bold')
    const italicElement = screen.getByText('italic')
    
    expect(boldElement.tagName).toBe('STRONG')
    expect(boldElement).toHaveClass('markdown-strong')
    expect(italicElement.tagName).toBe('EM')
    expect(italicElement).toHaveClass('markdown-em')
  })

  it('renders horizontal rules correctly', () => {
    const markdown = 'Before\n\n---\n\nAfter'
    
    render(<MarkdownRenderer content={markdown} />)
    
    const hr = document.querySelector('hr')
    expect(hr).toBeInTheDocument()
    expect(hr).toHaveClass('markdown-hr')
  })

  it('handles complex grocery list correctly', () => {
    const markdown = `Shopping list:

1. onions
1. tomatoes
1. cheese
1. bread
1. milk

Don't forget the **important** items!`
    
    render(<MarkdownRenderer content={markdown} />)
    
    // Check paragraph
    expect(screen.getByText('Shopping list:')).toBeInTheDocument()
    
    // Check ordered list
    const list = screen.getByRole('list')
    expect(list.tagName).toBe('OL')
    expect(list).toHaveClass('markdown-ol')
    
    // Check all items
    const items = ['onions', 'tomatoes', 'cheese', 'bread', 'milk']
    items.forEach(item => {
      expect(screen.getByText(item)).toBeInTheDocument()
    })
    
    const listItems = screen.getAllByRole('listitem')
    expect(listItems).toHaveLength(5)
    
    // Check formatting in final paragraph
    expect(screen.getByText('important')).toBeInTheDocument()
    expect(screen.getByText('important').tagName).toBe('STRONG')
  })

  it('handles mixed content correctly', () => {
    const markdown = `# Recipe

## Ingredients:
1. onions
1. tomatoes
1. cheese

## Instructions:
- Chop the \`onions\`
- Slice the **tomatoes**
- Grate the *cheese*

> **Note:** Be careful with the knife!

For more recipes, visit [our website](https://example.com).`
    
    render(<MarkdownRenderer content={markdown} />)
    
    // Check headings
    expect(screen.getByRole('heading', { level: 1, name: 'Recipe' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: 'Ingredients:' })).toBeInTheDocument()
    
    // Check lists
    const lists = screen.getAllByRole('list')
    expect(lists).toHaveLength(2)
    expect(lists[0].tagName).toBe('OL') // Ingredients
    expect(lists[1].tagName).toBe('UL') // Instructions
    
    // Check inline formatting
    expect(screen.getByText('onions')).toHaveClass('inline-code')
    expect(screen.getByText('tomatoes')).toHaveClass('markdown-strong')
    expect(screen.getByText('cheese')).toHaveClass('markdown-em')
    
    // Check blockquote
    const blockquote = document.querySelector('blockquote')
    expect(blockquote).toHaveClass('markdown-blockquote')
    
    // Check link
    const link = screen.getByRole('link', { name: 'our website' })
    expect(link).toHaveAttribute('href', 'https://example.com')
  })

  it('applies custom className', () => {
    render(<MarkdownRenderer content="Test" className="custom-class" />)
    
    const container = screen.getByText('Test').closest('.markdown-renderer')
    expect(container).toHaveClass('custom-class')
  })

  it('handles empty content gracefully', () => {
    const { container } = render(<MarkdownRenderer content="" />)
    
    const markdownRenderer = container.querySelector('.markdown-renderer')
    expect(markdownRenderer).toBeInTheDocument()
    expect(markdownRenderer).toBeEmptyDOMElement()
  })

  it('handles line breaks correctly', () => {
    const markdown = 'Line 1\nLine 2\nLine 3'
    
    render(<MarkdownRenderer content={markdown} />)
    
    // With breaks: true, \n should become <br>
    const paragraph = screen.getByText(/Line 1/).closest('p')
    expect(paragraph).toBeInTheDocument()
    expect(paragraph?.innerHTML).toContain('<br>')
  })

  it('memoizes content to prevent unnecessary re-renders', () => {
    const content = 'Test content'
    const { rerender } = render(<MarkdownRenderer content={content} />)
    
    const firstRender = screen.getByText(content)
    
    // Re-render with same content
    rerender(<MarkdownRenderer content={content} />)
    
    const secondRender = screen.getByText(content)
    
    // Should be the same element (memoized)
    expect(firstRender).toBe(secondRender)
  })
})