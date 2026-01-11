// [Task]: T082, T083, T084, T087 [From]: spec.md §FR-012
"use client";

/**
 * Delete task confirmation dialog using shadcn/ui Dialog.
 * Shows confirmation message with Cancel and Delete buttons.
 */

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { deleteTask, ApiClientError } from "@/lib/api";
import type { Task } from "@/types/task";
import { AlertTriangle } from "lucide-react";

interface DeleteTaskDialogProps {
  task: Task | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onTaskDeleted: (taskId: number) => void;
}

export function DeleteTaskDialog({
  task,
  open,
  onOpenChange,
  onTaskDeleted,
}: DeleteTaskDialogProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDelete = async () => {
    if (!task) return;

    setIsLoading(true);
    setError(null);

    try {
      await deleteTask(task.id);
      onTaskDeleted(task.id);
      onOpenChange(false);
    } catch (err) {
      if (err instanceof ApiClientError) {
        if (err.status === 404) {
          setError("Task not found. It may have already been deleted.");
        } else if (err.status === 401) {
          setError("You are not authorized to delete this task.");
        } else {
          setError(typeof err.detail === "string" ? err.detail : "Failed to delete task");
        }
      } else {
        setError("Failed to delete task. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100">
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>
            <DialogTitle>Delete Task</DialogTitle>
          </div>
          <DialogDescription className="pt-2">
            Are you sure you want to delete this task? This action cannot be undone.
          </DialogDescription>
        </DialogHeader>

        {task && (
          <div className="rounded-md bg-gray-50 p-3">
            <p className="font-medium text-gray-900">{task.title}</p>
            {task.description && (
              <p className="mt-1 text-sm text-gray-500">{task.description}</p>
            )}
          </div>
        )}

        {/* Error message */}
        {error && (
          <div
            className="rounded-md bg-red-50 p-3 text-sm text-red-600"
            role="alert"
          >
            {error}
          </div>
        )}

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleDelete}
            disabled={isLoading}
          >
            {isLoading ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
