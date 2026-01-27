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
            className="h-24 rounded-sm bg-muted/50 border border-border/30 relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-terminal/5 to-transparent animate-[shimmer_2s_infinite]" style={{ backgroundSize: '200% 100%' }} />
            <div className="p-4 space-y-3">
              <div className="h-4 w-3/4 bg-terminal/10 rounded-sm" />
              <div className="h-3 w-1/2 bg-terminal/5 rounded-sm" />
            </div>
          </div>
        ))}
        <p className="text-xs text-terminal-dim text-center uppercase tracking-wider animate-pulse-soft">
          loading tasks...
        </p>
      </div>
    );
  }

  // Empty state
  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="relative mb-4">
          <ClipboardList className="h-16 w-16 text-terminal/30" />
          <div className="absolute inset-0 blur-xl bg-terminal/10" />
        </div>
        <h3 className="text-sm font-medium text-foreground uppercase tracking-wider">
          <span className="text-terminal-dim">[</span>
          no_tasks
          <span className="text-terminal-dim">]</span>
        </h3>
        <p className="mt-2 text-xs text-muted-foreground tracking-wide">
          initialize your first task to begin
        </p>
        <button
          onClick={onAddFirstTask}
          className="mt-4 text-xs font-medium text-terminal hover:text-terminal-bright uppercase tracking-wider transition-colors hover:underline"
        >
          &gt; create_task
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
