// [Task]: T037 [From]: plan.md §Project Structure
/**
 * Chat input component with send button.
 */

"use client";

import { useState, useRef, useEffect, type KeyboardEvent } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = "Type a message...",
  className,
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [message]);

  const handleSend = () => {
    const trimmed = message.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setMessage("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      className={cn(
        "flex items-end gap-3 p-4 border-t border-border/60 bg-card/30",
        className
      )}
    >
      <div className="flex-1 relative">
        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-terminal-dim text-sm pointer-events-none">
          &gt;
        </span>
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className={cn(
            "flex-1 w-full resize-none rounded-sm border border-border/60 bg-input/50 pl-8 pr-4 py-3 text-sm tracking-wide",
            "placeholder:text-terminal-dim placeholder:text-xs placeholder:uppercase placeholder:tracking-wider",
            "focus:outline-none focus:border-terminal focus:bg-input/80 focus:shadow-[0_0_10px_var(--terminal-glow)]",
            "disabled:opacity-40 disabled:cursor-not-allowed",
            "min-h-[48px] max-h-[200px]",
            "transition-all duration-200"
          )}
        />
      </div>
      <Button
        onClick={handleSend}
        disabled={disabled || !message.trim()}
        size="icon"
        className="shrink-0 size-12 rounded-sm"
      >
        <Send className="size-5" />
        <span className="sr-only">Send message</span>
      </Button>
    </div>
  );
}
