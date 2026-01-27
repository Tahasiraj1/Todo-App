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

const strengthLabels = ["critical", "weak", "moderate", "secure", "fortified"];
const strengthColors = [
  "bg-destructive",
  "bg-orange-500",
  "bg-yellow-500",
  "bg-terminal",
  "bg-terminal-bright",
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
          value && !isValid ? "border-destructive shadow-[0_0_10px_oklch(0.55_0.22_25/30%)]" : ""
        }
        aria-describedby={showStrength ? `${id}-strength` : undefined}
      />

      {showStrength && value && (
        <div id={`${id}-strength`} className="space-y-2 animate-fade-in-up">
          {/* Strength meter */}
          <div className="flex gap-1">
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className={`h-1.5 flex-1 rounded-sm transition-all duration-300 ${
                  i <= score
                    ? `${strengthColors[score]} ${score >= 3 ? 'shadow-[0_0_8px_var(--terminal-glow)]' : ''}`
                    : "bg-muted"
                }`}
              />
            ))}
          </div>

          {/* Strength label */}
          <div className="flex justify-between text-[10px] uppercase tracking-wider">
            <span
              className={`font-medium ${
                isValid ? "text-terminal" : "text-destructive"
              }`}
            >
              [{strengthLabels[score]}]
            </span>
            {!isValid && <span className="text-terminal-dim">min: secure</span>}
          </div>

          {/* Feedback for improvement */}
          {feedback && (
            <p className="text-xs text-destructive/80" role="alert">
              <span className="opacity-70">[hint]</span> {feedback}
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
