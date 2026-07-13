const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ['@prisma/client', 'prisma'],
  env: {
    AUTH_PASSWORD: process.env.AUTH_PASSWORD,
  },
};

module.exports = nextConfig;
