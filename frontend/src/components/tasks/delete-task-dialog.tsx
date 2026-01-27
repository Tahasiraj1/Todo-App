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
            <div className="flex h-10 w-10 items-center justify-center rounded-sm bg-destructive/10 border border-destructive/30">
              <AlertTriangle className="h-5 w-5 text-destructive" />
            </div>
            <DialogTitle className="text-destructive">
              <span className="opacity-70 mr-2">[!]</span>
              delete_task
            </DialogTitle>
          </div>
          <DialogDescription className="pt-2">
            confirm deletion. this operation is irreversible.
          </DialogDescription>
        </DialogHeader>

        {task && (
          <div className="rounded-sm bg-muted/50 border border-border/60 p-3">
            <p className="font-medium text-foreground text-sm">{task.title}</p>
            {task.description && (
              <p className="mt-1 text-xs text-muted-foreground">{task.description}</p>
            )}
          </div>
        )}

        {/* Error message */}
        {error && (
          <div
            className="rounded-sm bg-destructive/10 border border-destructive/30 p-3 text-xs text-destructive animate-fade-in-up"
            role="alert"
          >
            <span className="opacity-70 mr-1">[ERROR]</span> {error}
          </div>
        )}

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleDelete}
            disabled={isLoading}
          >
            {isLoading ? "deleting..." : "confirm_delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
