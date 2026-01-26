// [Task]: T018, T025 [From]: plan.md, research.md - Better Auth server configuration
/**
 * Better Auth server configuration with PostgreSQL database.
 * This file is used on the server side (API routes, server components).
 */

import { betterAuth } from "better-auth";
import { Pool } from "pg";
import { nextCookies } from "better-auth/next-js";
import { jwt } from "better-auth/plugins";

// Database connection for Better Auth
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Get the base URL for Better Auth
// In production (Vercel), use VERCEL_URL or set BETTER_AUTH_URL
// In development, use localhost
const getBaseURL = (): string => {
  // Production URL from environment variable
  if (process.env.BETTER_AUTH_URL) {
    return process.env.BETTER_AUTH_URL;
  }
  // Vercel provides VERCEL_URL - use it if available
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}`;
  }
  // Fallback to NEXT_PUBLIC_BETTER_AUTH_URL or localhost
  return process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000";
};

export const auth = betterAuth({
  database: pool,
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: getBaseURL(),
  trustedOrigins: [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://todo-app-coral-two-71.vercel.app",
    process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "",
  ].filter(Boolean),
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day - update session every day
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },
  user: {
    additionalFields: {
      name: {
        type: "string",
        required: false,
      },
    },
  },
  plugins: [
    jwt({
      jwt: {
        expirationTime: "1h", // JWT expires in 1 hour
      },
    }),
    nextCookies(), // Must be last
  ],
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
