// [Task]: T038 [From]: plan.md §Project Structure
/**
 * Main chat interface component - combines message list and input.
 */

"use client";

import { useState, useCallback, useEffect } from "react";
import { MessageList } from "./message-list";
import { ChatInput } from "./chat-input";
import {
  sendMessage,
  getConversation,
  type ChatMessage,
  type ChatResponse,
} from "@/lib/chat-api";
import { cn } from "@/lib/utils";

interface ChatInterfaceProps {
  conversationId?: number;
  onConversationCreated?: (id: number) => void;
  className?: string;
}

export function ChatInterface({
  conversationId: initialConversationId,
  onConversationCreated,
  className,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<number | undefined>(
    initialConversationId
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load existing conversation messages
  useEffect(() => {
    async function loadConversation() {
      if (!conversationId) return;

      try {
        setIsLoading(true);
        const conversation = await getConversation(conversationId);
        setMessages(conversation.messages);
      } catch (err) {
        console.error("Failed to load conversation:", err);
        setError("Failed to load conversation history");
      } finally {
        setIsLoading(false);
      }
    }

    loadConversation();
  }, [conversationId]);

  const handleSendMessage = useCallback(
    async (messageText: string) => {
      // Create optimistic user message
      const optimisticMessage: ChatMessage = {
        id: Date.now(), // Temporary ID
        role: "user",
        content: messageText,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, optimisticMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const response: ChatResponse = await sendMessage(
          messageText,
          conversationId
        );

        // Update conversation ID if new conversation was created
        if (!conversationId && response.conversation_id) {
          setConversationId(response.conversation_id);
          onConversationCreated?.(response.conversation_id);
        }

        // Add assistant response
        const assistantMessage: ChatMessage = {
          id: Date.now() + 1, // Temporary ID
          role: "assistant",
          content: response.response,
          created_at: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        console.error("Failed to send message:", err);
        setError("Failed to send message. Please try again.");
        // Remove optimistic message on error
        setMessages((prev) =>
          prev.filter((m) => m.id !== optimisticMessage.id)
        );
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId, onConversationCreated]
  );

  return (
    <div className={cn("flex flex-col h-full", className)}>
      {error && (
        <div className="px-4 py-2 bg-destructive/10 text-destructive text-sm text-center">
          {error}
        </div>
      )}

      <MessageList messages={messages} isLoading={isLoading} />

      <ChatInput
        onSend={handleSendMessage}
        disabled={isLoading}
        placeholder="Ask me to add tasks, show your list, or manage todos..."
      />
    </div>
  );
}
