// [Task]: T079 [From]: plan.md §Phase C, spec.md US6
"use client";

/**
 * Notification provider component.
 * Establishes WebSocket connection for real-time task updates and reminders.
 * Shows browser notifications when permission granted, falls back to in-app reminders.
 */

import { useEffect, useRef, useState, useCallback } from "react";
import { TodoWebSocket, type WebSocketMessage } from "@/lib/websocket";
import {
  requestNotificationPermission,
  showTaskReminder,
  getPermissionStatus,
} from "@/lib/notifications";
import { ReminderBanner, type ReminderItem } from "@/components/tasks/reminder-banner";

interface NotificationProviderProps {
  userId: string;
  onTaskUpdate?: (action: string, task: Record<string, unknown>) => void;
  children?: React.ReactNode;
}

export function NotificationProvider({
  userId,
  onTaskUpdate,
  children,
}: NotificationProviderProps) {
  const wsRef = useRef<TodoWebSocket | null>(null);
  const [reminders, setReminders] = useState<ReminderItem[]>([]);
  const [notifPermission, setNotifPermission] = useState<string>("default");

  // Request notification permission on mount
  useEffect(() => {
    setNotifPermission(getPermissionStatus());
    requestNotificationPermission().then(setNotifPermission);
  }, []);

  // Handle incoming WebSocket messages
  const handleMessage = useCallback(
    (message: WebSocketMessage) => {
      if (message.type === "task_update") {
        const payload = message.payload as { action: string; task: Record<string, unknown> };
        onTaskUpdate?.(payload.action, payload.task);
      } else if (message.type === "reminder") {
        const payload = message.payload as { task_id: number; title: string; due_at: string };

        // Try browser notification first
        if (notifPermission === "granted") {
          showTaskReminder(payload.title, payload.due_at);
        } else {
          // Fall back to in-app banner
          setReminders((prev) => {
            if (prev.some((r) => r.taskId === payload.task_id)) return prev;
            return [
              ...prev,
              {
                taskId: payload.task_id,
                title: payload.title,
                dueAt: payload.due_at,
              },
            ];
          });
        }
      }
    },
    [onTaskUpdate, notifPermission]
  );

  // Establish WebSocket connection
  useEffect(() => {
    if (!userId) return;

    const ws = new TodoWebSocket(userId);
    wsRef.current = ws;
    ws.onMessage(handleMessage);
    ws.connect();

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [userId, handleMessage]);

  const dismissReminder = (taskId: number) => {
    setReminders((prev) => prev.filter((r) => r.taskId !== taskId));
  };

  const dismissAllReminders = () => {
    setReminders([]);
  };

  return (
    <>
      {reminders.length > 0 && (
        <div className="fixed top-16 right-4 z-50 w-96 max-w-[calc(100vw-2rem)]">
          <ReminderBanner
            reminders={reminders}
            onDismiss={dismissReminder}
            onDismissAll={dismissAllReminders}
          />
        </div>
      )}
      {children}
    </>
  );
}
