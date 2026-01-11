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

export const auth = betterAuth({
  database: pool,
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3001",
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
