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
        "flex items-center gap-1 px-4 py-3 max-w-[80%]",
        "bg-muted rounded-2xl rounded-bl-sm",
        className
      )}
    >
      <span className="text-sm text-muted-foreground mr-2">AI is thinking</span>
      <span className="flex gap-1">
        <span className="size-2 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:-0.3s]" />
        <span className="size-2 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:-0.15s]" />
        <span className="size-2 rounded-full bg-muted-foreground/60 animate-bounce" />
      </span>
    </div>
  );
}
