// [Task]: T027, T031, T034, T036, T037, T094 [From]: spec.md §FR-003
"use client";

/**
 * Sign in page with email and password fields.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { signInWithEmail } from "@/lib/auth";

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email.trim()) {
      setError("Email is required");
      return;
    }

    if (!password) {
      setError("Password is required");
      return;
    }

    setIsLoading(true);

    try {
      const result = await signInWithEmail(email.trim(), password);

      if (result.success) {
        // Redirect to dashboard after successful sign in
        router.push("/dashboard");
      } else {
        // User-friendly error message for invalid credentials
        setError("Invalid email or password. Please try again.");
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8 bg-background">
      <div className="w-full max-w-md space-y-6 animate-fade-in-up">
        {/* Terminal header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 text-terminal text-xs uppercase tracking-widest">
            <span className="size-2 rounded-full bg-terminal animate-pulse-soft shadow-[0_0_8px_var(--terminal-glow)]" />
            system_access
          </div>
        </div>

        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-center">
              <span className="text-terminal-dim mr-2">&gt;</span>
              auth_login
            </CardTitle>
            <CardDescription className="text-center">
              enter credentials to continue
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              {/* Error message */}
              {error && (
                <div
                  className="rounded-sm bg-destructive/10 border border-destructive/30 p-3 text-xs text-destructive animate-fade-in-up"
                  role="alert"
                >
                  <span className="opacity-70 mr-1">[ERROR]</span> {error}
                </div>
              )}

              {/* Email field */}
              <div className="space-y-2">
                <Label htmlFor="email">email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="user@domain.com"
                  required
                  disabled={isLoading}
                  autoComplete="email"
                />
              </div>

              {/* Password field */}
              <div className="space-y-2">
                <Label htmlFor="password">password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  disabled={isLoading}
                  autoComplete="current-password"
                />
              </div>
            </CardContent>

            <CardFooter className="flex flex-col space-y-4">
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "authenticating..." : "login"}
              </Button>

              <p className="text-center text-xs text-muted-foreground tracking-wide">
                no account?{" "}
                <Link
                  href="/sign-up"
                  className="font-medium text-terminal hover:text-terminal-bright hover:underline transition-colors"
                >
                  register_user
                </Link>
              </p>
            </CardFooter>
          </form>
        </Card>

        {/* Decorative terminal prompt */}
        <div className="text-center text-[10px] text-terminal-dim uppercase tracking-wider">
          <span className="animate-terminal-blink">_</span>
        </div>
      </div>
    </div>
  );
}
