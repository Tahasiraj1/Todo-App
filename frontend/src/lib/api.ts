// [Task]: T019, T048, T049, T062, T072, T081, T097, T098 [From]: plan.md, research.md
/**
 * API client utility with JWT token attachment and error handling.
 * Centralized API calls for all backend endpoints.
 * Endpoint pattern: /api/{user_id}/tasks (per hackathon requirements)
 */

import type {
  Task,
  TaskCreate,
  TaskListResponse,
  TaskUpdate,
  MessageResponse,
  ApiError,
} from "@/types/task";
import { getJwtToken, signOut, getSession } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Get the current user's ID from the session.
 * Required for building API endpoint URLs.
 */
async function getCurrentUserId(): Promise<string> {
  const session = await getSession();
  if (!session.data?.user?.id) {
    throw new Error("User not authenticated");
  }
  return session.data.user.id;
}

/**
 * Custom error class for API errors.
 */
export class ApiClientError extends Error {
  public status: number;
  public detail: string | unknown[];

  constructor(status: number, detail: string | unknown[]) {
    super(typeof detail === "string" ? detail : "API Error");
    this.status = status;
    this.detail = detail;
    this.name = "ApiClientError";
  }
}

/**
 * Make an authenticated API request.
 * Gets JWT token from Better Auth and attaches it to requests.
 */
async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Get JWT token from Better Auth
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

  // Handle 401 Unauthorized - session expired
  if (response.status === 401) {
    // Sign out and redirect to sign-in
    await signOut();
    if (typeof window !== "undefined") {
      window.location.href = "/sign-in";
    }
    throw new ApiClientError(401, "Session expired. Please sign in again.");
  }

  // Handle non-OK responses
  if (!response.ok) {
    let errorDetail: string | unknown[];
    try {
      const errorData = (await response.json()) as ApiError;
      errorDetail = errorData.detail;
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new ApiClientError(response.status, errorDetail);
  }

  // Handle empty responses (204 No Content)
  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}

// ============================================================================
// Task API Functions
// Endpoint pattern: /api/{user_id}/tasks (per hackathon requirements)
// ============================================================================

/**
 * List all tasks for the authenticated user.
 * GET /api/{user_id}/tasks
 */
export async function listTasks(): Promise<Task[]> {
  const userId = await getCurrentUserId();
  const response = await fetchWithAuth<TaskListResponse>(`/api/${userId}/tasks`);
  return response.tasks;
}

/**
 * Get a specific task by ID.
 * GET /api/{user_id}/tasks/{taskId}
 */
export async function getTask(taskId: number): Promise<Task> {
  const userId = await getCurrentUserId();
  return fetchWithAuth<Task>(`/api/${userId}/tasks/${taskId}`);
}

/**
 * Create a new task.
 * POST /api/{user_id}/tasks
 */
export async function createTask(data: TaskCreate): Promise<Task> {
  const userId = await getCurrentUserId();
  return fetchWithAuth<Task>(`/api/${userId}/tasks`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Update an existing task.
 * PUT /api/{user_id}/tasks/{taskId}
 */
export async function updateTask(
  taskId: number,
  data: TaskUpdate
): Promise<Task> {
  const userId = await getCurrentUserId();
  return fetchWithAuth<Task>(`/api/${userId}/tasks/${taskId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * Delete a task.
 * DELETE /api/{user_id}/tasks/{taskId}
 */
export async function deleteTask(taskId: number): Promise<MessageResponse> {
  const userId = await getCurrentUserId();
  return fetchWithAuth<MessageResponse>(`/api/${userId}/tasks/${taskId}`, {
    method: "DELETE",
  });
}

/**
 * Toggle task completion status.
 * PATCH /api/{user_id}/tasks/{taskId}/complete
 */
export async function toggleTaskCompletion(taskId: number): Promise<Task> {
  const userId = await getCurrentUserId();
  return fetchWithAuth<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
    method: "PATCH",
  });
}
