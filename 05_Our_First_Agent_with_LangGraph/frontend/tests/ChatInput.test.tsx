import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SettingsProvider } from '@/contexts/SettingsContext';
import ChatInput from '@/components/ChatInput';

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  toast: {
    error: jest.fn(),
    success: jest.fn(),
  },
}));

// Mock react-dropzone
jest.mock('react-dropzone', () => ({
  useDropzone: () => ({
    getRootProps: () => ({ 'data-testid': 'dropzone' }),
    getInputProps: () => ({ 'data-testid': 'file-input' }),
    isDragActive: false,
  }),
}));

const mockProps = {
  onPlayerAnalysis: jest.fn(),
  onPGNAnalysis: jest.fn(),
  onRecentGamesAnalysis: jest.fn(),
  onFileUpload: jest.fn(),
  onStop: jest.fn(),
  isLoading: false,
  isStreaming: false,
  disabled: false,
};

const renderWithProvider = (ui: React.ReactElement) => {
  return render(
    <SettingsProvider>
      {ui}
    </SettingsProvider>
  );
};

describe('ChatInput', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn((key) => {
          if (key === 'openaiKey') return 'test-openai-key';
          if (key === 'tavilyKey') return 'test-tavily-key';
          return null;
        }),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      },
      writable: true,
    });
  });

  it('renders with player analysis mode by default', () => {
    renderWithProvider(<ChatInput {...mockProps} />);
    
    expect(screen.getByText('Player Analysis')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter Chess.com username to analyze...')).toBeInTheDocument();
  });

  it('switches between analysis modes', () => {
    renderWithProvider(<ChatInput {...mockProps} />);
    
    // Switch to PGN analysis
    fireEvent.click(screen.getByText('PGN Analysis'));
    expect(screen.getByPlaceholderText('Paste PGN content here...')).toBeInTheDocument();
    
    // Switch to recent games analysis
    fireEvent.click(screen.getByText('Recent Games'));
    expect(screen.getByPlaceholderText('Enter username for recent games analysis...')).toBeInTheDocument();
  });

  it('calls onPlayerAnalysis when submitting in player mode', async () => {
    renderWithProvider(<ChatInput {...mockProps} />);
    
    const input = screen.getByPlaceholderText('Enter Chess.com username to analyze...');
    const submitButton = screen.getByLabelText('Send message');
    
    fireEvent.change(input, { target: { value: 'testuser' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockProps.onPlayerAnalysis).toHaveBeenCalledWith('testuser');
    });
  });

  it('calls onPGNAnalysis when submitting in PGN mode', async () => {
    renderWithProvider(<ChatInput {...mockProps} />);
    
    // Switch to PGN mode
    fireEvent.click(screen.getByText('PGN Analysis'));
    
    const input = screen.getByPlaceholderText('Paste PGN content here...');
    const submitButton = screen.getByLabelText('Send message');
    
    fireEvent.change(input, { target: { value: '1. e4 e5 2. Nf3 Nc6' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockProps.onPGNAnalysis).toHaveBeenCalledWith('1. e4 e5 2. Nf3 Nc6');
    });
  });

  it('calls onRecentGamesAnalysis when submitting in recent games mode', async () => {
    renderWithProvider(<ChatInput {...mockProps} />);
    
    // Switch to recent games mode
    fireEvent.click(screen.getByText('Recent Games'));
    
    const input = screen.getByPlaceholderText('Enter username for recent games analysis...');
    const submitButton = screen.getByLabelText('Send message');
    
    fireEvent.change(input, { target: { value: 'testuser' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockProps.onRecentGamesAnalysis).toHaveBeenCalledWith('testuser', 5);
    });
  });

  it('submits with Enter key', async () => {
    renderWithProvider(<ChatInput {...mockProps} />);
    
    const input = screen.getByPlaceholderText('Enter Chess.com username to analyze...');
    
    fireEvent.change(input, { target: { value: 'testuser' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    
    await waitFor(() => {
      expect(mockProps.onPlayerAnalysis).toHaveBeenCalledWith('testuser');
    });
  });

  it('does not submit with Shift+Enter', async () => {
    renderWithProvider(<ChatInput {...mockProps} />);
    
    const input = screen.getByPlaceholderText('Enter Chess.com username to analyze...');
    
    fireEvent.change(input, { target: { value: 'testuser' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', shiftKey: true });
    
    await waitFor(() => {
      expect(mockProps.onPlayerAnalysis).not.toHaveBeenCalled();
    });
  });

  it('shows stop button when streaming', () => {
    renderWithProvider(<ChatInput {...mockProps} isStreaming={true} />);
    
    expect(screen.getByLabelText('Stop generation')).toBeInTheDocument();
  });

  it('calls onStop when stop button is clicked', () => {
    renderWithProvider(<ChatInput {...mockProps} isStreaming={true} />);
    
    const stopButton = screen.getByLabelText('Stop generation');
    fireEvent.click(stopButton);
    
    expect(mockProps.onStop).toHaveBeenCalled();
  });

  it('disables input when disabled prop is true', () => {
    renderWithProvider(<ChatInput {...mockProps} disabled={true} />);
    
    const input = screen.getByPlaceholderText('Enter Chess.com username to analyze...');
    const submitButton = screen.getByLabelText('Send message');
    
    expect(input).toBeDisabled();
    expect(submitButton).toBeDisabled();
  });

  it('clears input after submission', async () => {
    renderWithProvider(<ChatInput {...mockProps} />);
    
    const input = screen.getByPlaceholderText('Enter Chess.com username to analyze...');
    const submitButton = screen.getByLabelText('Send message');
    
    fireEvent.change(input, { target: { value: 'testuser' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(input).toHaveValue('');
    });
  });
}); 