// [Task]: T024 [From]: data-model.md, contracts/api-endpoints.md
/**
 * TypeScript types for Task entity and API responses.
 */

/**
 * Task entity as returned from the API.
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Data for creating a new task.
 */
export interface TaskCreate {
  title: string;
  description?: string | null;
}

/**
 * Data for updating an existing task.
 */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
}

/**
 * Response from list tasks endpoint.
 */
export interface TaskListResponse {
  tasks: Task[];
}

/**
 * Simple message response.
 */
export interface MessageResponse {
  message: string;
}

/**
 * API error response.
 */
export interface ApiError {
  detail: string | ValidationError[];
}

/**
 * Validation error detail.
 */
export interface ValidationError {
  loc: string[];
  msg: string;
  type: string;
}
