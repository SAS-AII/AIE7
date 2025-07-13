import React, { useState, useRef, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import clsx from 'clsx';
import { 
  PaperAirplaneIcon, 
  PhotoIcon, 
  XMarkIcon,
  StopIcon
} from '@heroicons/react/24/outline';
import { useSettings } from '@/contexts/SettingsContext';
import { toast } from 'react-hot-toast';

interface ChatInputProps {
  onSendMessage: (message: string, file?: File) => void;
  onStop: () => void;
  isLoading?: boolean;
  isStreaming?: boolean;
  disabled?: boolean;
  className?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onStop,
  isLoading = false,
  isStreaming = false,
  disabled = false,
  className
}) => {
  const [input, setInput] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { hasRequiredKeys } = useSettings();

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/png': ['.png'],
      'text/plain': ['.pgn'],
    },
    multiple: false,
    onDrop: useCallback((acceptedFiles) => {
      const file = acceptedFiles[0];
      if (file) {
        setUploadedFile(file);
      }
    }, []),
  });

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (!hasRequiredKeys()) {
      toast.error('Please configure your API keys in settings');
      return;
    }
    if (!input.trim() && !uploadedFile) return;
    onSendMessage(input.trim(), uploadedFile || undefined);
    setInput('');
    setUploadedFile(null);
  }, [input, uploadedFile, onSendMessage, hasRequiredKeys]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
    }
  }, []);

  const removeFile = useCallback(() => {
    setUploadedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  const isDisabled = disabled || isLoading || !hasRequiredKeys();

  return (
    <div className={clsx('border-t bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700', className)}>
      <div className="max-w-chat mx-auto px-4 py-4">
        {/* File upload area (optional) */}
        <div
          {...getRootProps()}
          className={clsx(
            'border-2 border-dashed rounded-lg p-4 mb-4 transition-colors cursor-pointer',
            isDragActive 
              ? 'border-chess-accent bg-chess-accent/10' 
              : 'border-gray-300 dark:border-gray-600 hover:border-chess-accent hover:bg-chess-accent/5'
          )}
        >
          <input {...getInputProps()} />
          <div className="flex items-center justify-center gap-2 text-gray-500 dark:text-gray-400">
            <PhotoIcon className="w-5 h-5" />
            <span className="text-sm">
              Drag & drop PNG images or PGN files, or click to select
            </span>
          </div>
        </div>
        {/* Uploaded file preview */}
        {uploadedFile && (
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm text-gray-700 dark:text-gray-300">{uploadedFile.name}</span>
            <button onClick={removeFile} className="text-gray-400 hover:text-red-500">
              <XMarkIcon className="w-4 h-4" />
            </button>
          </div>
        )}
        {/* Chat input */}
        <form onSubmit={handleSubmit} className="flex items-end gap-2">
          <textarea
            ref={textareaRef}
            className="flex-1 resize-none rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-chess-accent"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={isDisabled}
            aria-label="Chat message input"
          />
          <button
            type="submit"
            className="p-2 bg-chess-accent text-white rounded-md hover:bg-chess-accent/90 transition-colors disabled:opacity-50"
            disabled={isDisabled}
            aria-label="Send message"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
          {isStreaming && (
            <button
              type="button"
              onClick={onStop}
              className="p-2 text-gray-400 hover:text-red-500"
              aria-label="Stop streaming"
            >
              <StopIcon className="w-5 h-5" />
            </button>
          )}
        </form>
      </div>
    </div>
  );
};

export default ChatInput; 