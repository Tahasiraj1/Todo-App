// [Task]: T052, T063, T068, T073, T074, T075, T077, T085, T086, T092 [From]: spec.md
"use client";

/**
 * Task item component to display individual task.
 * Includes edit, delete, and completion toggle functionality.
 */

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { toggleTaskCompletion, ApiClientError } from "@/lib/api";
import type { Task } from "@/types/task";
import { Pencil, Trash2 } from "lucide-react";

interface TaskItemProps {
  task: Task;
  onTaskUpdated: (task: Task) => void;
  onEditClick: (task: Task) => void;
  onDeleteClick: (task: Task) => void;
}

export function TaskItem({
  task,
  onTaskUpdated,
  onEditClick,
  onDeleteClick,
}: TaskItemProps) {
  const [isToggling, setIsToggling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleToggleComplete = async () => {
    setIsToggling(true);
    setError(null);

    try {
      const updatedTask = await toggleTaskCompletion(task.id);
      onTaskUpdated(updatedTask);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(typeof err.detail === "string" ? err.detail : "Failed to update task");
      } else {
        setError("Failed to update task");
      }
    } finally {
      setIsToggling(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div
      className={`group flex items-start gap-3 rounded-lg border p-4 transition-colors hover:bg-gray-50 ${
        task.completed ? "bg-gray-50 opacity-75" : "bg-white"
      }`}
    >
      {/* Completion checkbox */}
      <div className="pt-0.5">
        <Checkbox
          checked={task.completed}
          onCheckedChange={handleToggleComplete}
          disabled={isToggling}
          aria-label={task.completed ? "Mark as incomplete" : "Mark as complete"}
          className="h-5 w-5"
        />
      </div>

      {/* Task content */}
      <div className="flex-1 min-w-0">
        <h3
          className={`font-medium ${
            task.completed ? "text-gray-500 line-through" : "text-gray-900"
          }`}
        >
          {task.title}
        </h3>

        {task.description && (
          <p
            className={`mt-1 text-sm ${
              task.completed ? "text-gray-400 line-through" : "text-gray-600"
            }`}
          >
            {task.description}
          </p>
        )}

        {/* Timestamps */}
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-400">
          <span>Created: {formatDate(task.created_at)}</span>
          {task.updated_at !== task.created_at && (
            <span>Updated: {formatDate(task.updated_at)}</span>
          )}
        </div>

        {/* Error message */}
        {error && (
          <p className="mt-2 text-xs text-red-600" role="alert">
            {error}
          </p>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onEditClick(task)}
          aria-label="Edit task"
          className="h-8 w-8"
        >
          <Pencil className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => onDeleteClick(task)}
          aria-label="Delete task"
          className="h-8 w-8 text-red-600 hover:bg-red-50 hover:text-red-700"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
