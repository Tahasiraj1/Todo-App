// [Task]: T036 [From]: plan.md §Project Structure
/**
 * Message list component - displays chat messages with user/assistant styling.
 */

"use client";

import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import type { ChatMessage } from "@/lib/chat-api";
import { TypingIndicator } from "./typing-indicator";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  className?: string;
}

export function MessageList({
  messages,
  isLoading = false,
  className,
}: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div
      className={cn(
        "flex-1 overflow-y-auto p-4 space-y-4",
        className
      )}
    >
      {messages.length === 0 && !isLoading && (
        <div className="flex flex-col items-center justify-center h-full text-center animate-fade-in-up">
          <div className="relative mb-4">
            <div className="text-4xl opacity-50">_</div>
            <div className="absolute inset-0 blur-xl bg-terminal/20" />
          </div>
          <h3 className="text-sm font-semibold text-terminal uppercase tracking-wider mb-2">
            <span className="text-terminal-dim">[</span>
            awaiting_input
            <span className="text-terminal-dim">]</span>
          </h3>
          <p className="text-xs text-muted-foreground max-w-sm tracking-wide">
            manage tasks via natural language commands.
            create, list, complete, or delete tasks.
          </p>
        </div>
      )}

      {messages.map((message, index) => (
        <MessageBubble key={message.id} message={message} index={index} />
      ))}

      {isLoading && <TypingIndicator />}

      <div ref={bottomRef} />
    </div>
  );
}

interface MessageBubbleProps {
  message: ChatMessage;
  index?: number;
}

function MessageBubble({ message, index = 0 }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex animate-fade-in-up",
        isUser ? "justify-end" : "justify-start"
      )}
      style={{ animationDelay: `${index * 0.05}s` }}
    >
      <div
        className={cn(
          "px-4 py-3 max-w-[80%] rounded-sm whitespace-pre-wrap text-sm tracking-wide transition-all duration-200",
          isUser
            ? "bg-terminal text-background rounded-br-none shadow-[0_0_15px_var(--terminal-glow)]"
            : "bg-muted border border-border/60 text-foreground rounded-bl-none"
        )}
      >
        {!isUser && <span className="text-terminal-dim text-xs mr-2">&gt;</span>}
        {message.content}
      </div>
    </div>
  );
}
