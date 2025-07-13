import React from 'react';
import { render, screen } from '@testing-library/react';
import ChatMessage from '@/components/ChatMessage';
import { ChatMessage as ChatMessageType } from '@/utils/api';

// Mock react-markdown
jest.mock('react-markdown', () => {
  return function ReactMarkdown({ children }: { children: string }) {
    return <div data-testid="markdown-content">{children}</div>;
  };
});

// Mock markdown plugins
jest.mock('@/utils/markdownPlugins', () => ({
  defaultMarkdownConfig: {
    remarkPlugins: [],
    rehypePlugins: [],
    components: {},
  },
}));

describe('ChatMessage', () => {
  const mockUserMessage: ChatMessageType = {
    role: 'user',
    content: 'Hello, analyze this chess player',
    timestamp: 1234567890000,
  };

  const mockAssistantMessage: ChatMessageType = {
    role: 'assistant',
    content: 'Here is the analysis of the chess player...',
    timestamp: 1234567890000,
  };

  it('renders user message correctly', () => {
    render(<ChatMessage message={mockUserMessage} />);
    
    expect(screen.getByText('You')).toBeInTheDocument();
    expect(screen.getByTestId('markdown-content')).toHaveTextContent(
      'Hello, analyze this chess player'
    );
  });

  it('renders assistant message correctly', () => {
    render(<ChatMessage message={mockAssistantMessage} />);
    
    expect(screen.getByText('Chess Assistant')).toBeInTheDocument();
    expect(screen.getByTestId('markdown-content')).toHaveTextContent(
      'Here is the analysis of the chess player...'
    );
  });

  it('displays timestamp when provided', () => {
    render(<ChatMessage message={mockUserMessage} />);
    
    const timestamp = new Date(mockUserMessage.timestamp!).toLocaleTimeString();
    expect(screen.getByText(timestamp)).toBeInTheDocument();
  });

  it('shows loading dots when message is empty and streaming', () => {
    const emptyMessage: ChatMessageType = {
      role: 'assistant',
      content: '',
    };
    
    render(<ChatMessage message={emptyMessage} isStreaming={true} />);
    
    expect(screen.getByText('Thinking...')).toBeInTheDocument();
  });

  it('shows "No response" when message is empty and not streaming', () => {
    const emptyMessage: ChatMessageType = {
      role: 'assistant',
      content: '',
    };
    
    render(<ChatMessage message={emptyMessage} isStreaming={false} />);
    
    expect(screen.getByText('No response')).toBeInTheDocument();
  });

  it('shows streaming indicator when streaming and has content', () => {
    render(<ChatMessage message={mockAssistantMessage} isStreaming={true} />);
    
    // Should show content and streaming indicator
    expect(screen.getByTestId('markdown-content')).toHaveTextContent(
      'Here is the analysis of the chess player...'
    );
    
    // Look for streaming indicator (pulse animation)
    const streamingIndicator = screen.getByTestId('markdown-content')
      .parentElement?.querySelector('[class*="animate-pulse"]');
    expect(streamingIndicator).toBeInTheDocument();
  });

  it('applies correct styling for user messages', () => {
    render(<ChatMessage message={mockUserMessage} />);
    
    const messageContainer = screen.getByText('You').closest('div');
    expect(messageContainer).toHaveClass('bg-transparent');
  });

  it('applies correct styling for assistant messages', () => {
    render(<ChatMessage message={mockAssistantMessage} />);
    
    const messageContainer = screen.getByText('Chess Assistant').closest('div');
    expect(messageContainer).toHaveClass('bg-gray-50');
  });

  it('handles whitespace-only content correctly', () => {
    const whitespaceMessage: ChatMessageType = {
      role: 'assistant',
      content: '   \n   ',
    };
    
    render(<ChatMessage message={whitespaceMessage} />);
    
    expect(screen.getByText('No response')).toBeInTheDocument();
  });

  it('applies custom className when provided', () => {
    const { container } = render(
      <ChatMessage message={mockUserMessage} className="custom-class" />
    );
    
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('renders markdown content through ReactMarkdown', () => {
    const markdownMessage: ChatMessageType = {
      role: 'assistant',
      content: '# Header\n\nThis is **bold** text.',
    };
    
    render(<ChatMessage message={markdownMessage} />);
    
    expect(screen.getByTestId('markdown-content')).toHaveTextContent(
      '# Header\n\nThis is **bold** text.'
    );
  });
}); 