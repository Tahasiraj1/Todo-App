// [Task]: T056 [From]: spec.md US3, plan.md §Phase C
"use client";

/**
 * In-app reminder banner component.
 * Fallback when browser notifications are denied.
 * Displays upcoming task reminders as dismissible banners.
 */

import { useState } from "react";
import { AlertTriangle, X, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface ReminderItem {
  taskId: number;
  title: string;
  dueAt: string;
}

interface ReminderBannerProps {
  reminders: ReminderItem[];
  onDismiss: (taskId: number) => void;
  onDismissAll: () => void;
}

export function ReminderBanner({
  reminders,
  onDismiss,
  onDismissAll,
}: ReminderBannerProps) {
  const [collapsed, setCollapsed] = useState(false);

  if (reminders.length === 0) return null;

  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleTimeString(undefined, {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (collapsed) {
    return (
      <button
        onClick={() => setCollapsed(false)}
        className="fixed bottom-4 right-4 z-50 flex items-center gap-2 rounded-sm border border-yellow-400/40 bg-yellow-400/10 px-3 py-2 text-xs font-mono text-yellow-400 shadow-lg hover:bg-yellow-400/20 transition-all animate-fade-in-up"
      >
        <Bell className="h-4 w-4" />
        {reminders.length} reminder{reminders.length > 1 ? "s" : ""}
      </button>
    );
  }

  return (
    <div className="w-full rounded-sm border border-yellow-400/40 bg-yellow-400/5 p-3 space-y-2 animate-fade-in-up">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-mono text-yellow-400 uppercase tracking-wider">
          <AlertTriangle className="h-3.5 w-3.5" />
          task reminders ({reminders.length})
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={onDismissAll}
            className="h-6 px-2 text-[10px] text-terminal-dim hover:text-terminal"
          >
            dismiss all
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(true)}
            className="h-6 w-6 text-terminal-dim hover:text-terminal"
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {reminders.map((reminder) => (
        <div
          key={reminder.taskId}
          className="flex items-center justify-between rounded-sm border border-border/40 bg-card/50 px-3 py-2"
        >
          <div className="flex items-center gap-2">
            <Bell className="h-3 w-3 text-yellow-400" />
            <span className="text-xs font-medium">{reminder.title}</span>
            <span className="text-[10px] font-mono text-terminal-dim">
              due {formatTime(reminder.dueAt)}
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onDismiss(reminder.taskId)}
            className="h-6 w-6 text-terminal-dim hover:text-terminal"
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      ))}
    </div>
  );
}
