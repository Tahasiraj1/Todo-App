// [Task]: T061, T064, T065, T066 [From]: spec.md §FR-009
"use client";

/**
 * Task edit dialog component using shadcn/ui Dialog.
 * Pre-fills form with existing task data.
 */

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { updateTask, ApiClientError } from "@/lib/api";
import type { Task } from "@/types/task";

interface TaskEditDialogProps {
  task: Task | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onTaskUpdated: (task: Task) => void;
}

export function TaskEditDialog({
  task,
  open,
  onOpenChange,
  onTaskUpdated,
}: TaskEditDialogProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [titleError, setTitleError] = useState<string | null>(null);

  // Pre-fill form when task changes
  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || "");
      setError(null);
      setTitleError(null);
    }
  }, [task]);

  const validateTitle = (value: string): boolean => {
    if (!value.trim()) {
      setTitleError("Title is required");
      return false;
    }
    if (value.trim().length > 200) {
      setTitleError("Title must be 200 characters or less");
      return false;
    }
    setTitleError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!task) return;

    setError(null);

    if (!validateTitle(title)) {
      return;
    }

    if (description.length > 1000) {
      setError("Description must be 1000 characters or less");
      return;
    }

    setIsLoading(true);

    try {
      const updatedTask = await updateTask(task.id, {
        title: title.trim(),
        description: description.trim() || null,
      });

      onTaskUpdated(updatedTask);
      onOpenChange(false);
    } catch (err) {
      if (err instanceof ApiClientError) {
        if (err.status === 404) {
          setError("Task not found. It may have been deleted.");
        } else if (err.status === 401) {
          setError("You are not authorized to edit this task.");
        } else if (Array.isArray(err.detail)) {
          const messages = (err.detail as Array<{ msg?: string }>).map((e) => e.msg || "Validation error").join(", ");
          setError(messages);
        } else {
          setError(typeof err.detail === "string" ? err.detail : "Failed to update task");
        }
      } else {
        setError("Failed to update task. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Edit Task</DialogTitle>
          <DialogDescription>
            Make changes to your task details.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            {/* Error message */}
            {error && (
              <div
                className="rounded-md bg-red-50 p-3 text-sm text-red-600"
                role="alert"
              >
                {error}
              </div>
            )}

            {/* Title field */}
            <div className="space-y-2">
              <Label htmlFor="edit-title">Title</Label>
              <Input
                id="edit-title"
                type="text"
                value={title}
                onChange={(e) => {
                  setTitle(e.target.value);
                  if (titleError) validateTitle(e.target.value);
                }}
                onBlur={() => validateTitle(title)}
                placeholder="Task title"
                required
                disabled={isLoading}
                maxLength={200}
                className={titleError ? "border-red-500" : ""}
              />
              {titleError && (
                <p className="text-xs text-red-600" role="alert">
                  {titleError}
                </p>
              )}
              <p className="text-xs text-gray-500">{title.length}/200</p>
            </div>

            {/* Description field */}
            <div className="space-y-2">
              <Label htmlFor="edit-description">Description (optional)</Label>
              <Input
                id="edit-description"
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add details..."
                disabled={isLoading}
                maxLength={1000}
              />
              <p className="text-xs text-gray-500">{description.length}/1000</p>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading || !title.trim()}>
              {isLoading ? "Saving..." : "Save changes"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
