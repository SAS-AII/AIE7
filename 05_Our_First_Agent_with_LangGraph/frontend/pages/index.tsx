import { NextPage } from 'next';
import Head from 'next/head';
import ChatContainer from '@/components/ChatContainer';

const HomePage: NextPage = () => {
  return (
    <>
      <Head>
        <title>Chess Assistant - AI-Powered Chess Analysis</title>
        <meta 
          name="description" 
          content="Get AI-powered analysis of chess players, games, and positions. Upload PGN files or analyze Chess.com players with our intelligent chess assistant." 
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        
        {/* Open Graph / Facebook */}
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://chess-assistant.vercel.app/" />
        <meta property="og:title" content="Chess Assistant - AI-Powered Chess Analysis" />
        <meta property="og:description" content="Get AI-powered analysis of chess players, games, and positions. Upload PGN files or analyze Chess.com players with our intelligent chess assistant." />
        <meta property="og:image" content="https://chess-assistant.vercel.app/chess-hero.svg" />
        
        {/* Twitter */}
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:url" content="https://chess-assistant.vercel.app/" />
        <meta property="twitter:title" content="Chess Assistant - AI-Powered Chess Analysis" />
        <meta property="twitter:description" content="Get AI-powered analysis of chess players, games, and positions. Upload PGN files or analyze Chess.com players with our intelligent chess assistant." />
        <meta property="twitter:image" content="https://chess-assistant.vercel.app/chess-hero.svg" />
        
        {/* Additional SEO */}
        <meta name="robots" content="index, follow" />
        <meta name="language" content="English" />
        <meta name="revisit-after" content="7 days" />
        <meta name="author" content="Chess Assistant" />
        <meta name="keywords" content="chess, ai, analysis, chess.com, pgn, chess assistant, game analysis, player stats" />
        
        {/* Preload critical resources */}
        <link rel="preload" href="/chess-hero.svg" as="image" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </Head>
      
      <ChatContainer />
    </>
  );
};

export default HomePage; 