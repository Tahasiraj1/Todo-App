// [Task]: T051, T053, T067, T076, T088, T091 [From]: spec.md
"use client";

/**
 * Task list component to display all tasks.
 * Includes empty state and loading states.
 */

import { TaskItem } from "./task-item";
import type { Task } from "@/types/task";
import { ClipboardList } from "lucide-react";

interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
  onTaskUpdated: (task: Task) => void;
  onEditClick: (task: Task) => void;
  onDeleteClick: (task: Task) => void;
  onAddFirstTask: () => void;
}

export function TaskList({
  tasks,
  isLoading,
  onTaskUpdated,
  onEditClick,
  onDeleteClick,
  onAddFirstTask,
}: TaskListProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-24 animate-pulse rounded-lg bg-gray-100"
          />
        ))}
      </div>
    );
  }

  // Empty state
  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <ClipboardList className="mb-4 h-16 w-16 text-gray-300" />
        <h3 className="text-lg font-medium text-gray-900">No tasks yet</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by adding your first task
        </p>
        <button
          onClick={onAddFirstTask}
          className="mt-4 text-sm font-medium text-primary hover:underline"
        >
          Add your first task
        </button>
      </div>
    );
  }

  // Sort tasks: incomplete first, then by updated_at descending
  const sortedTasks = [...tasks].sort((a, b) => {
    // Incomplete tasks first
    if (a.completed !== b.completed) {
      return a.completed ? 1 : -1;
    }
    // Then by updated_at descending
    return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
  });

  return (
    <div className="space-y-3">
      {sortedTasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onTaskUpdated={onTaskUpdated}
          onEditClick={onEditClick}
          onDeleteClick={onDeleteClick}
        />
      ))}
    </div>
  );
}
