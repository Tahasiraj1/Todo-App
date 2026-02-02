# Data Model: Phase V — Advanced Cloud Deployment

**Feature**: `005-cloud-event-deployment`
**Date**: 2026-01-31

---

## Existing Entities (Modified)

### Task (Extended)

Existing columns retained. New columns added:

| Column | Type | Nullable | Default | Constraint | Notes |
|--------|------|----------|---------|------------|-------|
| `id` | INTEGER | No | auto-increment | PK | Existing |
| `user_id` | VARCHAR | No | — | FK → user.id, indexed | Existing |
| `title` | VARCHAR(200) | No | — | min 1 char | Existing |
| `description` | VARCHAR(1000) | Yes | NULL | — | Existing |
| `completed` | BOOLEAN | No | false | — | Existing |
| `created_at` | TIMESTAMP(TZ) | No | utcnow | — | Existing |
| `updated_at` | TIMESTAMP(TZ) | No | utcnow | — | Existing |
| **`priority`** | VARCHAR(10) | No | "medium" | enum: high/medium/low | **New** |
| **`tags`** | JSON | No | [] | JSON array of strings | **New** |
| **`due_date`** | TIMESTAMP(TZ) | Yes | NULL | — | **New** |
| **`is_recurring`** | BOOLEAN | No | false | — | **New** |
| **`recurrence_frequency`** | VARCHAR(10) | Yes | NULL | enum: daily/weekly/monthly | **New** |
| **`recurrence_interval`** | INTEGER | No | 1 | min 1 | **New** |
| **`recurrence_day_of_week`** | INTEGER | Yes | NULL | 0-6 (Mon-Sun) | **New** |
| **`recurrence_day_of_month`** | INTEGER | Yes | NULL | 1-31 | **New** |
| **`recurrence_end_date`** | TIMESTAMP(TZ) | Yes | NULL | — | **New** |
| **`reminder_sent`** | BOOLEAN | No | false | — | **New** — tracks if reminder was published for current due_date |

**Indexes (new)**:
- `ix_tasks_due_date` on `due_date` (for overdue queries)
- `ix_tasks_priority` on `priority` (for filtered listing)

**Validation rules**:
- `priority` must be one of: `high`, `medium`, `low`
- `tags` must be a JSON array; each element must be a non-empty string, max 50 chars, max 10 tags per task
- `due_date` can be past (task is immediately overdue)
- `recurrence_frequency` required if `is_recurring` is true
- `recurrence_day_of_week` valid only when `recurrence_frequency` is `weekly`
- `recurrence_day_of_month` valid only when `recurrence_frequency` is `monthly`
- `recurrence_interval` must be >= 1
- `reminder_sent` resets to false when `due_date` changes

**Derived properties** (not stored):
- `is_overdue`: computed as `due_date is not None AND due_date < now() AND completed is false`

---

## New Entities

### Activity Log Entry

| Column | Type | Nullable | Default | Constraint | Notes |
|--------|------|----------|---------|------------|-------|
| `id` | INTEGER | No | auto-increment | PK | |
| `user_id` | VARCHAR | No | — | FK → user.id, indexed | |
| `task_id` | INTEGER | No | — | — | Reference to task (not FK — task may be deleted) |
| `event_type` | VARCHAR(20) | No | — | enum: created/updated/completed/deleted | |
| `task_title` | VARCHAR(200) | No | — | — | Snapshot of task title at event time |
| `task_data` | JSON | No | — | — | Full task snapshot at event time |
| `created_at` | TIMESTAMP(TZ) | No | utcnow | — | When the event occurred |

**Indexes**:
- `ix_activity_log_user_id` on `user_id` (for user-specific queries)
- `ix_activity_log_created_at` on `created_at` (for retention purge and chronological listing)

**Retention**: Entries older than 90 days are automatically purged (scheduled cleanup).

**Validation rules**:
- `event_type` must be one of: `created`, `updated`, `completed`, `deleted`
- `task_data` must be a valid JSON object containing at minimum: `id`, `title`, `completed`

---

## Event Schemas (Kafka / Dapr Pub/Sub)

### Task Event (topic: `task-events`)

Published by the backend on every task mutation. Consumed by: activity log handler, recurring task service.

```json
{
  "id": "uuid-v4",
  "specversion": "1.0",
  "type": "com.todo.task.created",
  "source": "/api/tasks",
  "time": "2026-01-31T12:00:00Z",
  "data": {
    "event_type": "created | updated | completed | deleted",
    "task_id": 123,
    "user_id": "user-abc-123",
    "task_data": {
      "id": 123,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "priority": "high",
      "tags": ["shopping", "home"],
      "due_date": "2026-02-01T15:00:00Z",
      "is_recurring": true,
      "recurrence_frequency": "weekly",
      "recurrence_interval": 1,
      "recurrence_day_of_week": 0
    },
    "timestamp": "2026-01-31T12:00:00Z"
  }
}
```

CloudEvents envelope used because Dapr wraps pub/sub messages in CloudEvents format by default.

**type field mapping**:
- `com.todo.task.created` — new task created
- `com.todo.task.updated` — task fields modified
- `com.todo.task.completed` — task marked complete
- `com.todo.task.deleted` — task deleted

### Reminder Event (topic: `reminders`)

Published by the backend when a Dapr Job fires (task approaching due date). Consumed by: notification service.

```json
{
  "id": "uuid-v4",
  "specversion": "1.0",
  "type": "com.todo.reminder.due",
  "source": "/api/jobs",
  "time": "2026-02-01T14:30:00Z",
  "data": {
    "task_id": 123,
    "title": "Buy groceries",
    "due_at": "2026-02-01T15:00:00Z",
    "remind_at": "2026-02-01T14:30:00Z",
    "user_id": "user-abc-123"
  }
}
```

### Task Update Event (topic: `task-updates`)

Published by the backend on every task mutation (same source event as task-events, different topic). Consumed by: notification service (for WebSocket broadcast to connected clients).

```json
{
  "id": "uuid-v4",
  "specversion": "1.0",
  "type": "com.todo.task.sync",
  "source": "/api/tasks",
  "time": "2026-01-31T12:00:00Z",
  "data": {
    "action": "created | updated | completed | deleted",
    "user_id": "user-abc-123",
    "task": {
      "id": 123,
      "title": "Buy groceries",
      "completed": false,
      "priority": "high",
      "tags": ["shopping"],
      "due_date": "2026-02-01T15:00:00Z"
    }
  }
}
```

---

## Entity Relationship Diagram

```
┌──────────┐       ┌──────────────────────────────────┐
│   User   │──1:N──│              Task                 │
│          │       │  + priority (new)                 │
│  id (PK) │       │  + tags[] (new)                  │
│  email   │       │  + due_date (new)                │
│  name    │       │  + recurrence fields (new)       │
└──────────┘       │  + reminder_sent (new)           │
     │             └──────────────────────────────────┘
     │                        │ publishes
     │                        ▼
     │             ┌─────────────────────┐
     │             │    Task Event       │   → topic: task-events
     │             │    Reminder Event   │   → topic: reminders
     │             │    Update Event     │   → topic: task-updates
     │             └─────────────────────┘
     │                        │ consumed by
     │                        ▼
     │             ┌──────────────────────┐
     ├──────1:N────│  Activity Log Entry  │   (persisted events)
     │             │  + 90-day retention  │
     │             └──────────────────────┘
     │
     ├──────1:N────┌──────────────┐
     │             │ Conversation │
     │             └──────┬───────┘
     │                    │
     └──────1:N────┌──────┴───────┐
                   │   Message    │
                   └──────────────┘
```

---

## State Transitions

### Task Lifecycle

```
                    ┌─────────────────────┐
                    │                     │
    create ────────►│   Active (pending)  │◄──── update (title, desc,
                    │   completed=false   │       priority, tags, due_date,
                    │                     │       recurrence)
                    └────────┬────────────┘
                             │
                        complete
                             │
                    ┌────────▼────────────┐
                    │                     │
                    │  Completed          │──── if is_recurring:
                    │  completed=true     │     → publish task-completed event
                    │                     │     → recurring service creates
                    └────────┬────────────┘       next occurrence (new Active task)
                             │
                         delete
                             │
                    ┌────────▼────────────┐
                    │     Deleted         │  (hard delete from DB)
                    └─────────────────────┘
```

### Reminder Lifecycle

```
    due_date set on task
         │
         ▼
    Schedule Dapr Job
    (due_date - 30min)
         │
         ├── due_date changed → Cancel old job, schedule new
         ├── due_date removed → Cancel job
         ├── task deleted     → Cancel job
         │
         ▼
    Job fires at remind_at
         │
         ▼
    Publish to "reminders" topic
    Set task.reminder_sent = true
         │
         ▼
    Notification Service receives
         │
         ├── Browser permission granted → Browser notification
         └── Browser permission denied  → In-app banner
```
