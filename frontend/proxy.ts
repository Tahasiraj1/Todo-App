// [Task]: T038 [From]: spec.md §FR-019
/**
 * Next.js middleware for protected route authentication.
 * Redirects unauthenticated users to sign-in page.
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Routes that require authentication
const protectedRoutes = ["/dashboard"];

// Routes that are only for unauthenticated users
const authRoutes = ["/sign-in", "/sign-up"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check for auth token in cookies
  // Better Auth stores session in cookies - default cookie name is "session_token"
  // Check multiple possible cookie names for compatibility
  const sessionToken =
    request.cookies.get("session_token")?.value ||
    request.cookies.get("__better-auth.session_token")?.value ||
    request.cookies.get("better-auth.session_token")?.value ||
    request.cookies.get("auth_token")?.value;

  const isAuthenticated = !!sessionToken;

  // Check if accessing a protected route
  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  );

  // Check if accessing an auth route (sign-in, sign-up)
  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route));

  // Redirect unauthenticated users from protected routes to sign-in
  if (isProtectedRoute && !isAuthenticated) {
    const signInUrl = new URL("/sign-in", request.url);
    signInUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(signInUrl);
  }

  // Redirect authenticated users from auth routes to dashboard
  if (isAuthRoute && isAuthenticated) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     * - api routes (Better Auth handles its own auth)
     */
    "/((?!_next/static|_next/image|favicon.ico|api).*)",
  ],
};
