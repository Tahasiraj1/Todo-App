// [Task]: T024, T012 [From]: data-model.md, contracts/api-endpoints.md
/**
 * TypeScript types for Task entity and API responses.
 * Phase V extensions: priority, tags, due_date, recurrence fields.
 */

export type TaskPriority = "high" | "medium" | "low";
export type RecurrenceFrequency = "daily" | "weekly" | "monthly";

/**
 * Task entity as returned from the API.
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: TaskPriority;
  tags: string[];
  due_date: string | null;
  is_overdue: boolean;
  is_recurring: boolean;
  recurrence_frequency: RecurrenceFrequency | null;
  recurrence_interval: number;
  recurrence_day_of_week: number | null;
  recurrence_day_of_month: number | null;
  recurrence_end_date: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Data for creating a new task.
 */
export interface TaskCreate {
  title: string;
  description?: string | null;
  priority?: TaskPriority;
  tags?: string[];
  due_date?: string | null;
  is_recurring?: boolean;
  recurrence_frequency?: RecurrenceFrequency | null;
  recurrence_interval?: number;
  recurrence_day_of_week?: number | null;
  recurrence_day_of_month?: number | null;
  recurrence_end_date?: string | null;
}

/**
 * Data for updating an existing task.
 */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  priority?: TaskPriority;
  tags?: string[];
  due_date?: string | null;
  is_recurring?: boolean;
  recurrence_frequency?: RecurrenceFrequency | null;
  recurrence_interval?: number;
  recurrence_day_of_week?: number | null;
  recurrence_day_of_month?: number | null;
  recurrence_end_date?: string | null;
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
