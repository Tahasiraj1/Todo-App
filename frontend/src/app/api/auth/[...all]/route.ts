// [Task]: T025 [From]: plan.md - Better Auth API route handler
/**
 * Better Auth API route handler for Next.js.
 * Handles all authentication requests at /api/auth/*
 */

import { auth } from "@/lib/auth-server";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth.handler);
