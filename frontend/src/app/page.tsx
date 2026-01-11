// [Task]: T093 [From]: spec.md
/**
 * Home page - redirects to dashboard or sign-in based on auth state.
 */

import { redirect } from "next/navigation";
import { cookies } from "next/headers";

export default async function Home() {
  // Check for auth token
  const cookieStore = await cookies();
  const token =
    cookieStore.get("better-auth.session_token")?.value ||
    cookieStore.get("auth_token")?.value;

  if (token) {
    redirect("/dashboard");
  } else {
    redirect("/sign-in");
  }
}
