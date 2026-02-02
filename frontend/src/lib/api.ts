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
    credentials: "include",
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
 * Query parameters for listing tasks with filtering, sorting, and search.
 */
export interface ListTasksParams {
  status?: string;
  priority?: string;
  tag?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
  overdue?: boolean;
}

/**
 * List tasks for the authenticated user with optional filtering, sorting, and search.
 * GET /api/{user_id}/tasks
 */
export async function listTasks(params?: ListTasksParams): Promise<Task[]> {
  const userId = await getCurrentUserId();
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== "" && value !== null) {
        searchParams.set(key, String(value));
      }
    });
  }
  const query = searchParams.toString();
  const url = `/api/${userId}/tasks${query ? `?${query}` : ""}`;
  const response = await fetchWithAuth<TaskListResponse>(url);
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

// ============================================================================
// Activity Log API Functions (Phase V)
// ============================================================================

export interface ActivityEntry {
  id: number;
  user_id: string;
  task_id: number;
  event_type: string;
  task_title: string;
  task_data: Record<string, unknown>;
  created_at: string;
}

export interface ActivityResponse {
  entries: ActivityEntry[];
  total: number;
}

/**
 * Get activity log entries for a user.
 * GET /api/{user_id}/activity
 */
export async function getActivity(
  userId?: string,
  limit: number = 20,
  offset: number = 0
): Promise<ActivityResponse> {
  const uid = userId || (await getCurrentUserId());
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  return fetchWithAuth<ActivityResponse>(`/api/${uid}/activity?${params}`);
}
