# Chatbot UI

A modern React-based chat interface for the FastAPI RAG Application. This frontend provides a clean, intuitive chat experience that seamlessly integrates with the backend's RAG-enhanced AI assistant.

## Features

- **Clean Chat Interface**: Modern, responsive design with user and assistant message bubbles
- **Real-time Conversations**: Multi-turn conversations with full context preservation
- **Loading States**: Visual feedback during API calls with typing indicators
- **Error Handling**: Graceful error handling with retry functionality
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark/Light Theme**: Automatic theme switching based on system preferences
- **Accessibility**: Full keyboard navigation and screen reader support
- **RAG Transparency**: Users benefit from enhanced responses without seeing technical complexity

## Technology Stack

- **React 19.2.0** with TypeScript
- **Vite** for fast development and building
- **Vitest** for unit and integration testing
- **React Testing Library** for component testing
- **CSS Variables** for theming and customization

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm, yarn, or pnpm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm run test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Build for production
npm run build
```

## Project Structure

```
src/
├── components/           # React components
│   ├── ChatContainer.tsx    # Main chat container
│   ├── ChatHistory.tsx      # Message history display
│   ├── ChatInput.tsx        # Input field and send button
│   └── ChatMessage.tsx      # Individual message component
├── services/            # API services
│   └── chatApi.ts          # Chat API integration
├── types/               # TypeScript type definitions
│   └── chat.ts             # Chat-related types
├── __mocks__/           # Test mocks and utilities
│   └── chatApiMocks.ts     # Mock data for testing
├── App.tsx              # Main application component
├── App.css              # Application styles
├── index.css            # Global styles and CSS variables
└── setupTests.ts        # Test configuration
```

## API Integration

The frontend integrates with the FastAPI backend using the `/chat/advanced` endpoint:

- **Endpoint**: `POST http://localhost:8000/chat/advanced`
- **Features**: Multi-turn conversations, RAG enhancement (transparent to user)
- **Error Handling**: Comprehensive error handling for all API failure scenarios

### RAG Transparency

The application receives RAG-enhanced responses from the backend but keeps this functionality completely transparent to the user:

- Users see natural, enhanced responses without knowing about document retrieval
- No RAG metadata is displayed in the UI
- The experience feels like chatting with a knowledgeable assistant

## Component Architecture

### ChatContainer
- Main orchestrator component
- Manages conversation state and API calls
- Handles error states and loading indicators

### ChatHistory
- Displays conversation messages
- Auto-scrolls to latest messages
- Shows loading indicators during API calls

### ChatInput
- Text input with send button
- Handles Enter key and button click events
- Validates and trims user input

### ChatMessage
- Individual message display
- Role-based styling (user vs assistant)
- Timestamp display
- System messages are filtered out

## Testing

Comprehensive test suite covering:

- **Unit Tests**: Individual component functionality
- **Integration Tests**: Complete conversation flows
- **API Tests**: Service layer with mocked responses
- **Accessibility Tests**: Keyboard navigation and screen readers
- **Error Scenarios**: Network failures and API errors

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage report
npm run test:coverage

# Run tests with UI interface
npm run test:ui
```

## Styling and Theming

- **CSS Variables**: Easy customization of colors and spacing
- **Responsive Design**: Mobile-first approach with breakpoints
- **Dark/Light Theme**: Automatic switching based on system preference
- **Modern UI**: Clean, minimalist design with smooth animations

### Customization

Modify CSS variables in `src/index.css` to customize the appearance:

```css
:root {
  --primary-color: #0d6efd;
  --user-message-bg: #0d6efd;
  --assistant-message-bg: #f8f9fa;
  /* ... more variables */
}
```

## Accessibility

- Full keyboard navigation support
- Screen reader compatible
- High contrast color schemes
- Focus indicators for interactive elements
- Semantic HTML structure

## Performance

- Optimized React rendering with proper key props
- Efficient state management
- Lazy loading and code splitting ready
- Minimal bundle size with tree shaking

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style and patterns
2. Write tests for new features
3. Ensure accessibility compliance
4. Test on multiple devices and browsers
5. Update documentation as needed

## License

This project is part of the FastAPI RAG Application suite.