import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';

const globalForPrisma = globalThis;

function makePrisma() {
  const adapter = new PrismaPg({
    connectionString: process.env.DATABASE_URL,
    poolConfig: {
      ssl: {
        rejectUnauthorized: false,
      },
    },
  });
  return new PrismaClient({ adapter });
}

export const prisma = globalForPrisma.prisma ?? makePrisma();

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
