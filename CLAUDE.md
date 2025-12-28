# Claude Code Instructions

This project uses **Spec-Driven Development** with Claude Code. All code must be generated following the specification artifacts.

## Project Context

**Feature**: Phase I - Todo Console App  
**Branch**: `001-phase1-console`  
**Technology Stack**: Python 3.13+, UV, argparse, pytest

## Active Technologies

- Python 3.13+ (001-phase1-console)
- UV (package manager), Python standard library (argparse or click for CLI) (001-phase1-console)
- In-memory (Python list/dict) - no database persistence (001-phase1-console)

## Project Structure

```
src/
├── models/
│   └── task.py          # Task data model
├── services/
│   └── task_service.py  # Business logic for task operations
├── cli/
│   └── commands.py      # CLI command handlers
└── main.py              # Application entry point

tests/
├── unit/
│   ├── test_task.py
│   ├── test_task_service.py
│   └── test_commands.py
└── integration/
    └── test_cli_workflow.py
```

## Development Workflow

1. **Read Specifications**: Always check `specs/001-phase1-console/` before implementing
2. **Follow Tasks**: Reference `specs/001-phase1-console/tasks.md` for task IDs
3. **Reference Plan**: Check `specs/001-phase1-console/plan.md` for architecture
4. **Code Generation**: All code must reference Task IDs in comments

## Code Requirements

- **Task References**: Every code file must contain comments linking to Task IDs
- **Format**: `[Task]: T-XXX [From]: spec.md §X.X, plan.md §Y.Y`
- **File Paths**: Follow exact paths specified in tasks.md
- **Error Handling**: Use Python exceptions with user-friendly messages to stderr
- **CLI Framework**: Use argparse (standard library)

## Key Files

- **Constitution**: `.specify/memory/constitution.md` - Project principles
- **Specification**: `specs/001-phase1-console/spec.md` - Requirements
- **Plan**: `specs/001-phase1-console/plan.md` - Technical design
- **Tasks**: `specs/001-phase1-console/tasks.md` - Implementation tasks
- **Data Model**: `specs/001-phase1-console/data-model.md` - Entity definitions
- **Contracts**: `specs/001-phase1-console/contracts/cli-commands.md` - CLI specifications

## Recent Changes

- 001-phase1-console: Added Python 3.13+ + UV (package manager), Python standard library (argparse or click for CLI)

## Commands

- `cd src; pytest; ruff check .` (if ruff is configured)

## Language Conventions

Python 3.13+: Follow standard conventions
- Use type hints where appropriate
- Follow PEP 8 style guide
- Use docstrings for functions and classes
- Error messages to stderr, success messages to stdout

**Last updated**: 2025-12-27

