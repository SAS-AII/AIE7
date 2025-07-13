# Chess Assistant Frontend

A responsive, chess-themed ChatGPT-style frontend built with Next.js that connects to the FastAPI LangGraph backend for AI-powered chess analysis.

## Features

- 🎨 **Chess-themed Design**: Beautiful, responsive UI with chess piece animations and board patterns
- 💬 **ChatGPT-style Interface**: Familiar chat experience with streaming responses
- 📊 **Multiple Analysis Types**: Player analysis, PGN game analysis, and recent games review
- 📸 **PNG Upload Support**: Upload chess position images for analysis
- 🌙 **Dark Mode**: Toggle between light and dark themes
- 🔧 **Settings Modal**: Secure API key management with localStorage
- 📱 **Fully Responsive**: Works seamlessly on mobile, tablet, and desktop
- ⚡ **Real-time Streaming**: Live streaming of AI responses with auto-scroll
- 🎯 **Accessibility**: ARIA labels, keyboard navigation, and high contrast support
- 🧪 **Testing**: Comprehensive test suite with Jest and React Testing Library

## Tech Stack

- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom chess theme
- **UI Components**: Headless UI, Heroicons
- **Markdown**: ReactMarkdown with syntax highlighting, math support, and GitHub-flavored markdown
- **File Upload**: React Dropzone for PNG/PGN file handling
- **State Management**: React Context + custom hooks
- **Testing**: Jest, React Testing Library
- **Deployment**: Vercel (optimized with standalone output)

## Quick Start

### Prerequisites

- Node.js 18+ and npm/pnpm/yarn
- Backend API running on `http://127.0.0.1:8000` (or configured via `NEXT_PUBLIC_API_URL`)

### Installation

```bash
# Clone the repository
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Start development server
npm run dev
```

### Environment Variables

Create a `.env.local` file in the frontend directory:

```bash
# API URL (defaults to http://127.0.0.1:8000)
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# Optional: Custom domain for production
NEXT_PUBLIC_DOMAIN=https://your-domain.com
```

## API Keys Configuration

The app requires API keys to function. Configure them through the settings modal (⚙️ icon) in the app:

### Required Keys:
- **OpenAI API Key**: For LLM analysis (`sk-...`)
- **Tavily API Key**: For web search (`tvly-...`)

### Optional Keys:
- **LangSmith API Key**: For tracing and monitoring (`ls__...`)
- **Qdrant API Key**: For vector storage (`qdrant-...`)
- **Qdrant URL**: Vector database endpoint

## Usage

### Player Analysis
1. Select "Player Analysis" mode
2. Enter a Chess.com username
3. Get comprehensive player statistics and insights

### PGN Game Analysis
1. Select "PGN Analysis" mode
2. Paste PGN game notation or drag & drop a .pgn file
3. Receive detailed game analysis with move-by-move breakdown

### Recent Games Analysis
1. Select "Recent Games" mode
2. Enter a Chess.com username
3. Choose number of games to analyze (3, 5, or 10)
4. Get pattern analysis across multiple games

### PNG Upload
1. Drag & drop PNG images of chess positions
2. Or click the photo icon to select files
3. Get AI-powered position analysis

## Project Structure

```
frontend/
├── components/           # React components
│   ├── ChatContainer.tsx    # Main chat interface
│   ├── ChatMessage.tsx      # Individual message rendering
│   ├── ChatInput.tsx        # Input with file upload
│   ├── SettingsModal.tsx    # API key management
│   ├── LoadingDots.tsx      # Loading animation
│   └── ChessThemeWrapper.tsx # Global theme provider
├── contexts/
│   └── SettingsContext.tsx  # Settings state management
├── hooks/
│   ├── useChatStream.ts     # Chat streaming logic
│   └── useAutoScroll.ts     # Auto-scroll functionality
├── pages/
│   ├── _app.tsx            # App wrapper with providers
│   ├── index.tsx           # Main chat page
│   ├── _document.tsx       # Document configuration
│   └── 404.tsx             # Custom 404 page
├── styles/
│   └── globals.css         # Global styles and chess theme
├── utils/
│   ├── api.ts              # API client functions
│   └── markdownPlugins.ts  # Markdown configuration
└── tests/                  # Test files
```

## Development

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server

# Quality Assurance
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript compiler
npm test             # Run tests
npm run test:watch   # Run tests in watch mode
```

### Code Quality

The project uses:
- **ESLint**: Code linting with Next.js configuration
- **Prettier**: Code formatting with Tailwind CSS plugin
- **TypeScript**: Strict type checking
- **Jest**: Unit testing framework
- **React Testing Library**: Component testing utilities

### Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm test -- --coverage
```

## Deployment

### Vercel (Recommended)

1. Connect your repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

The app is optimized for Vercel with:
- Standalone output mode
- Optimized bundle size
- Edge-compatible configuration

### Manual Deployment

```bash
# Build the application
npm run build

# The built files will be in the .next directory
# Deploy the .next directory to your hosting provider
```

## Configuration

### Tailwind CSS Theme

The chess theme is configured in `tailwind.config.js`:

```javascript
colors: {
  chess: {
    light: '#f0d9b5',    // Light chess squares
    dark: '#b58863',     // Dark chess squares
    accent: '#3c79e6',   // Primary accent color
    board: '#769656',    // Board background
  }
}
```

### Markdown Support

Includes support for:
- GitHub Flavored Markdown (GFM)
- Mathematical expressions (KaTeX)
- Syntax highlighting (highlight.js)
- Tables, lists, and blockquotes
- Emoji support
- Line breaks

### Accessibility Features

- ARIA labels for all interactive elements
- Keyboard navigation support
- High contrast mode compatibility
- Screen reader optimizations
- Focus management for modals
- Semantic HTML structure

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues or questions:
1. Check the GitHub issues page
2. Review the API documentation
3. Check the backend connectivity
4. Ensure all required API keys are configured

## Performance Optimizations

- Next.js Image component for optimized images
- Code splitting and lazy loading
- Streaming responses for better UX
- Efficient re-renders with React.memo
- Debounced scroll events
- Optimized bundle size with tree shaking 