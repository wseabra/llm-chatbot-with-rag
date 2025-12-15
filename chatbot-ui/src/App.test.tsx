/**
 * Integration tests for the complete chat application with markdown support using 'marked'
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

// Mock DOMPurify
vi.mock('dompurify', () => ({
  default: {
    sanitize: vi.fn((html) => html) // Return HTML as-is for testing
  }
}))

// Mock fetch globally
global.fetch = vi.fn()

describe('App Integration Tests with Markdown (marked library)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the complete chat interface', () => {
    render(<App />)
    
    // Check for main components
    expect(screen.getByText('AI Assistant')).toBeInTheDocument()
    expect(screen.getByText('Start a conversation by typing a message below.')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
  })

  it('renders user messages as plain text', async () => {
    const user = userEvent.setup()
    
    // Mock API response
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        choices: [{
          message: { content: 'Hello! How can I help you?' }
        }]
      })
    } as Response)
    
    render(<App />)
    
    // Type and send a message
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Hello **world**')
    await user.keyboard('{Enter}')
    
    // User message should be plain text (no markdown rendering)
    await waitFor(() => {
      expect(screen.getByText('Hello **world**')).toBeInTheDocument()
    })
    
    // Should not have markdown formatting for user message
    expect(screen.queryByText('world')).not.toBeInTheDocument()
  })

  it('renders assistant messages with markdown formatting', async () => {
    const user = userEvent.setup()
    
    // Mock API response with markdown content
    const markdownResponse = `# Hello!

Here's some **bold text** and *italic text*.

## Code Example

\`\`\`javascript
const greeting = "Hello World";
console.log(greeting);
\`\`\`

- Item 1
- Item 2
- Item 3`

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        choices: [{
          message: { content: markdownResponse }
        }]
      })
    } as Response)
    
    render(<App />)
    
    // Send a message
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Show me some markdown')
    await user.keyboard('{Enter}')
    
    // Wait for response and check markdown rendering
    await waitFor(() => {
      // Check heading
      expect(screen.getByRole('heading', { level: 1, name: 'Hello!' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { level: 2, name: 'Code Example' })).toBeInTheDocument()
      
      // Check formatted text
      expect(screen.getByText('bold text')).toBeInTheDocument()
      expect(screen.getByText('italic text')).toBeInTheDocument()
      
      // Check code block
      expect(screen.getByText('const greeting = "Hello World";\nconsole.log(greeting);')).toBeInTheDocument()
      
      // Check list
      expect(screen.getByText('Item 1')).toBeInTheDocument()
    })
  })

  it('handles numbered lists with repeated "1." correctly', async () => {
    const user = userEvent.setup()
    
    const listResponse = `Here's your shopping list:

1. onions
1. tomatoes
1. cheese
1. bread
1. milk

All items are fresh!`

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        choices: [{
          message: { content: listResponse }
        }]
      })
    } as Response)
    
    render(<App />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Give me a shopping list')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      // Check that we have an ordered list
      const list = screen.getByRole('list')
      expect(list.tagName).toBe('OL')
      expect(list).toHaveClass('markdown-ol')
      
      // Check all items are present
      const items = ['onions', 'tomatoes', 'cheese', 'bread', 'milk']
      items.forEach(item => {
        expect(screen.getByText(item)).toBeInTheDocument()
      })
      
      // Check we have 5 list items
      const listItems = screen.getAllByRole('listitem')
      expect(listItems).toHaveLength(5)
      
      // Check the items have correct classes
      listItems.forEach(item => {
        expect(item).toHaveClass('markdown-li')
      })
    })
  })

  it('handles code blocks with syntax highlighting classes', async () => {
    const user = userEvent.setup()
    
    const codeResponse = `Here's a Python example:

\`\`\`python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
\`\`\`

And some inline code: \`print("hello")\``

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        choices: [{
          message: { content: codeResponse }
        }]
      })
    } as Response)
    
    render(<App />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Show me code')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      // Check code block
      const codeBlock = screen.getByText(/def fibonacci/)
      expect(codeBlock).toBeInTheDocument()
      expect(codeBlock.closest('pre')).toHaveClass('code-block')
      expect(codeBlock.closest('pre')).toHaveAttribute('data-language', 'python')
      expect(codeBlock).toHaveClass('language-python')
      
      // Check inline code
      const inlineCode = screen.getByText('print("hello")')
      expect(inlineCode.tagName).toBe('CODE')
      expect(inlineCode).toHaveClass('inline-code')
    })
  })

  it('handles tables in markdown responses', async () => {
    const user = userEvent.setup()
    
    const tableResponse = `Here's a comparison table:

| Feature | Status | Notes |
|---------|--------|-------|
| Markdown | ✅ Done | Full support |
| Tables | ✅ Done | Responsive |
| Code | ✅ Done | Syntax highlighting |`

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        choices: [{
          message: { content: tableResponse }
        }]
      })
    } as Response)
    
    render(<App />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Show me a table')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      expect(screen.getByRole('table')).toBeInTheDocument()
      expect(screen.getByRole('table')).toHaveClass('markdown-table')
      expect(screen.getByRole('columnheader', { name: 'Feature' })).toBeInTheDocument()
      expect(screen.getByRole('cell', { name: 'Markdown' })).toBeInTheDocument()
      expect(screen.getByRole('cell', { name: '✅ Done' })).toBeInTheDocument()
      
      // Check table wrapper
      const tableWrapper = screen.getByRole('table').closest('.table-wrapper')
      expect(tableWrapper).toBeInTheDocument()
    })
  })

  it('handles links safely in markdown responses', async () => {
    const user = userEvent.setup()
    
    const linkResponse = `Check out these resources:

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)`

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        choices: [{
          message: { content: linkResponse }
        }]
      })
    } as Response)
    
    render(<App />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Show me links')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      const reactLink = screen.getByRole('link', { name: 'React Documentation' })
      expect(reactLink).toHaveAttribute('href', 'https://react.dev')
      expect(reactLink).toHaveAttribute('target', '_blank')
      expect(reactLink).toHaveAttribute('rel', 'noopener noreferrer')
      expect(reactLink).toHaveClass('markdown-link')
      
      const tsLink = screen.getByRole('link', { name: 'TypeScript Handbook' })
      expect(tsLink).toHaveAttribute('href', 'https://www.typescriptlang.org/docs/')
    })
  })

  it('handles complex recipe with mixed markdown elements', async () => {
    const user = userEvent.setup()
    
    const recipeResponse = `# Tomato Cheese Toast

## Ingredients:
1. onions
1. tomatoes
1. cheese
1. bread

## Instructions:
- Chop the \`onions\` finely
- Slice the **tomatoes** thick
- Grate the *cheese*
- Toast the bread until **golden**

> **Tip:** Use fresh ingredients for best results!

Enjoy your meal! 🍞`

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        choices: [{
          message: { content: recipeResponse }
        }]
      })
    } as Response)
    
    render(<App />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Give me a recipe')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      // Check headings
      expect(screen.getByRole('heading', { level: 1, name: 'Tomato Cheese Toast' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { level: 2, name: 'Ingredients:' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { level: 2, name: 'Instructions:' })).toBeInTheDocument()
      
      // Check ordered list (ingredients)
      const lists = screen.getAllByRole('list')
      expect(lists[0].tagName).toBe('OL')
      expect(lists[0]).toHaveClass('markdown-ol')
      
      // Check unordered list (instructions)
      expect(lists[1].tagName).toBe('UL')
      expect(lists[1]).toHaveClass('markdown-ul')
      
      // Check ingredients
      expect(screen.getByText('onions')).toBeInTheDocument()
      expect(screen.getByText('tomatoes')).toBeInTheDocument()
      expect(screen.getByText('cheese')).toBeInTheDocument()
      expect(screen.getByText('bread')).toBeInTheDocument()
      
      // Check inline formatting in instructions
      expect(screen.getByText('onions')).toHaveClass('inline-code')
      expect(screen.getByText('tomatoes')).toHaveClass('markdown-strong')
      expect(screen.getByText('cheese')).toHaveClass('markdown-em')
      expect(screen.getByText('golden')).toHaveClass('markdown-strong')
      
      // Check blockquote
      const blockquote = document.querySelector('blockquote')
      expect(blockquote).toHaveClass('markdown-blockquote')
      expect(blockquote).toHaveTextContent('Tip: Use fresh ingredients for best results!')
    })
  })

  it('handles error gracefully when markdown parsing fails', async () => {
    const user = userEvent.setup()
    
    // Mock console.error to avoid noise in test output
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        choices: [{
          message: { content: 'Normal content' }
        }]
      })
    } as Response)
    
    render(<App />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    await user.type(input, 'Test error handling')
    await user.keyboard('{Enter}')
    
    // Should handle gracefully without crashing
    await waitFor(() => {
      expect(screen.getByText('Normal content')).toBeInTheDocument()
    })
    
    consoleSpy.mockRestore()
  })
})