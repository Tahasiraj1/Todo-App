// [Task]: T047, T050, T054, T055, T090 [From]: spec.md §FR-006, §FR-007
"use client";

/**
 * Task form component for creating new tasks.
 * Includes title and description fields with validation.
 */

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createTask, ApiClientError } from "@/lib/api";
import type { Task } from "@/types/task";
import { Plus } from "lucide-react";

interface TaskFormProps {
  onTaskCreated: (task: Task) => void;
}

export function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [titleError, setTitleError] = useState<string | null>(null);

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

  const validateDescription = (value: string): boolean => {
    if (value.length > 1000) {
      setError("Description must be 1000 characters or less");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!validateTitle(title)) {
      return;
    }

    if (!validateDescription(description)) {
      return;
    }

    setIsLoading(true);

    try {
      const task = await createTask({
        title: title.trim(),
        description: description.trim() || null,
      });

      // Reset form
      setTitle("");
      setDescription("");

      // Notify parent
      onTaskCreated(task);
    } catch (err) {
      if (err instanceof ApiClientError) {
        if (Array.isArray(err.detail)) {
          // Handle validation errors
          const messages = (err.detail as Array<{ msg?: string }>).map((e) => e.msg || "Validation error").join(", ");
          setError(messages);
        } else {
          setError(err.detail as string);
        }
      } else {
        setError("Failed to create task. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Error message */}
      {error && (
        <div
          className="rounded-sm bg-destructive/10 border border-destructive/30 p-3 text-xs text-destructive animate-fade-in-up"
          role="alert"
        >
          <span className="opacity-70 mr-1">[ERROR]</span> {error}
        </div>
      )}

      <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
        {/* Title field */}
        <div className="flex-1 space-y-2">
          <Label htmlFor="task-title">title</Label>
          <Input
            id="task-title"
            type="text"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              if (titleError) validateTitle(e.target.value);
            }}
            onBlur={() => title && validateTitle(title)}
            placeholder="what needs to be done?"
            required
            disabled={isLoading}
            maxLength={200}
            className={titleError ? "border-destructive shadow-[0_0_10px_oklch(0.55_0.22_25/30%)]" : ""}
          />
          {titleError && (
            <p className="text-xs text-destructive animate-fade-in-up" role="alert">
              <span className="opacity-70">[!]</span> {titleError}
            </p>
          )}
        </div>

        {/* Description field */}
        <div className="flex-1 space-y-2">
          <Label htmlFor="task-description">description <span className="normal-case text-muted-foreground/60">(optional)</span></Label>
          <Input
            id="task-description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="add details..."
            disabled={isLoading}
            maxLength={1000}
          />
        </div>

        {/* Submit button */}
        <Button type="submit" disabled={isLoading || !title.trim()}>
          <Plus className="mr-2 h-4 w-4" />
          {isLoading ? "adding..." : "add_task"}
        </Button>
      </div>

      {/* Character count */}
      <div className="flex justify-between text-[10px] text-terminal-dim uppercase tracking-wider">
        <span>title: {title.length}/200</span>
        <span>desc: {description.length}/1000</span>
      </div>
    </form>
  );
}
