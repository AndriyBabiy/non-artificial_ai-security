/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${
          process.env.BACKEND_URL || "http://localhost:8000"
        }/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
