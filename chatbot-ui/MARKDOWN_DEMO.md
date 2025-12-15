# Markdown Support Demo

This file demonstrates the markdown features now supported in the chat interface.

## Text Formatting

You can use **bold text**, *italic text*, and `inline code` in your responses.

## Code Blocks

```javascript
// JavaScript example
function greetUser(name) {
    console.log(`Hello, ${name}!`);
    return `Welcome to the chat, ${name}`;
}

greetUser("Developer");
```

```python
# Python example
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print([fibonacci(i) for i in range(10)])
```

## Lists

### Unordered Lists
- Feature 1: Markdown rendering
- Feature 2: Syntax highlighting
- Feature 3: Responsive design
- Feature 4: Dark/light theme support

### Ordered Lists
1. Install dependencies
2. Create MarkdownRenderer component
3. Update ChatMessage component
4. Add comprehensive styling
5. Test the implementation

## Links

Check out these resources:
- [React Documentation](https://react.dev)
- [Markdown Guide](https://www.markdownguide.org)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## Tables

| Feature | Status | Notes |
|---------|--------|-------|
| Headers | ✅ Done | H1-H6 support |
| Lists | ✅ Done | Ordered & unordered |
| Code | ✅ Done | Inline & blocks |
| Tables | ✅ Done | Responsive design |
| Links | ✅ Done | Safe external links |

## Blockquotes

> **Important Note:** This markdown renderer is specifically designed for chat messages. It includes security features like safe link handling and responsive design for mobile devices.

> You can also have multi-line blockquotes
> that span several lines and maintain
> proper formatting.

## Advanced Features

### Nested Lists
1. Main item 1
   - Sub item 1.1
   - Sub item 1.2
     - Sub sub item 1.2.1
2. Main item 2
   - Sub item 2.1

### Mixed Content
Here's a paragraph with **bold**, *italic*, and `code` elements, followed by a code block:

```bash
# Install the chat application
npm install
npm run dev
```

And then a table:

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run test` | Run test suite |

## Testing the Implementation

To test the markdown rendering:

1. Start the chat application
2. Send a message to the AI assistant
3. Ask for code examples, lists, or formatted content
4. The assistant's response will be rendered with full markdown support
5. User messages remain as plain text for clarity

**Note:** Only assistant messages are rendered as markdown. User messages are displayed as plain text to maintain clarity about what was actually typed.