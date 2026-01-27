// [Task]: T026, T029, T030, T033, T035, T037, T094 [From]: spec.md §FR-001, §FR-002
"use client";

/**
 * Sign up page with email, password, and name fields.
 * Uses zxcvbn for password validation with minimum score of 3.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { PasswordInput, usePasswordValidation } from "@/components/auth/password-input";
import { signUpWithEmail } from "@/lib/auth";

// Email validation regex (RFC 5322 simplified)
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function SignUpPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);

  const { isValid: isPasswordValid } = usePasswordValidation(password, 3);

  const validateEmail = (value: string): boolean => {
    if (!value) {
      setEmailError("Email is required");
      return false;
    }
    if (!EMAIL_REGEX.test(value)) {
      setEmailError("Please enter a valid email address");
      return false;
    }
    setEmailError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate all fields
    if (!name.trim()) {
      setError("Name is required");
      return;
    }

    if (!validateEmail(email)) {
      return;
    }

    if (!isPasswordValid) {
      setError("Please choose a stronger password");
      return;
    }

    setIsLoading(true);

    try {
      const result = await signUpWithEmail(email, password, name.trim());

      if (result.success) {
        // Redirect to dashboard after successful sign up
        router.push("/dashboard");
      } else {
        // Handle specific error messages
        if (result.error?.includes("already exists") || result.error?.includes("duplicate")) {
          setError("An account with this email already exists. Please sign in instead.");
        } else {
          setError(result.error || "Sign up failed. Please try again.");
        }
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
            new_user_registration
          </div>
        </div>

        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-center">
              <span className="text-terminal-dim mr-2">&gt;</span>
              create_account
            </CardTitle>
            <CardDescription className="text-center">
              initialize user profile
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

              {/* Name field */}
              <div className="space-y-2">
                <Label htmlFor="name">username</Label>
                <Input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="your_name"
                  required
                  disabled={isLoading}
                  autoComplete="name"
                />
              </div>

              {/* Email field */}
              <div className="space-y-2">
                <Label htmlFor="email">email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (emailError) validateEmail(e.target.value);
                  }}
                  onBlur={() => validateEmail(email)}
                  placeholder="user@domain.com"
                  required
                  disabled={isLoading}
                  autoComplete="email"
                  className={emailError ? "border-destructive shadow-[0_0_10px_oklch(0.55_0.22_25/30%)]" : ""}
                />
                {emailError && (
                  <p className="text-xs text-destructive animate-fade-in-up" role="alert">
                    <span className="opacity-70">[!]</span> {emailError}
                  </p>
                )}
              </div>

              {/* Password field with strength meter */}
              <PasswordInput
                id="password"
                value={password}
                onChange={setPassword}
                showStrength={true}
                minScore={3}
                label="password"
                placeholder="secure_passphrase"
                disabled={isLoading}
              />
            </CardContent>

            <CardFooter className="flex flex-col space-y-4">
              <Button
                type="submit"
                className="w-full mt-3"
                disabled={isLoading || !isPasswordValid}
              >
                {isLoading ? "initializing..." : "register"}
              </Button>

              <p className="text-center text-xs text-muted-foreground tracking-wide">
                existing user?{" "}
                <Link
                  href="/sign-in"
                  className="font-medium text-terminal hover:text-terminal-bright hover:underline transition-colors"
                >
                  auth_login
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
