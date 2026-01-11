// [Task]: T018, T025 [From]: plan.md, research.md - Better Auth client configuration
/**
 * Better Auth client for React/Next.js frontend.
 * Uses createAuthClient with JWT plugin for API authentication.
 */

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

// Create the auth client instance with JWT plugin
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  plugins: [jwtClient()],
});

// Export commonly used functions and hooks
export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient;

/**
 * Sign up a new user with email and password.
 */
export async function signUpWithEmail(
  email: string,
  password: string,
  name: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const result = await authClient.signUp.email({
      email,
      password,
      name,
    });

    if (result.error) {
      return {
        success: false,
        error: result.error.message || "Sign up failed"
      };
    }

    return { success: true };
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "An error occurred during sign up";
    return { success: false, error: message };
  }
}

/**
 * Sign in an existing user with email and password.
 */
export async function signInWithEmail(
  email: string,
  password: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const result = await authClient.signIn.email({
      email,
      password,
    });

    if (result.error) {
      return {
        success: false,
        error: result.error.message || "Invalid email or password"
      };
    }

    return { success: true };
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Invalid email or password";
    return { success: false, error: message };
  }
}

/**
 * Sign out the current user.
 */
export async function signOutUser(): Promise<void> {
  try {
    await authClient.signOut();
  } catch {
    // Ignore errors during sign out
  }
}

/**
 * Check if user is authenticated.
 */
export async function isAuthenticated(): Promise<boolean> {
  try {
    const session = await authClient.getSession();
    return !!session.data?.user;
  } catch {
    return false;
  }
}

/**
 * Get a JWT token for API calls to the FastAPI backend.
 * Uses Better Auth's JWT plugin to generate tokens.
 */
export async function getJwtToken(): Promise<string | null> {
  try {
    // Use the JWT client plugin to get a token
    const result = await authClient.token();
    if (result.data?.token) {
      return result.data.token;
    }
    return null;
  } catch {
    return null;
  }
}
