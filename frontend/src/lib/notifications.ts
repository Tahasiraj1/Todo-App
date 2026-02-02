// [Task]: T055 [From]: spec.md US3, plan.md §Phase C
/**
 * Browser notification utilities.
 * Handles permission requests and showing notifications.
 * Falls back gracefully when notifications are denied or unavailable.
 */

export type NotificationPermission = "granted" | "denied" | "default" | "unsupported";

/**
 * Check if the browser supports notifications.
 */
export function isNotificationSupported(): boolean {
  return typeof window !== "undefined" && "Notification" in window;
}

/**
 * Get the current notification permission status.
 */
export function getPermissionStatus(): NotificationPermission {
  if (!isNotificationSupported()) return "unsupported";
  return Notification.permission as NotificationPermission;
}

/**
 * Request notification permission from the user.
 * Returns the resulting permission status.
 */
export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!isNotificationSupported()) return "unsupported";

  if (Notification.permission === "granted") return "granted";
  if (Notification.permission === "denied") return "denied";

  try {
    const result = await Notification.requestPermission();
    return result as NotificationPermission;
  } catch {
    return "denied";
  }
}

/**
 * Show a browser notification.
 * Returns true if the notification was shown, false otherwise.
 */
export function showNotification(
  title: string,
  options?: {
    body?: string;
    icon?: string;
    tag?: string;
    onClick?: () => void;
  }
): boolean {
  if (!isNotificationSupported()) return false;
  if (Notification.permission !== "granted") return false;

  try {
    const notification = new Notification(title, {
      body: options?.body,
      icon: options?.icon || "/favicon.ico",
      tag: options?.tag,
    });

    if (options?.onClick) {
      notification.onclick = () => {
        window.focus();
        options.onClick?.();
        notification.close();
      };
    }

    // Auto-close after 10 seconds
    setTimeout(() => notification.close(), 10000);

    return true;
  } catch {
    return false;
  }
}

/**
 * Show a task reminder notification.
 */
export function showTaskReminder(taskTitle: string, dueAt: string): boolean {
  const dueDate = new Date(dueAt);
  const timeStr = dueDate.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  });

  return showNotification(`Task Reminder: ${taskTitle}`, {
    body: `Due at ${timeStr}`,
    tag: `reminder-${taskTitle}`,
    onClick: () => {
      // Focus on the dashboard when clicked
      window.location.href = "/dashboard";
    },
  });
}
