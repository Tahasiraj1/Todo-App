# Data Model: Phase I - Todo Console App

**Date**: 2025-12-27  
**Feature**: Phase I - Todo Console App

## Entities

### Task

Represents a single todo item stored in memory.

**Fields**:
- `id` (integer, required, auto-generated): Unique identifier for the task. Sequential, starting from 1.
- `title` (string, required, non-empty): Task title. Must be at least 1 character, no maximum length enforced (but reasonable limits apply for CLI display).
- `description` (string, optional): Task description. Can be empty or None.
- `completed` (boolean, required, default: false): Completion status. True if task is completed, False if pending.
- `created_at` (datetime, optional): Timestamp when task was created. Included for good practice, though not strictly required for Phase I.

**Validation Rules**:
- `id`: Must be positive integer, auto-generated, unique within session
- `title`: Cannot be empty string, cannot be None, must be at least 1 character
- `description`: Can be None or empty string (optional field)
- `completed`: Must be boolean (True or False)

**State Transitions**:
- Task creation: `completed = False` (default)
- Mark complete: `completed = True`
- Mark incomplete: `completed = False`
- Update: `title` and/or `description` can be modified, `completed` status unchanged unless explicitly toggled

**Relationships**:
- None (Phase I is single-entity, no relationships)

## Data Storage

**Storage Type**: In-memory Python `list` of `dict` objects (or Task model instances)

**Structure**:
```python
tasks = [
    {
        "id": 1,
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": False,
        "created_at": datetime(2025, 12, 27, 10, 30, 0)
    },
    # ... more tasks
]
```

**Access Patterns**:
- Add: Append to list, assign sequential ID
- View: Iterate entire list
- Update: Find by ID, modify fields
- Delete: Find by ID, remove from list
- Mark complete: Find by ID, toggle `completed` field

**Constraints**:
- IDs are sequential and unique within session
- No persistence - data lost on application exit
- No maximum task limit (practical limit: memory constraints)

## Data Integrity

**Guarantees**:
- Task IDs are unique within a session
- Task IDs are sequential (no gaps unless tasks deleted)
- All tasks have required fields populated
- No orphaned or invalid task states

**No Guarantees** (by design for Phase I):
- Data persistence across sessions
- Concurrent access safety (single-user, single-threaded)
- Transactional consistency (simple in-memory operations)

