// [Task]: T047, T050, T054, T055, T090, T022 [From]: spec.md §FR-006, §FR-007
"use client";

/**
 * Task form component for creating new tasks.
 * Phase V: priority selector, tag input, due date picker, recurrence fields.
 */

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createTask, ApiClientError } from "@/lib/api";
import type { Task, TaskPriority } from "@/types/task";
import { Plus, ChevronDown, ChevronUp, Calendar, Repeat } from "lucide-react";

interface TaskFormProps {
  onTaskCreated: (task: Task) => void;
}

export function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [dueDate, setDueDate] = useState("");
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurrenceFrequency, setRecurrenceFrequency] = useState<string>("");
  const [recurrenceInterval, setRecurrenceInterval] = useState(1);
  const [showAdvanced, setShowAdvanced] = useState(false);
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
        priority,
        tags,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
        is_recurring: isRecurring,
        recurrence_frequency: isRecurring ? recurrenceFrequency || null : null,
        recurrence_interval: isRecurring ? recurrenceInterval : 1,
      });

      // Reset form
      setTitle("");
      setDescription("");
      setPriority("medium");
      setTagInput("");
      setTags([]);
      setDueDate("");
      setIsRecurring(false);
      setRecurrenceFrequency("");
      setRecurrenceInterval(1);
      setShowAdvanced(false);

      // Notify parent
      onTaskCreated(task);
    } catch (err) {
      if (err instanceof ApiClientError) {
        if (Array.isArray(err.detail)) {
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

  const priorityOptions: { value: TaskPriority; label: string; color: string }[] = [
    { value: "high", label: "HIGH", color: "text-red-400 border-red-400/40 bg-red-400/10 hover:bg-red-400/20" },
    { value: "medium", label: "MED", color: "text-yellow-400 border-yellow-400/40 bg-yellow-400/10 hover:bg-yellow-400/20" },
    { value: "low", label: "LOW", color: "text-green-400 border-green-400/40 bg-green-400/10 hover:bg-green-400/20" },
  ];

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

      {/* Advanced toggle */}
      <button
        type="button"
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="flex items-center gap-1 text-[10px] text-terminal-dim uppercase tracking-wider hover:text-terminal transition-colors"
      >
        {showAdvanced ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
        {showAdvanced ? "hide options" : "priority, tags & due date"}
      </button>

      {showAdvanced && (
        <div className="space-y-3 animate-fade-in-up">
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

          {/* Due date picker */}
          <div className="space-y-2">
            <Label htmlFor="task-due-date">
              <Calendar className="inline h-3 w-3 mr-1" />
              due date <span className="normal-case text-muted-foreground/60">(optional)</span>
            </Label>
            <Input
              id="task-due-date"
              type="datetime-local"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              disabled={isLoading}
              className="font-mono text-xs"
            />
            {dueDate && (
              <button
                type="button"
                onClick={() => setDueDate("")}
                className="text-[10px] text-terminal-dim hover:text-destructive uppercase tracking-wider"
              >
                clear due date
              </button>
            )}
          </div>

          {/* Recurrence selector */}
          <div className="space-y-2">
            <Label>
              <Repeat className="inline h-3 w-3 mr-1" />
              recurrence <span className="normal-case text-muted-foreground/60">(optional)</span>
            </Label>
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 text-xs font-mono cursor-pointer">
                <input
                  type="checkbox"
                  checked={isRecurring}
                  onChange={(e) => {
                    setIsRecurring(e.target.checked);
                    if (!e.target.checked) {
                      setRecurrenceFrequency("");
                      setRecurrenceInterval(1);
                    }
                  }}
                  className="accent-[oklch(var(--terminal))]"
                />
                repeating task
              </label>
            </div>
            {isRecurring && (
              <div className="flex items-center gap-2 animate-fade-in-up">
                <span className="text-[10px] text-terminal-dim uppercase tracking-wider">every</span>
                <Input
                  type="number"
                  min={1}
                  max={99}
                  value={recurrenceInterval}
                  onChange={(e) => setRecurrenceInterval(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-16 text-xs font-mono"
                />
                <select
                  value={recurrenceFrequency}
                  onChange={(e) => setRecurrenceFrequency(e.target.value)}
                  className="rounded-sm border border-border/60 bg-background px-2 py-1.5 text-xs font-mono text-foreground focus:border-terminal/60 focus:outline-none"
                >
                  <option value="">select...</option>
                  <option value="daily">day(s)</option>
                  <option value="weekly">week(s)</option>
                  <option value="monthly">month(s)</option>
                </select>
              </div>
            )}
          </div>

          {/* Tag input */}
          <div className="space-y-2">
            <Label htmlFor="task-tags">tags <span className="normal-case text-muted-foreground/60">({tags.length}/10)</span></Label>
            <div className="flex gap-2">
              <Input
                id="task-tags"
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
      )}

      {/* Character count */}
      <div className="flex justify-between text-[10px] text-terminal-dim uppercase tracking-wider">
        <span>title: {title.length}/200</span>
        <span>desc: {description.length}/1000</span>
      </div>
    </form>
  );
}
