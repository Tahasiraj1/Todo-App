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
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="text-4xl mb-4">💬</div>
          <h3 className="text-lg font-semibold text-foreground mb-2">
            Start a conversation
          </h3>
          <p className="text-sm text-muted-foreground max-w-sm">
            Ask me to add tasks, show your task list, mark tasks complete, or
            help manage your todos in any way.
          </p>
        </div>
      )}

      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isLoading && <TypingIndicator />}

      <div ref={bottomRef} />
    </div>
  );
}

interface MessageBubbleProps {
  message: ChatMessage;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "px-4 py-3 max-w-[80%] rounded-2xl whitespace-pre-wrap",
          isUser
            ? "bg-primary text-primary-foreground rounded-br-sm"
            : "bg-muted text-foreground rounded-bl-sm"
        )}
      >
        {message.content}
      </div>
    </div>
  );
}
