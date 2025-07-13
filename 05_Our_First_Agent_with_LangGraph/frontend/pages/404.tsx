import { NextPage } from 'next';
import Head from 'next/head';
import Link from 'next/link';
import { HomeIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

const NotFoundPage: NextPage = () => {
  return (
    <>
      <Head>
        <title>404 - Page Not Found | Chess Assistant</title>
        <meta name="description" content="The page you're looking for doesn't exist." />
        <meta name="robots" content="noindex, nofollow" />
      </Head>
      
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="text-center">
          {/* Chess-themed 404 illustration */}
          <div className="mb-8 relative">
            <div className="text-9xl font-bold text-chess-accent/20 select-none">
              404
            </div>
            
            {/* Fallen chess pieces */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="flex items-center gap-4 text-chess-dark/60">
                {/* Fallen king */}
                <svg width="40" height="40" viewBox="0 0 40 40" fill="currentColor" className="transform rotate-45">
                  <path d="M10 30 L30 30 L27.5 7.5 L25 7.5 L25 2.5 L22.5 2.5 L22.5 0 L17.5 0 L17.5 2.5 L15 2.5 L15 7.5 L12.5 7.5 L10 30 Z" />
                  <circle cx="20" cy="4" r="1.5" />
                </svg>
                
                {/* Fallen queen */}
                <svg width="35" height="35" viewBox="0 0 35 35" fill="currentColor" className="transform -rotate-30">
                  <path d="M7.5 30 L32.5 30 L30 7.5 L27.5 10 L25 5 L22.5 12.5 L20 2.5 L17.5 12.5 L15 5 L12.5 10 L10 7.5 L7.5 30 Z" />
                </svg>
                
                {/* Fallen rook */}
                <svg width="30" height="30" viewBox="0 0 30 30" fill="currentColor" className="transform rotate-12">
                  <path d="M10 30 L30 30 L27.5 10 L25 10 L25 5 L22.5 5 L22.5 10 L20 10 L20 5 L17.5 5 L17.5 10 L15 10 L15 5 L12.5 5 L12.5 10 L10 10 L10 30 Z" />
                </svg>
              </div>
            </div>
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Checkmate!
          </h1>
          
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-md mx-auto">
            The page you're looking for seems to have been captured. 
            Let's get you back to the game.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/"
              className="inline-flex items-center gap-2 px-6 py-3 bg-chess-accent text-white rounded-lg hover:bg-chess-accent/90 transition-colors font-medium"
            >
              <HomeIcon className="w-5 h-5" />
              Back to Home
            </Link>
            
            <button
              onClick={() => window.history.back()}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors font-medium"
            >
              <ArrowLeftIcon className="w-5 h-5" />
              Go Back
            </button>
          </div>
          
          {/* Chess board pattern decoration */}
          <div className="mt-12 flex justify-center">
            <div className="grid grid-cols-8 gap-0 w-32 h-32 opacity-20">
              {Array.from({ length: 64 }).map((_, i) => {
                const row = Math.floor(i / 8);
                const col = i % 8;
                const isLight = (row + col) % 2 === 0;
                
                return (
                  <div
                    key={i}
                    className={`aspect-square ${
                      isLight ? 'bg-chess-light' : 'bg-chess-dark'
                    }`}
                  />
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default NotFoundPage; 