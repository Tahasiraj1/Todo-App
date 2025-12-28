# CLI Commands Contract: Phase I - Todo Console App

**Date**: 2025-12-27  
**Feature**: Phase I - Todo Console App  
**Interface Type**: Command-Line Interface (CLI)

## Command Overview

The application provides a command-line interface with the following commands:

1. `add` - Create a new task
2. `list` - View all tasks
3. `complete` - Mark a task as complete/incomplete
4. `update` - Update task title or description
5. `delete` - Remove a task

## Command Specifications

### 1. Add Task

**Command**: `add <title> [description]`

**Purpose**: Create a new task with a title and optional description.

**Arguments**:
- `title` (required, string): Task title. Must be non-empty.
- `description` (optional, string): Task description.

**Examples**:
```bash
todo add "Buy groceries"
todo add "Call mom" "Discuss weekend plans"
```

**Output** (stdout):
```
Task added: ID 1 - Buy groceries
```

**Errors** (stderr):
- Empty title: `Error: Task title cannot be empty`
- Exit code: 1

**Success Criteria**:
- Task is created with unique ID
- Task appears in list command
- Returns exit code 0

---

### 2. List Tasks

**Command**: `list`

**Purpose**: Display all tasks with their status.

**Arguments**: None

**Examples**:
```bash
todo list
```

**Output** (stdout):
```
Tasks:
  1. [ ] Buy groceries
      Description: Milk, eggs, bread
  2. [X] Call mom
      Description: Discuss weekend plans
  3. [ ] Finish homework

Total: 3 tasks (1 completed, 2 pending)
```

**Empty List Output**:
```
No tasks found. Use 'add' to create a task.
```

**Success Criteria**:
- All tasks displayed with ID, status, title, description
- Status indicators clearly show completed [X] vs pending [ ]
- Summary shows total count and completion breakdown
- Returns exit code 0

---

### 3. Mark Complete

**Command**: `complete <id>`

**Purpose**: Toggle task completion status.

**Arguments**:
- `id` (required, integer): Task ID to mark complete/incomplete.

**Examples**:
```bash
todo complete 1
todo complete 2
```

**Output** (stdout):
```
Task 1 marked as complete.
```
or
```
Task 2 marked as incomplete.
```

**Errors** (stderr):
- Invalid ID: `Error: Task with ID 99 not found`
- Non-numeric ID: `Error: Invalid task ID. Must be a number.`
- Exit code: 1

**Success Criteria**:
- Task status toggled (complete ↔ incomplete)
- Status change reflected in list command
- Returns exit code 0 on success

---

### 4. Update Task

**Command**: `update <id> [--title <title>] [--description <description>]`

**Purpose**: Update task title and/or description.

**Arguments**:
- `id` (required, integer): Task ID to update.
- `--title <title>` (optional, string): New task title.
- `--description <description>` (optional, string): New task description.

**Examples**:
```bash
todo update 1 --title "Buy groceries and fruits"
todo update 2 --description "From grocery store"
todo update 3 --title "Finish homework" --description "Math and science"
```

**Output** (stdout):
```
Task 1 updated successfully.
```

**Errors** (stderr):
- Invalid ID: `Error: Task with ID 99 not found`
- No update fields: `Error: At least one field (--title or --description) must be provided`
- Empty title: `Error: Task title cannot be empty`
- Exit code: 1

**Success Criteria**:
- Specified fields updated
- Changes reflected in list command
- Unspecified fields remain unchanged
- Returns exit code 0 on success

---

### 5. Delete Task

**Command**: `delete <id>`

**Purpose**: Remove a task from the list.

**Arguments**:
- `id` (required, integer): Task ID to delete.

**Examples**:
```bash
todo delete 1
```

**Output** (stdout):
```
Task 1 deleted successfully.
```

**Errors** (stderr):
- Invalid ID: `Error: Task with ID 99 not found`
- Non-numeric ID: `Error: Invalid task ID. Must be a number.`
- Exit code: 1

**Success Criteria**:
- Task removed from list
- Task no longer appears in list command
- Other task IDs remain unchanged
- Returns exit code 0 on success

---

## General Command Behavior

### Help Command

**Command**: `--help` or `-h` (for any command or main application)

**Purpose**: Display usage information.

**Examples**:
```bash
todo --help
todo add --help
```

### Error Handling

- All errors printed to stderr
- Success messages printed to stdout
- Exit code 0 for success, 1 for errors
- User-friendly error messages (no stack traces)

### Input Validation

- Task IDs must be positive integers
- Task titles cannot be empty
- All required arguments must be provided
- Invalid commands show usage/help

### Output Format

- Consistent formatting across all commands
- Clear status indicators ([ ] for pending, [X] for completed)
- Descriptive success/error messages
- Summary information where applicable (e.g., task counts)

