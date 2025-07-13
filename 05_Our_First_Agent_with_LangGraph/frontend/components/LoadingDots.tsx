import React from 'react';
import clsx from 'clsx';

interface LoadingDotsProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const LoadingDots: React.FC<LoadingDotsProps> = ({ 
  size = 'md',
  className 
}) => {
  const sizeClasses = {
    sm: 'w-1 h-1',
    md: 'w-2 h-2',
    lg: 'w-3 h-3',
  };

  const containerClasses = {
    sm: 'space-x-1',
    md: 'space-x-1.5',
    lg: 'space-x-2',
  };

  return (
    <div 
      className={clsx(
        'flex items-center justify-center',
        containerClasses[size],
        className
      )}
      role="status"
      aria-label="Loading"
    >
      <div 
        className={clsx(
          'rounded-full bg-chess-accent animate-bounce',
          sizeClasses[size]
        )}
        style={{ animationDelay: '0ms' }}
      />
      <div 
        className={clsx(
          'rounded-full bg-chess-accent animate-bounce',
          sizeClasses[size]
        )}
        style={{ animationDelay: '150ms' }}
      />
      <div 
        className={clsx(
          'rounded-full bg-chess-accent animate-bounce',
          sizeClasses[size]
        )}
        style={{ animationDelay: '300ms' }}
      />
    </div>
  );
};

export default LoadingDots; 