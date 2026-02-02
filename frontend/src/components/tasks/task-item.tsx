// [Task]: T052, T063, T068, T073, T074, T075, T077, T085, T086, T092, T021, T053, T061 [From]: spec.md
"use client";

/**
 * Task item component to display individual task.
 * Includes edit, delete, and completion toggle functionality.
 * Phase V: priority badge, tag chips, due date display, overdue indicator, recurrence display.
 */

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { toggleTaskCompletion, ApiClientError } from "@/lib/api";
import type { Task, TaskPriority } from "@/types/task";
import { Pencil, Trash2, Clock, AlertTriangle, Repeat } from "lucide-react";

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

  const priorityConfig: Record<TaskPriority, { label: string; color: string }> = {
    high: { label: "HIGH", color: "text-red-400 border-red-400/40 bg-red-400/10" },
    medium: { label: "MED", color: "text-yellow-400 border-yellow-400/40 bg-yellow-400/10" },
    low: { label: "LOW", color: "text-green-400 border-green-400/40 bg-green-400/10" },
  };

  const recurrenceLabel = task.is_recurring && task.recurrence_frequency
    ? `Repeats ${task.recurrence_frequency}${task.recurrence_interval > 1 ? ` (every ${task.recurrence_interval})` : ""}`
    : null;

  return (
    <div
      className={`group flex items-start gap-3 rounded-sm border p-4 transition-all duration-200 animate-slide-in ${
        task.completed
          ? "bg-muted/30 border-border/30 opacity-60"
          : "bg-card/50 border-border/60 hover:border-terminal/40 hover:bg-card/80 hover:shadow-[0_0_15px_var(--terminal-glow)]"
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
        <div className="flex items-center gap-2">
          <h3
            className={`font-medium text-sm tracking-wide ${
              task.completed ? "text-muted-foreground line-through" : "text-foreground"
            }`}
          >
            {task.completed && <span className="text-terminal-dim mr-2">[DONE]</span>}
            {task.title}
          </h3>

          {/* Priority badge */}
          <span
            className={`inline-flex items-center rounded-sm border px-1.5 py-0.5 text-[9px] font-mono font-bold uppercase tracking-widest ${priorityConfig[task.priority].color}`}
          >
            {priorityConfig[task.priority].label}
          </span>
        </div>

        {task.description && (
          <p
            className={`mt-1 text-xs tracking-wide ${
              task.completed ? "text-muted-foreground/60 line-through" : "text-muted-foreground"
            }`}
          >
            {task.description}
          </p>
        )}

        {/* Tags */}
        {task.tags && task.tags.length > 0 && (
          <div className="mt-1.5 flex flex-wrap gap-1">
            {task.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center rounded-sm border border-terminal/30 bg-terminal/5 px-1.5 py-0.5 text-[9px] font-mono text-terminal-dim tracking-wider"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}

        {/* Due date and recurrence */}
        <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1">
          {task.due_date && (
            <span
              className={`inline-flex items-center gap-1 text-[10px] font-mono tracking-wider ${
                task.is_overdue
                  ? "text-red-400 font-bold"
                  : "text-terminal-dim"
              }`}
            >
              {task.is_overdue ? (
                <AlertTriangle className="h-3 w-3" />
              ) : (
                <Clock className="h-3 w-3" />
              )}
              {task.is_overdue ? "OVERDUE: " : "due: "}
              {formatDate(task.due_date)}
            </span>
          )}

          {recurrenceLabel && (
            <span className="inline-flex items-center gap-1 text-[10px] font-mono text-terminal-dim tracking-wider">
              <Repeat className="h-3 w-3" />
              {recurrenceLabel}
            </span>
          )}
        </div>

        {/* Timestamps */}
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-[10px] text-terminal-dim uppercase tracking-wider">
          <span>created: {formatDate(task.created_at)}</span>
          {task.updated_at !== task.created_at && (
            <span>modified: {formatDate(task.updated_at)}</span>
          )}
        </div>

        {/* Error message */}
        {error && (
          <p className="mt-2 text-xs text-destructive" role="alert">
            <span className="opacity-70">[ERROR]</span> {error}
          </p>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex gap-1 opacity-0 transition-all duration-200 group-hover:opacity-100 focus-within:opacity-100 translate-x-2 group-hover:translate-x-0">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onEditClick(task)}
          aria-label="Edit task"
          className="h-8 w-8 text-terminal-dim hover:text-terminal hover:bg-terminal/10"
        >
          <Pencil className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => onDeleteClick(task)}
          aria-label="Delete task"
          className="h-8 w-8 text-destructive/70 hover:bg-destructive/10 hover:text-destructive"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
