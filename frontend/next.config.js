/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // Standalone output for optimized Docker images
  output: 'standalone',

  images: {
    domains: ['localhost'],
  },

  // Optimize for production
  compress: true,
  poweredByHeader: false,

  // Production-ready settings
  productionBrowserSourceMaps: false,
}

module.exports = nextConfig
