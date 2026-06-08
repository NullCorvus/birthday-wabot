const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ['@prisma/client', 'prisma'],
};

module.exports = nextConfig;
