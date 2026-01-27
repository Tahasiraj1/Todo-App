// [Task]: T035 [From]: plan.md §Project Structure
/**
 * Typing indicator component - shows when AI is processing.
 */

"use client";

import { cn } from "@/lib/utils";

interface TypingIndicatorProps {
  className?: string;
}

export function TypingIndicator({ className }: TypingIndicatorProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-2 px-4 py-3 max-w-[80%] animate-fade-in-up",
        "bg-muted border border-border/60 rounded-sm rounded-bl-none",
        className
      )}
    >
      <span className="text-xs text-terminal-dim uppercase tracking-wider">&gt; processing</span>
      <span className="flex gap-1">
        <span className="size-1.5 rounded-full bg-terminal animate-bounce [animation-delay:-0.3s] shadow-[0_0_5px_var(--terminal-glow)]" />
        <span className="size-1.5 rounded-full bg-terminal animate-bounce [animation-delay:-0.15s] shadow-[0_0_5px_var(--terminal-glow)]" />
        <span className="size-1.5 rounded-full bg-terminal animate-bounce shadow-[0_0_5px_var(--terminal-glow)]" />
      </span>
    </div>
  );
}
