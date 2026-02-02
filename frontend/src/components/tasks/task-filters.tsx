// [Task]: T028 [From]: spec.md §FR-003, §FR-004, §FR-005, §FR-006
"use client";

/**
 * Task filters component with priority dropdown, tag filter, status toggle,
 * sort selector, and search input.
 */

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { TaskPriority } from "@/types/task";
import { Search, SlidersHorizontal, X } from "lucide-react";

export interface TaskFilters {
  status?: string;
  priority?: TaskPriority | "";
  tag?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
  overdue?: boolean;
}

interface TaskFiltersProps {
  filters: TaskFilters;
  onFiltersChange: (filters: TaskFilters) => void;
  availableTags: string[];
}

export function TaskFiltersBar({
  filters,
  onFiltersChange,
  availableTags,
}: TaskFiltersProps) {
  const [showFilters, setShowFilters] = useState(false);

  const updateFilter = (key: keyof TaskFilters, value: string | boolean | undefined) => {
    onFiltersChange({ ...filters, [key]: value || undefined });
  };

  const clearFilters = () => {
    onFiltersChange({});
  };

  const hasActiveFilters = filters.status || filters.priority || filters.tag || filters.search || filters.overdue;

  return (
    <div className="space-y-3">
      {/* Search bar + filter toggle */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-terminal-dim" />
          <Input
            type="text"
            value={filters.search || ""}
            onChange={(e) => updateFilter("search", e.target.value)}
            placeholder="search tasks..."
            className="pl-8 h-9 text-xs"
          />
        </div>
        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className={`inline-flex items-center gap-1.5 rounded-sm border px-3 py-1.5 text-[10px] font-mono uppercase tracking-wider transition-all ${
            showFilters || hasActiveFilters
              ? "border-terminal/40 bg-terminal/10 text-terminal"
              : "border-border/40 text-terminal-dim hover:border-border hover:text-terminal"
          }`}
        >
          <SlidersHorizontal className="h-3.5 w-3.5" />
          filters
          {hasActiveFilters && (
            <span className="ml-1 rounded-full bg-terminal/20 px-1.5 py-0.5 text-[8px]">on</span>
          )}
        </button>
        {hasActiveFilters && (
          <button
            type="button"
            onClick={clearFilters}
            className="inline-flex items-center gap-1 rounded-sm border border-destructive/30 px-2 py-1.5 text-[10px] font-mono uppercase tracking-wider text-destructive/70 hover:bg-destructive/10 hover:text-destructive transition-all"
          >
            <X className="h-3 w-3" />
            clear
          </button>
        )}
      </div>

      {/* Filter panel */}
      {showFilters && (
        <div className="grid grid-cols-2 gap-3 rounded-sm border border-border/40 bg-card/30 p-3 animate-fade-in-up sm:grid-cols-4">
          {/* Status filter */}
          <div className="space-y-1.5">
            <Label className="text-[9px]">status</Label>
            <div className="flex flex-wrap gap-1">
              {["all", "pending", "completed"].map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => updateFilter("status", s === "all" ? "" : s)}
                  className={`rounded-sm border px-2 py-0.5 text-[9px] font-mono uppercase tracking-wider transition-all ${
                    (filters.status || "all") === s || (!filters.status && s === "all")
                      ? "border-terminal/40 bg-terminal/10 text-terminal"
                      : "border-border/30 text-terminal-dim hover:border-border"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Priority filter */}
          <div className="space-y-1.5">
            <Label className="text-[9px]">priority</Label>
            <div className="flex flex-wrap gap-1">
              {[
                { value: "", label: "all", color: "" },
                { value: "high", label: "high", color: "text-red-400" },
                { value: "medium", label: "med", color: "text-yellow-400" },
                { value: "low", label: "low", color: "text-green-400" },
              ].map((p) => (
                <button
                  key={p.value}
                  type="button"
                  onClick={() => updateFilter("priority", p.value)}
                  className={`rounded-sm border px-2 py-0.5 text-[9px] font-mono uppercase tracking-wider transition-all ${
                    (filters.priority || "") === p.value
                      ? `border-current/40 bg-current/10 ${p.color || "text-terminal"}`
                      : "border-border/30 text-terminal-dim hover:border-border"
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Sort */}
          <div className="space-y-1.5">
            <Label className="text-[9px]">sort by</Label>
            <select
              value={filters.sort_by || "created_at"}
              onChange={(e) => updateFilter("sort_by", e.target.value)}
              className="w-full rounded-sm border border-border/40 bg-background px-2 py-1 text-[10px] font-mono text-foreground"
            >
              <option value="created_at">created</option>
              <option value="due_date">due date</option>
              <option value="priority">priority</option>
              <option value="title">title</option>
            </select>
            <div className="flex gap-1">
              {["desc", "asc"].map((order) => (
                <button
                  key={order}
                  type="button"
                  onClick={() => updateFilter("sort_order", order)}
                  className={`rounded-sm border px-2 py-0.5 text-[9px] font-mono uppercase tracking-wider transition-all ${
                    (filters.sort_order || "desc") === order
                      ? "border-terminal/40 bg-terminal/10 text-terminal"
                      : "border-border/30 text-terminal-dim hover:border-border"
                  }`}
                >
                  {order === "desc" ? "newest" : "oldest"}
                </button>
              ))}
            </div>
          </div>

          {/* Overdue + Tag filter */}
          <div className="space-y-1.5">
            <Label className="text-[9px]">more</Label>
            <button
              type="button"
              onClick={() => updateFilter("overdue", !filters.overdue)}
              className={`w-full rounded-sm border px-2 py-0.5 text-[9px] font-mono uppercase tracking-wider transition-all ${
                filters.overdue
                  ? "border-red-400/40 bg-red-400/10 text-red-400"
                  : "border-border/30 text-terminal-dim hover:border-border"
              }`}
            >
              overdue only
            </button>
            {availableTags.length > 0 && (
              <select
                value={filters.tag || ""}
                onChange={(e) => updateFilter("tag", e.target.value)}
                className="w-full rounded-sm border border-border/40 bg-background px-2 py-1 text-[10px] font-mono text-foreground"
              >
                <option value="">all tags</option>
                {availableTags.map((tag) => (
                  <option key={tag} value={tag}>
                    #{tag}
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
