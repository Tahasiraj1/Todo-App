# MCP Tools Contract: Phase III - AI-Powered Todo Chatbot

**Created**: 2026-01-17
**Feature**: [specs/003-phase3-chatbot/spec.md](../spec.md)

## Overview

This document specifies the MCP (Model Context Protocol) tools that the AI agent will use to manage tasks. All tools are exposed through an MCP server implemented using the Official MCP SDK and are invoked by the OpenAI Agents SDK.

## Tool Specifications

### Tool: add_task

| Attribute | Value |
|-----------|-------|
| **Purpose** | Create a new task |
| **Parameters** | user_id (string, required), title (string, required), description (string, optional) |
| **Returns** | task_id, status, title |

**Example Input**:
```json
{
  "user_id": "usr_abc123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Example Output**:
```json
{
  "task_id": 5,
  "status": "created",
  "title": "Buy groceries"
}
```

**Error Cases**:
- Missing user_id: Return error with message "user_id is required"
- Missing title: Return error with message "title is required"
- Title too long (>200 chars): Return error with message "title exceeds maximum length"

---

### Tool: list_tasks

| Attribute | Value |
|-----------|-------|
| **Purpose** | Retrieve tasks from the list |
| **Parameters** | user_id (string, required), status (string, optional: "all", "pending", "completed") |
| **Returns** | Array of task objects |

**Example Input**:
```json
{
  "user_id": "usr_abc123",
  "status": "pending"
}
```

**Example Output**:
```json
[
  {"id": 1, "title": "Buy groceries", "completed": false, "description": "Milk, eggs, bread"},
  {"id": 3, "title": "Call mom", "completed": false, "description": null}
]
```

**Notes**:
- If status is not provided, defaults to "all"
- Returns empty array if no tasks match

---

### Tool: complete_task

| Attribute | Value |
|-----------|-------|
| **Purpose** | Mark a task as complete |
| **Parameters** | user_id (string, required), task_id (integer, required) |
| **Returns** | task_id, status, title |

**Example Input**:
```json
{
  "user_id": "usr_abc123",
  "task_id": 3
}
```

**Example Output**:
```json
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom"
}
```

**Error Cases**:
- Task not found: Return error with message "Task not found"
- Task belongs to different user: Return error with message "Task not found" (no leak of other user data)

---

### Tool: delete_task

| Attribute | Value |
|-----------|-------|
| **Purpose** | Remove a task from the list |
| **Parameters** | user_id (string, required), task_id (integer, required) |
| **Returns** | task_id, status, title |

**Example Input**:
```json
{
  "user_id": "usr_abc123",
  "task_id": 2
}
```

**Example Output**:
```json
{
  "task_id": 2,
  "status": "deleted",
  "title": "Old task"
}
```

**Error Cases**:
- Task not found: Return error with message "Task not found"
- Task belongs to different user: Return error with message "Task not found" (no leak of other user data)

---

### Tool: update_task

| Attribute | Value |
|-----------|-------|
| **Purpose** | Modify task title or description |
| **Parameters** | user_id (string, required), task_id (integer, required), title (string, optional), description (string, optional) |
| **Returns** | task_id, status, title |

**Example Input**:
```json
{
  "user_id": "usr_abc123",
  "task_id": 1,
  "title": "Buy groceries and fruits"
}
```

**Example Output**:
```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits"
}
```

**Error Cases**:
- Task not found: Return error with message "Task not found"
- Task belongs to different user: Return error with message "Task not found"
- Empty title provided: Return error with message "title cannot be empty"
- No updates provided: Return error with message "No updates provided"

## Agent Behavior Mapping

| User Intent | Natural Language Examples | MCP Tool |
|-------------|--------------------------|----------|
| **Task Creation** | "Add a task to buy groceries", "I need to remember to pay bills", "Create a task called 'Call mom'" | `add_task` |
| **Task Listing** | "Show me all my tasks", "What's pending?", "What have I completed?" | `list_tasks` |
| **Task Completion** | "Mark task 3 as complete", "I'm done with the groceries task", "Complete my 'Call mom' task" | `complete_task` |
| **Task Deletion** | "Delete task 2", "Remove the meeting task", "Cancel my 'Old task'" | `delete_task` |
| **Task Update** | "Change task 1 to 'Buy groceries and fruits'", "Rename my groceries task", "Add description to task 5" | `update_task` |

## Security Considerations

1. All tools require `user_id` parameter to enforce data isolation
2. Tools must verify the task belongs to the specified user before any operation
3. Error messages must not leak information about other users' data
4. All tool invocations should be logged for audit purposes

## Stateless Design

All MCP tools are designed to be stateless:
- No in-memory state is maintained between tool invocations
- All state is persisted to and retrieved from the Neon PostgreSQL database
- Each tool invocation is independent and can be processed by any server instance
