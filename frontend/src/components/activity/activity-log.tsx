// [Task]: T067 [From]: spec.md US5, plan.md §Phase C
"use client";

/**
 * Activity log component.
 * Displays recent task operations with timestamps.
 */

import { useState, useEffect } from "react";
import { getActivity } from "@/lib/api";
import { Clock, Plus, Pencil, CheckCircle, Trash2, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ActivityEntry {
  id: number;
  user_id: string;
  task_id: number;
  event_type: string;
  task_title: string;
  task_data: Record<string, unknown>;
  created_at: string;
}

interface ActivityLogProps {
  userId: string;
}

const eventConfig: Record<string, { icon: typeof Plus; label: string; color: string }> = {
  created: { icon: Plus, label: "Created", color: "text-green-400" },
  updated: { icon: Pencil, label: "Updated", color: "text-yellow-400" },
  completed: { icon: CheckCircle, label: "Completed", color: "text-blue-400" },
  deleted: { icon: Trash2, label: "Deleted", color: "text-red-400" },
};

export function ActivityLog({ userId }: ActivityLogProps) {
  const [entries, setEntries] = useState<ActivityEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const limit = 20;

  const fetchActivity = async (currentOffset: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getActivity(userId, limit, currentOffset);
      if (currentOffset === 0) {
        setEntries(data.entries);
      } else {
        setEntries((prev) => [...prev, ...data.entries]);
      }
      setTotal(data.total);
    } catch {
      setError("Failed to load activity log");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivity(0);
  }, [userId]);

  const loadMore = () => {
    const newOffset = offset + limit;
    setOffset(newOffset);
    fetchActivity(newOffset);
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMin < 1) return "just now";
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  };

  if (error) {
    return (
      <div className="rounded-sm border border-destructive/30 bg-destructive/5 p-4 text-xs text-destructive">
        <span className="opacity-70">[ERROR]</span> {error}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-mono uppercase tracking-wider text-terminal-dim flex items-center gap-2">
          <Clock className="h-3.5 w-3.5" />
          recent activity ({total})
        </h3>
      </div>

      {entries.length === 0 && !loading && (
        <p className="text-xs text-muted-foreground py-4 text-center">No activity yet</p>
      )}

      <div className="space-y-1">
        {entries.map((entry) => {
          const config = eventConfig[entry.event_type] || eventConfig.updated;
          const Icon = config.icon;

          return (
            <div
              key={entry.id}
              className="flex items-center gap-3 rounded-sm border border-border/30 bg-card/30 px-3 py-2 text-xs"
            >
              <Icon className={`h-3.5 w-3.5 flex-shrink-0 ${config.color}`} />
              <div className="flex-1 min-w-0">
                <span className={`font-mono text-[10px] uppercase tracking-wider ${config.color}`}>
                  {config.label}
                </span>
                <span className="mx-1.5 text-muted-foreground/50">—</span>
                <span className="font-medium truncate">{entry.task_title}</span>
              </div>
              <span className="text-[10px] text-terminal-dim font-mono whitespace-nowrap">
                {formatDate(entry.created_at)}
              </span>
            </div>
          );
        })}
      </div>

      {loading && (
        <div className="text-center py-2 text-xs text-terminal-dim animate-pulse">
          loading...
        </div>
      )}

      {entries.length < total && !loading && (
        <Button
          variant="ghost"
          size="sm"
          onClick={loadMore}
          className="w-full text-[10px] text-terminal-dim hover:text-terminal uppercase tracking-wider"
        >
          <ChevronDown className="h-3 w-3 mr-1" />
          load more ({total - entries.length} remaining)
        </Button>
      )}
    </div>
  );
}
