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
    <div className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">
            Create an account
          </CardTitle>
          <CardDescription className="text-center">
            Enter your details to get started
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {/* Error message */}
            {error && (
              <div
                className="rounded-md bg-red-50 p-3 text-sm text-red-600"
                role="alert"
              >
                {error}
              </div>
            )}

            {/* Name field */}
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                required
                disabled={isLoading}
                autoComplete="name"
              />
            </div>

            {/* Email field */}
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (emailError) validateEmail(e.target.value);
                }}
                onBlur={() => validateEmail(email)}
                placeholder="Enter your email"
                required
                disabled={isLoading}
                autoComplete="email"
                className={emailError ? "border-red-500" : ""}
              />
              {emailError && (
                <p className="text-xs text-red-600" role="alert">
                  {emailError}
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
              label="Password"
              placeholder="Choose a strong password"
              disabled={isLoading}
            />
          </CardContent>

          <CardFooter className="flex flex-col space-y-4">
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading || !isPasswordValid}
            >
              {isLoading ? "Creating account..." : "Create account"}
            </Button>

            <p className="text-center text-sm text-gray-600">
              Already have an account?{" "}
              <Link
                href="/sign-in"
                className="font-medium text-primary hover:underline"
              >
                Sign in
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
