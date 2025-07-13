/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['127.0.0.1', 'localhost'],
  },
  async rewrites() {
    // Only rewrite for local development - in production, Vercel handles routing
    if (process.env.NODE_ENV === 'development') {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
      return [
        {
          source: '/api/:path*',
          destination: `${apiUrl}/api/:path*`,
        },
      ];
    }
    return [];
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value:
              "default-src 'self'; " +
              "img-src 'self' data: blob:; " +
              "media-src 'self' data: blob:; " +
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob:; " +
              "style-src 'self' 'unsafe-inline' blob:; " +
              "connect-src 'self' http://127.0.0.1:8000 https://*.vercel.app ws://localhost:*;",
          },
        ],
      },
    ];
  },
  // Enable webpack 5 features
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
    };
    return config;
  },
};

module.exports = nextConfig; 