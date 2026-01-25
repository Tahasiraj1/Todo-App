// [Task]: T034 [From]: plan.md, contracts/chat-api.md
/**
 * Chat API client for AI chatbot functionality.
 * Handles chat messages and conversation management.
 */

import { getJwtToken, signOut, getSession } from "./auth";
import { ApiClientError } from "./api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ============================================================================
// Type Definitions
// ============================================================================

export interface ToolCall {
  tool: string;
  parameters: Record<string, unknown>;
  result?: Record<string, unknown> | unknown[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: ToolCall[];
}

export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ConversationSummary {
  id: number;
  user_id: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface ConversationResponse {
  id: number;
  user_id: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get the current user's ID from the session.
 */
async function getCurrentUserId(): Promise<string> {
  const session = await getSession();
  if (!session.data?.user?.id) {
    throw new Error("User not authenticated");
  }
  return session.data.user.id;
}

/**
 * Make an authenticated API request.
 */
async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getJwtToken();

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    await signOut();
    if (typeof window !== "undefined") {
      window.location.href = "/sign-in";
    }
    throw new ApiClientError(401, "Session expired. Please sign in again.");
  }

  if (!response.ok) {
    let errorDetail: string | unknown[];
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail;
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new ApiClientError(response.status, errorDetail);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}

// ============================================================================
// Chat API Functions
// ============================================================================

/**
 * Send a message to the AI assistant.
 * POST /api/{user_id}/chat
 */
export async function sendMessage(
  message: string,
  conversationId?: number
): Promise<ChatResponse> {
  const userId = await getCurrentUserId();
  const request: ChatRequest = {
    message,
    conversation_id: conversationId,
  };

  return fetchWithAuth<ChatResponse>(`/api/${userId}/chat`, {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * List all conversations for the authenticated user.
 * GET /api/{user_id}/conversations
 */
export async function getConversations(
  limit = 50,
  offset = 0
): Promise<ConversationSummary[]> {
  const userId = await getCurrentUserId();
  return fetchWithAuth<ConversationSummary[]>(
    `/api/${userId}/conversations?limit=${limit}&offset=${offset}`
  );
}

/**
 * Get a specific conversation with all messages.
 * GET /api/{user_id}/conversations/{conversationId}
 */
export async function getConversation(
  conversationId: number
): Promise<ConversationResponse> {
  const userId = await getCurrentUserId();
  return fetchWithAuth<ConversationResponse>(
    `/api/${userId}/conversations/${conversationId}`
  );
}

/**
 * Delete a conversation.
 * DELETE /api/{user_id}/conversations/{conversationId}
 */
export async function deleteConversation(
  conversationId: number
): Promise<{ message: string }> {
  const userId = await getCurrentUserId();
  return fetchWithAuth<{ message: string }>(
    `/api/${userId}/conversations/${conversationId}`,
    {
      method: "DELETE",
    }
  );
}
