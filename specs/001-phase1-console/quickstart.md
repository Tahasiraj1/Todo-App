# Quickstart Guide: Phase I - Todo Console App

**Date**: 2025-12-27  
**Feature**: Phase I - Todo Console App

## Prerequisites

- Python 3.13+ installed
- UV package manager installed
- Command-line terminal access

## Setup

1. **Install UV** (if not already installed):
   ```bash
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows (PowerShell)
   powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Initialize project** (if not already done):
   ```bash
   uv init
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

## Running the Application

**Start the application**:
```bash
python src/main.py
```

Or with UV:
```bash
uv run python src/main.py
```

## Basic Usage Examples

### 1. Add Tasks

```bash
todo add "Buy groceries"
todo add "Call mom" "Discuss weekend plans"
todo add "Finish homework"
```

### 2. View Tasks

```bash
todo list
```

**Expected Output**:
```
Tasks:
  1. [ ] Buy groceries
  2. [X] Call mom
      Description: Discuss weekend plans
  3. [ ] Finish homework

Total: 3 tasks (1 completed, 2 pending)
```

### 3. Mark Task Complete

```bash
todo complete 1
```

### 4. Update Task

```bash
todo update 1 --title "Buy groceries and fruits"
todo update 2 --description "From grocery store"
```

### 5. Delete Task

```bash
todo delete 3
```

## Complete Workflow Example

```bash
# 1. Add some tasks
todo add "Buy groceries"
todo add "Call mom" "Discuss weekend plans"
todo add "Finish homework"

# 2. View the list
todo list

# 3. Mark first task complete
todo complete 1

# 4. Update second task
todo update 2 --description "Call to discuss weekend"

# 5. View updated list
todo list

# 6. Delete third task
todo delete 3

# 7. Final list
todo list
```

## Getting Help

View help for any command:
```bash
todo --help
todo add --help
todo list --help
```

## Testing

Run tests:
```bash
uv run pytest
```

Run specific test file:
```bash
uv run pytest tests/unit/test_task.py
```

## Troubleshooting

### Application not found
- Ensure you're in the project root directory
- Check that `src/main.py` exists
- Verify Python 3.13+ is installed: `python --version`

### Command not recognized
- Ensure the application is properly installed
- Check that the CLI entry point is configured correctly

### Tasks not persisting
- This is expected behavior for Phase I (in-memory storage)
- Tasks are lost when the application exits
- Persistence will be added in Phase II

## Next Steps

After completing Phase I:
- Phase II: Add web interface and database persistence
- Phase III: Add AI chatbot interface
- Phase IV: Deploy to local Kubernetes
- Phase V: Deploy to cloud with event-driven architecture

