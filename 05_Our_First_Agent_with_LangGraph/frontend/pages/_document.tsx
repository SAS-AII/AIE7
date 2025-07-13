import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        {/* Preload fonts */}
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500&display=swap"
          rel="stylesheet"
        />
        
        {/* Theme color */}
        <meta name="theme-color" content="#3c79e6" />
        
        {/* Apple touch icon */}
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        
        {/* Manifest */}
        <link rel="manifest" href="/manifest.json" />
        
        {/* Prevent flash of unstyled content */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
                var storedTheme = localStorage.getItem('darkMode');
                
                if (storedTheme === 'true' || (storedTheme === null && prefersDark)) {
                  document.documentElement.classList.add('dark');
                }
              })()
            `,
          }}
        />
      </Head>
      <body className="antialiased">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
} 