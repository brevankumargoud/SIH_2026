/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      { source: '/login', destination: '/' },
      { source: '/forgot-password', destination: '/' },
      { source: '/dashboard', destination: '/' },
      { source: '/chat', destination: '/' },
      { source: '/documents', destination: '/' },
      { source: '/knowledge-base', destination: '/' },
      { source: '/vision', destination: '/' },
      { source: '/agents', destination: '/' },
      { source: '/models', destination: '/' },
      { source: '/reports', destination: '/' },
      { source: '/audit', destination: '/' },
      { source: '/admin', destination: '/' },
      { source: '/settings', destination: '/' },
    ];
  },
}

export default nextConfig
