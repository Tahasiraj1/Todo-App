// [Task]: T028, T022 [From]: spec.md §FR-005, research.md §Password Validation
"use client";

/**
 * Password input component with zxcvbn validation.
 * Requires minimum password score of 3 (strong).
 */

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import zxcvbn from "zxcvbn";

interface PasswordInputProps {
  id: string;
  value: string;
  onChange: (value: string) => void;
  showStrength?: boolean;
  minScore?: number;
  label?: string;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
}

const strengthLabels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"];
const strengthColors = [
  "bg-red-500",
  "bg-orange-500",
  "bg-yellow-500",
  "bg-green-500",
  "bg-green-600",
];

export function PasswordInput({
  id,
  value,
  onChange,
  showStrength = true,
  minScore = 3,
  label = "Password",
  placeholder = "Enter password",
  disabled = false,
  required = true,
}: PasswordInputProps) {
  const [score, setScore] = useState<number>(0);
  const [feedback, setFeedback] = useState<string>("");
  const [isValid, setIsValid] = useState<boolean>(false);

  useEffect(() => {
    if (value) {
      const result = zxcvbn(value);
      setScore(result.score);
      setIsValid(result.score >= minScore);

      // Get feedback for weak passwords
      if (result.score < minScore) {
        const suggestions = result.feedback.suggestions.join(" ");
        const warning = result.feedback.warning;
        setFeedback(warning || suggestions || "Password is too weak");
      } else {
        setFeedback("");
      }
    } else {
      setScore(0);
      setIsValid(false);
      setFeedback("");
    }
  }, [value, minScore]);

  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        type="password"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        className={
          value && !isValid ? "border-red-500 focus-visible:ring-red-500" : ""
        }
        aria-describedby={showStrength ? `${id}-strength` : undefined}
      />

      {showStrength && value && (
        <div id={`${id}-strength`} className="space-y-1">
          {/* Strength meter */}
          <div className="flex gap-1">
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className={`h-1 flex-1 rounded ${
                  i <= score ? strengthColors[score] : "bg-gray-200"
                }`}
              />
            ))}
          </div>

          {/* Strength label */}
          <div className="flex justify-between text-xs">
            <span
              className={`${
                isValid ? "text-green-600" : "text-red-600"
              } font-medium`}
            >
              {strengthLabels[score]}
            </span>
            {!isValid && <span className="text-gray-500">Minimum: Strong</span>}
          </div>

          {/* Feedback for improvement */}
          {feedback && (
            <p className="text-xs text-red-600" role="alert">
              {feedback}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Hook to validate password strength.
 */
export function usePasswordValidation(
  password: string,
  minScore: number = 3
): { isValid: boolean; score: number; feedback: string } {
  const [validation, setValidation] = useState({
    isValid: false,
    score: 0,
    feedback: "",
  });

  useEffect(() => {
    if (password) {
      const result = zxcvbn(password);
      const isValid = result.score >= minScore;
      setValidation({
        isValid,
        score: result.score,
        feedback: isValid
          ? ""
          : result.feedback.warning ||
            result.feedback.suggestions.join(" ") ||
            "Password is too weak",
      });
    } else {
      setValidation({ isValid: false, score: 0, feedback: "" });
    }
  }, [password, minScore]);

  return validation;
}
