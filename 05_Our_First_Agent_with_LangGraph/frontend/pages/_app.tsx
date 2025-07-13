import type { AppProps } from 'next/app';
import { Inter } from 'next/font/google';
import { Toaster } from 'react-hot-toast';
import { SettingsProvider } from '@/contexts/SettingsContext';
import ChessThemeWrapper from '@/components/ChessThemeWrapper';
import '@/styles/globals.css';
import 'katex/dist/katex.min.css';
import 'highlight.js/styles/github.css';

const inter = Inter({ subsets: ['latin'] });

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className={inter.className}>
      <SettingsProvider>
        <ChessThemeWrapper>
          <Component {...pageProps} />
          <Toaster
            position="top-center"
            toastOptions={{
              duration: 4000,
              style: {
                background: 'var(--toast-bg)',
                color: 'var(--toast-color)',
                border: '1px solid var(--toast-border)',
              },
              success: {
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#ffffff',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#ffffff',
                },
              },
            }}
          />
        </ChessThemeWrapper>
      </SettingsProvider>
      
      <style jsx global>{`
        :root {
          --toast-bg: #ffffff;
          --toast-color: #374151;
          --toast-border: #e5e7eb;
        }
        
        .dark {
          --toast-bg: #1f2937;
          --toast-color: #f3f4f6;
          --toast-border: #4b5563;
        }
      `}</style>
    </div>
  );
} 