// [Task]: T039 [From]: plan.md §Project Structure
"use client";

/**
 * Chat page for AI-powered task management.
 * Protected route requiring authentication.
 */

import { useState, useEffect } from "react";
import Link from "next/link";
import { MessageSquare, ArrowLeft, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChatInterface } from "@/components/chat/chat-interface";
import { SignOutButton } from "@/components/auth/sign-out-button";
import {
  getConversations,
  deleteConversation,
  type ConversationSummary,
} from "@/lib/chat-api";

export default function ChatPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<
    number | undefined
  >();
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setIsLoadingConversations(true);
      const convos = await getConversations();
      setConversations(convos);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const handleNewConversation = () => {
    setSelectedConversationId(undefined);
  };

  const handleConversationCreated = (id: number) => {
    // Reload conversations to include the new one
    loadConversations();
    setSelectedConversationId(id);
  };

  const handleDeleteConversation = async (id: number) => {
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (selectedConversationId === id) {
        setSelectedConversationId(undefined);
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="border-b bg-white shrink-0">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="size-4" />
              <span className="hidden sm:inline">Dashboard</span>
            </Link>
            <h1 className="text-xl font-bold text-gray-900 sm:text-2xl flex items-center gap-2">
              <MessageSquare className="size-6" />
              AI Chat
            </h1>
          </div>
          <SignOutButton />
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex mx-auto max-w-6xl w-full overflow-hidden">
        {/* Sidebar - Conversation list */}
        <aside className="w-64 border-r bg-white shrink-0 hidden md:flex flex-col">
          <div className="p-4 border-b">
            <Button
              onClick={handleNewConversation}
              className="w-full"
              variant="outline"
            >
              New Conversation
            </Button>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {isLoadingConversations ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground text-sm">
                Loading...
              </div>
            ) : conversations.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground text-sm">
                No conversations yet
              </div>
            ) : (
              <ul className="space-y-1">
                {conversations.map((convo) => (
                  <li key={convo.id}>
                    <button
                      onClick={() => setSelectedConversationId(convo.id)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center justify-between group transition-colors ${
                        selectedConversationId === convo.id
                          ? "bg-primary/10 text-primary"
                          : "hover:bg-gray-100"
                      }`}
                    >
                      <span className="truncate">
                        Conversation #{convo.id}
                        {convo.message_count !== undefined && (
                          <span className="text-xs text-muted-foreground ml-1">
                            ({convo.message_count})
                          </span>
                        )}
                      </span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteConversation(convo.id);
                        }}
                        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded transition-opacity"
                        title="Delete conversation"
                      >
                        <Trash2 className="size-3 text-destructive" />
                      </button>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </aside>

        {/* Main chat area */}
        <main className="flex-1 flex flex-col bg-white overflow-hidden">
          <ChatInterface
            key={selectedConversationId ?? "new"}
            conversationId={selectedConversationId}
            onConversationCreated={handleConversationCreated}
            className="h-full"
          />
        </main>
      </div>
    </div>
  );
}
