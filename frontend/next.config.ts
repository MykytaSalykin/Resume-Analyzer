import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  output: 'standalone',
  devIndicators: false,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
      },
      {
        protocol: 'https',
        hostname: 'farmui.vercel.app',
      },
      {
        protocol: 'https',
        hostname: 'www.launchuicomponents.com',
      },
    ],
  },
};

export default nextConfig;
