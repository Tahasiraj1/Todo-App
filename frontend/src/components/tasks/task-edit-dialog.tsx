// [Task]: T061, T064, T065, T066, T023 [From]: spec.md §FR-009
"use client";

/**
 * Task edit dialog component using shadcn/ui Dialog.
 * Phase V: priority selector and tag editing support.
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
import type { Task, TaskPriority } from "@/types/task";

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
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [titleError, setTitleError] = useState<string | null>(null);

  // Pre-fill form when task changes
  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || "");
      setPriority(task.priority || "medium");
      setTags(task.tags || []);
      setTagInput("");
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

  const handleAddTag = () => {
    const tag = tagInput.trim().toLowerCase();
    if (tag && !tags.includes(tag) && tags.length < 10 && tag.length <= 50) {
      setTags([...tags, tag]);
      setTagInput("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((t) => t !== tagToRemove));
  };

  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddTag();
    }
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
        priority,
        tags,
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

  const priorityOptions: { value: TaskPriority; label: string; color: string }[] = [
    { value: "high", label: "HIGH", color: "text-red-400 border-red-400/40 bg-red-400/10 hover:bg-red-400/20" },
    { value: "medium", label: "MED", color: "text-yellow-400 border-yellow-400/40 bg-yellow-400/10 hover:bg-yellow-400/20" },
    { value: "low", label: "LOW", color: "text-green-400 border-green-400/40 bg-green-400/10 hover:bg-green-400/20" },
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            <span className="text-terminal-dim mr-2">&gt;</span>
            edit_task
          </DialogTitle>
          <DialogDescription>
            modify task parameters
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            {/* Error message */}
            {error && (
              <div
                className="rounded-sm bg-destructive/10 border border-destructive/30 p-3 text-xs text-destructive animate-fade-in-up"
                role="alert"
              >
                <span className="opacity-70 mr-1">[ERROR]</span> {error}
              </div>
            )}

            {/* Title field */}
            <div className="space-y-2">
              <Label htmlFor="edit-title">title</Label>
              <Input
                id="edit-title"
                type="text"
                value={title}
                onChange={(e) => {
                  setTitle(e.target.value);
                  if (titleError) validateTitle(e.target.value);
                }}
                onBlur={() => validateTitle(title)}
                placeholder="task_title"
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
              <p className="text-[10px] text-terminal-dim uppercase tracking-wider">{title.length}/200</p>
            </div>

            {/* Description field */}
            <div className="space-y-2">
              <Label htmlFor="edit-description">description <span className="normal-case text-muted-foreground/60">(optional)</span></Label>
              <Input
                id="edit-description"
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="add details..."
                disabled={isLoading}
                maxLength={1000}
              />
              <p className="text-[10px] text-terminal-dim uppercase tracking-wider">{description.length}/1000</p>
            </div>

            {/* Priority selector */}
            <div className="space-y-2">
              <Label>priority</Label>
              <div className="flex gap-2">
                {priorityOptions.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setPriority(opt.value)}
                    className={`rounded-sm border px-3 py-1 text-[10px] font-mono font-bold uppercase tracking-widest transition-all ${
                      priority === opt.value
                        ? opt.color + " ring-1 ring-current"
                        : "text-muted-foreground border-border/40 bg-transparent hover:border-border"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Tag editing */}
            <div className="space-y-2">
              <Label htmlFor="edit-tags">tags <span className="normal-case text-muted-foreground/60">({tags.length}/10)</span></Label>
              <div className="flex gap-2">
                <Input
                  id="edit-tags"
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleTagKeyDown}
                  placeholder="add tag and press enter..."
                  disabled={isLoading || tags.length >= 10}
                  maxLength={50}
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAddTag}
                  disabled={!tagInput.trim() || tags.length >= 10}
                >
                  +tag
                </Button>
              </div>
              {tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1 rounded-sm border border-terminal/30 bg-terminal/5 px-1.5 py-0.5 text-[9px] font-mono text-terminal-dim tracking-wider"
                    >
                      #{tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        className="text-terminal-dim/60 hover:text-destructive ml-0.5"
                        aria-label={`Remove tag ${tag}`}
                      >
                        x
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
            >
              cancel
            </Button>
            <Button type="submit" disabled={isLoading || !title.trim()}>
              {isLoading ? "saving..." : "save"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
