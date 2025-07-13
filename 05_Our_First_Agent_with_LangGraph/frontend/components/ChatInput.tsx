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
  onPlayerAnalysis: (username: string) => void;
  onPGNAnalysis: (pgn: string) => void;
  onRecentGamesAnalysis: (username: string, limit?: number) => void;
  onFileUpload: (file: File) => void;
  onStop: () => void;
  isLoading?: boolean;
  isStreaming?: boolean;
  disabled?: boolean;
  className?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onPlayerAnalysis,
  onPGNAnalysis,
  onRecentGamesAnalysis,
  onFileUpload,
  onStop,
  isLoading = false,
  isStreaming = false,
  disabled = false,
  className
}) => {
  const [input, setInput] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [analysisType, setAnalysisType] = useState<'player' | 'pgn' | 'recent'>('player');
  const [recentGamesLimit, setRecentGamesLimit] = useState(5);
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
        if (file.type === 'image/png') {
          setUploadedFile(file);
        } else if (file.name.endsWith('.pgn')) {
          // Read PGN file content
          const reader = new FileReader();
          reader.onload = (e) => {
            const content = e.target?.result as string;
            setInput(content);
            setAnalysisType('pgn');
          };
          reader.readAsText(file);
        }
      }
    }, []),
  });

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    
    if (!hasRequiredKeys()) {
      toast.error('Please configure your API keys in settings');
      return;
    }

    if (uploadedFile) {
      onFileUpload(uploadedFile);
      setUploadedFile(null);
      return;
    }

    if (!input.trim()) return;

    const trimmedInput = input.trim();
    
    // Detect analysis type based on input
    if (analysisType === 'player') {
      onPlayerAnalysis(trimmedInput);
    } else if (analysisType === 'pgn') {
      onPGNAnalysis(trimmedInput);
    } else if (analysisType === 'recent') {
      onRecentGamesAnalysis(trimmedInput, recentGamesLimit);
    }
    
    setInput('');
    setUploadedFile(null);
  }, [
    input, 
    uploadedFile, 
    analysisType, 
    recentGamesLimit, 
    onPlayerAnalysis, 
    onPGNAnalysis, 
    onRecentGamesAnalysis, 
    onFileUpload,
    hasRequiredKeys
  ]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'image/png') {
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
        {/* Analysis type selector */}
        <div className="flex gap-2 mb-3">
          <button
            type="button"
            onClick={() => setAnalysisType('player')}
            className={clsx(
              'px-3 py-1 text-sm rounded-md font-medium transition-colors',
              analysisType === 'player'
                ? 'bg-chess-accent text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            )}
          >
            Player Analysis
          </button>
          <button
            type="button"
            onClick={() => setAnalysisType('pgn')}
            className={clsx(
              'px-3 py-1 text-sm rounded-md font-medium transition-colors',
              analysisType === 'pgn'
                ? 'bg-chess-accent text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            )}
          >
            PGN Analysis
          </button>
          <button
            type="button"
            onClick={() => setAnalysisType('recent')}
            className={clsx(
              'px-3 py-1 text-sm rounded-md font-medium transition-colors',
              analysisType === 'recent'
                ? 'bg-chess-accent text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            )}
          >
            Recent Games
          </button>
          {analysisType === 'recent' && (
            <select
              value={recentGamesLimit}
              onChange={(e) => setRecentGamesLimit(Number(e.target.value))}
              className="px-2 py-1 text-sm rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
            >
              <option value={3}>3 games</option>
              <option value={5}>5 games</option>
              <option value={10}>10 games</option>
            </select>
          )}
        </div>

        {/* File upload area */}
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
              {isDragActive 
                ? 'Drop files here...' 
                : 'Drag & drop PNG images or PGN files, or click to select'
              }
            </span>
          </div>
        </div>

        {/* Uploaded file preview */}
        {uploadedFile && (
          <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <PhotoIcon className="w-5 h-5 text-chess-accent" />
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {uploadedFile.name}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  ({(uploadedFile.size / 1024).toFixed(1)} KB)
                </span>
              </div>
              <button
                type="button"
                onClick={removeFile}
                className="text-gray-400 hover:text-red-500 transition-colors"
                aria-label="Remove file"
              >
                <XMarkIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Input form */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                analysisType === 'player' 
                  ? 'Enter Chess.com username to analyze...'
                  : analysisType === 'pgn'
                  ? 'Paste PGN content here...'
                  : 'Enter username for recent games analysis...'
              }
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-chess-accent focus:border-chess-accent resize-none"
              rows={uploadedFile ? 1 : 3}
              disabled={isDisabled}
            />
          </div>
          
          <div className="flex flex-col gap-2">
            {/* File upload button */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".png"
              onChange={handleFileSelect}
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isDisabled}
              className="p-2 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-chess-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Upload PNG file"
            >
              <PhotoIcon className="w-5 h-5" />
            </button>
            
            {/* Submit/Stop button */}
            {isStreaming ? (
              <button
                type="button"
                onClick={onStop}
                className="p-2 bg-red-500 text-white rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 transition-colors"
                aria-label="Stop generation"
              >
                <StopIcon className="w-5 h-5" />
              </button>
            ) : (
              <button
                type="submit"
                disabled={isDisabled || (!input.trim() && !uploadedFile)}
                className="p-2 bg-chess-accent text-white rounded-md hover:bg-chess-accent/90 focus:outline-none focus:ring-2 focus:ring-chess-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                aria-label="Send message"
              >
                <PaperAirplaneIcon className="w-5 h-5" />
              </button>
            )}
          </div>
        </form>
        
        {/* Status message */}
        {!hasRequiredKeys() && (
          <div className="mt-2 text-sm text-amber-600 dark:text-amber-400">
            Please configure your API keys in settings to use the chat
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInput; 