import React, { useEffect, useState } from 'react';
import Image from 'next/image';
import { useSettings } from '@/contexts/SettingsContext';
import { checkHealth } from '@/utils/api';
import clsx from 'clsx';

interface ChessThemeWrapperProps {
  children: React.ReactNode;
  className?: string;
}

const ChessThemeWrapper: React.FC<ChessThemeWrapperProps> = ({ 
  children, 
  className 
}) => {
  const { darkMode } = useSettings();
  const [isBackendConnected, setIsBackendConnected] = useState<boolean | null>(null);

  // Check backend health on mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        await checkHealth();
        setIsBackendConnected(true);
      } catch (error) {
        setIsBackendConnected(false);
      }
    };

    checkBackendHealth();
    
    // Check health every 30 seconds
    const interval = setInterval(checkBackendHealth, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={clsx(
      'min-h-screen relative transition-colors duration-300',
      darkMode 
        ? 'bg-gray-900 text-white' 
        : 'bg-gray-50 text-gray-900',
      className
    )}>
      {/* Background pattern */}
      <div className="absolute inset-0 chess-background" />
      
      {/* Hero background SVG */}
      <div className="absolute inset-0 opacity-20">
        <div className="w-full h-full bg-gradient-to-br from-chess-light/30 to-chess-dark/30">
          {/* Chess piece silhouettes */}
          <svg 
            className="absolute inset-0 w-full h-full"
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
          >
            <defs>
              <pattern id="chessPattern" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse">
                <rect width="4" height="4" fill="rgba(240, 217, 181, 0.1)" />
                <rect x="4" y="4" width="4" height="4" fill="rgba(240, 217, 181, 0.1)" />
                <rect x="4" y="0" width="4" height="4" fill="rgba(181, 136, 99, 0.1)" />
                <rect x="0" y="4" width="4" height="4" fill="rgba(181, 136, 99, 0.1)" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#chessPattern)" />
          </svg>
        </div>
      </div>
      
      {/* Connection status indicator */}
      <div className="absolute top-4 right-4 z-10">
        <div className={clsx(
          'flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium backdrop-blur-sm',
          isBackendConnected === true 
            ? 'bg-green-500/20 text-green-700 dark:text-green-400 border border-green-500/30'
            : isBackendConnected === false
            ? 'bg-red-500/20 text-red-700 dark:text-red-400 border border-red-500/30'
            : 'bg-gray-500/20 text-gray-700 dark:text-gray-400 border border-gray-500/30'
        )}>
          <div className={clsx(
            'w-2 h-2 rounded-full',
            isBackendConnected === true 
              ? 'bg-green-500 animate-pulse'
              : isBackendConnected === false
              ? 'bg-red-500'
              : 'bg-gray-500 animate-pulse'
          )} />
          <span>
            {isBackendConnected === true 
              ? 'Connected'
              : isBackendConnected === false
              ? 'Disconnected'
              : 'Connecting...'
            }
          </span>
        </div>
      </div>
      
      {/* Main content */}
      <div className="relative z-10">
        {children}
      </div>
      
      {/* Decorative chess pieces (visible only on larger screens) */}
      <div className="hidden lg:block absolute inset-0 pointer-events-none">
        {/* King silhouette */}
        <div className="absolute top-1/4 left-1/4 opacity-5">
          <svg width="80" height="80" viewBox="0 0 80 80" fill="currentColor">
            <path d="M20 60 L60 60 L55 15 L50 15 L50 5 L45 5 L45 0 L35 0 L35 5 L30 5 L30 15 L25 15 L20 60 Z" />
            <circle cx="40" cy="8" r="3" />
            <rect x="37" y="2" width="6" height="8" />
            <rect x="35" y="4" width="10" height="4" />
          </svg>
        </div>
        
        {/* Queen silhouette */}
        <div className="absolute top-1/3 right-1/4 opacity-5">
          <svg width="70" height="70" viewBox="0 0 70 70" fill="currentColor">
            <path d="M15 60 L65 60 L60 15 L55 20 L50 10 L45 25 L40 5 L35 25 L30 10 L25 20 L20 15 L15 60 Z" />
            <circle cx="28" cy="15" r="2" />
            <circle cx="40" cy="8" r="3" />
            <circle cx="52" cy="15" r="2" />
          </svg>
        </div>
        
        {/* Rook silhouette */}
        <div className="absolute bottom-1/4 left-1/3 opacity-5">
          <svg width="60" height="60" viewBox="0 0 60 60" fill="currentColor">
            <path d="M20 60 L60 60 L55 20 L50 20 L50 10 L45 10 L45 20 L40 20 L40 10 L35 10 L35 20 L30 20 L30 10 L25 10 L25 20 L20 20 L20 60 Z" />
          </svg>
        </div>
        
        {/* Bishop silhouette */}
        <div className="absolute bottom-1/3 right-1/3 opacity-5">
          <svg width="50" height="50" viewBox="0 0 50 50" fill="currentColor">
            <path d="M25 60 L55 60 L50 15 L45 25 L40 5 L35 25 L30 15 L25 60 Z" />
            <circle cx="40" cy="8" r="4" />
            <path d="M36 8 L44 8 L42 12 L38 12 Z" />
          </svg>
        </div>
        
        {/* Knight silhouette */}
        <div className="absolute top-1/2 left-1/6 opacity-5">
          <svg width="55" height="55" viewBox="0 0 55 55" fill="currentColor">
            <path d="M25 60 L55 60 L50 25 L45 30 L40 20 L35 15 L30 20 L25 30 L25 60 Z" />
            <path d="M30 20 Q35 10 45 15 Q50 20 45 30 L40 25 L35 30 Z" />
          </svg>
        </div>
        
        {/* Pawns */}
        <div className="absolute bottom-1/6 left-1/2 opacity-5">
          <svg width="40" height="40" viewBox="0 0 40 40" fill="currentColor">
            <path d="M30 60 L50 60 L45 25 L35 25 L30 60 Z" />
            <circle cx="40" cy="20" r="8" />
          </svg>
        </div>
      </div>
    </div>
  );
};

export default ChessThemeWrapper; 