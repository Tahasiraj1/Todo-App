# Tasks: Phase I - Todo Console App

**Input**: Design documents from `/specs/001-phase1-console/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below follow the single project structure from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan (src/, tests/, src/models/, src/services/, src/cli/)
- [x] T002 Initialize Python project with UV package manager (create pyproject.toml in repository root)
- [x] T003 [P] Configure pytest for testing (add pytest to pyproject.toml dependencies)
- [x] T004 [P] Create README.md with setup instructions in repository root
- [x] T005 [P] Create CLAUDE.md with Claude Code instructions in repository root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 [P] Create Task model in src/models/task.py with id, title, description, completed, created_at fields
- [x] T007 Create in-memory task storage in src/services/task_service.py (initialize empty list for tasks)
- [x] T008 Implement task ID generation logic in src/services/task_service.py (sequential integer starting from 1)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add New Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks with a title and optional description. Tasks are assigned unique IDs and stored in memory.

**Independent Test**: Run the application and successfully add a task with a title. The task should be stored and retrievable, demonstrating core functionality works.

### Implementation for User Story 1

- [x] T009 [US1] Implement add_task method in src/services/task_service.py (creates task with title, optional description, assigns ID)
- [x] T010 [US1] Add title validation in src/services/task_service.py (reject empty titles, raise error)
- [x] T011 [US1] Implement add command handler in src/cli/commands.py (parse title and description arguments)
- [x] T012 [US1] Wire add command to task service in src/cli/commands.py (call add_task, display success message)
- [x] T013 [US1] Add error handling for empty title in src/cli/commands.py (catch validation error, print to stderr, exit code 1)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can add tasks via CLI.

---

## Phase 4: User Story 2 - View Task List (Priority: P1)

**Goal**: Users can view all tasks with their status indicators. Empty list shows appropriate message.

**Independent Test**: Add tasks and then view the list. The list should display all tasks with their status, demonstrating data persistence and retrieval.

### Implementation for User Story 2

- [x] T014 [US2] Implement get_all_tasks method in src/services/task_service.py (returns all tasks from storage)
- [x] T015 [US2] Implement list command handler in src/cli/commands.py (parse no arguments, call get_all_tasks)
- [x] T016 [US2] Format task list output in src/cli/commands.py (display ID, status [ ]/[X], title, description)
- [x] T017 [US2] Add empty list message in src/cli/commands.py (display "No tasks found. Use 'add' to create a task." when list is empty)
- [x] T018 [US2] Add task summary in src/cli/commands.py (display total count and completion breakdown)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can add and view tasks.

---

## Phase 5: User Story 3 - Mark Tasks as Complete (Priority: P2)

**Goal**: Users can toggle task completion status. Completed tasks show [X], pending tasks show [ ].

**Independent Test**: Add a task, mark it complete, and verify the status changed. This demonstrates state management and status updates.

### Implementation for User Story 3

- [x] T019 [US3] Implement toggle_complete method in src/services/task_service.py (find task by ID, toggle completed field)
- [x] T020 [US3] Add task not found error handling in src/services/task_service.py (raise TaskNotFoundError for invalid ID)
- [x] T021 [US3] Implement complete command handler in src/cli/commands.py (parse task ID argument)
- [x] T022 [US3] Wire complete command to task service in src/cli/commands.py (call toggle_complete, display status message)
- [x] T023 [US3] Add error handling for invalid ID in src/cli/commands.py (catch TaskNotFoundError, print to stderr, exit code 1)
- [x] T024 [US3] Add error handling for non-numeric ID in src/cli/commands.py (validate ID is integer, print error, exit code 1)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Users can add, view, and mark tasks complete.

---

## Phase 6: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Users can update task titles and/or descriptions. Unspecified fields remain unchanged.

**Independent Test**: Add a task, update its title or description, and verify the changes are saved. This demonstrates data modification capabilities.

### Implementation for User Story 4

- [x] T025 [US4] Implement update_task method in src/services/task_service.py (find task by ID, update title and/or description)
- [x] T026 [US4] Add validation for at least one field in src/services/task_service.py (require title or description to be provided)
- [x] T027 [US4] Add title validation in update_task in src/services/task_service.py (reject empty title if provided)
- [x] T028 [US4] Implement update command handler in src/cli/commands.py (parse task ID, --title, --description arguments)
- [x] T029 [US4] Wire update command to task service in src/cli/commands.py (call update_task, display success message)
- [x] T030 [US4] Add error handling for invalid ID in src/cli/commands.py (catch TaskNotFoundError, print to stderr, exit code 1)
- [x] T031 [US4] Add error handling for no update fields in src/cli/commands.py (validate at least one field provided, print error, exit code 1)
- [x] T032 [US4] Add error handling for empty title in src/cli/commands.py (catch validation error, print to stderr, exit code 1)

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently. Users can add, view, mark complete, and update tasks.

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P3)

**Goal**: Users can delete tasks by ID. Deleted tasks no longer appear in the list.

**Independent Test**: Add tasks, delete one by ID, and verify it no longer appears in the list. This demonstrates data removal capabilities.

### Implementation for User Story 5

- [x] T033 [US5] Implement delete_task method in src/services/task_service.py (find task by ID, remove from storage)
- [x] T034 [US5] Add task not found error handling in delete_task in src/services/task_service.py (raise TaskNotFoundError for invalid ID)
- [x] T035 [US5] Implement delete command handler in src/cli/commands.py (parse task ID argument)
- [x] T036 [US5] Wire delete command to task service in src/cli/commands.py (call delete_task, display success message)
- [x] T037 [US5] Add error handling for invalid ID in src/cli/commands.py (catch TaskNotFoundError, print to stderr, exit code 1)
- [x] T038 [US5] Add error handling for non-numeric ID in src/cli/commands.py (validate ID is integer, print error, exit code 1)

**Checkpoint**: At this point, all 5 user stories should be independently functional. Users can perform all CRUD operations.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T039 Create main entry point in src/main.py (setup argparse, register all commands, handle command routing)
- [x] T040 [P] Add help command support in src/cli/commands.py (display usage for --help or -h)
- [x] T041 [P] Add consistent error message formatting across all commands in src/cli/commands.py
- [x] T042 [P] Add consistent success message formatting across all commands in src/cli/commands.py
- [x] T043 [P] Update README.md with usage examples from quickstart.md
- [x] T044 [P] Update CLAUDE.md with project context and implementation guidance
- [x] T045 Run quickstart.md validation (test all commands work as documented)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Depends on US1 for data (tasks must exist to view)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for data (tasks must exist to mark complete)
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for data (tasks must exist to update)
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 for data (tasks must exist to delete)

**Note**: While stories depend on US1 for data, they are independently testable - you can add a task in US1, then test US2/US3/US4/US5 independently.

### Within Each User Story

- Models before services (Task model in Phase 2 before service methods)
- Service methods before CLI handlers
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005)
- Foundational task T006 can run in parallel with T007/T008 setup
- Once Foundational phase completes, user stories can start in parallel (if team capacity allows)
- Polish tasks marked [P] can run in parallel (T040, T041, T042, T043, T044)

---

## Parallel Example: User Story 1

```bash
# All US1 tasks are sequential (service → CLI → error handling)
# But can be worked on in logical groups:
# 1. Service layer (T009, T010)
# 2. CLI layer (T011, T012)
# 3. Error handling (T013)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add Tasks)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - can add tasks!)
3. Add User Story 2 → Test independently → Deploy/Demo (can view tasks)
4. Add User Story 3 → Test independently → Deploy/Demo (can mark complete)
5. Add User Story 4 → Test independently → Deploy/Demo (can update tasks)
6. Add User Story 5 → Test independently → Deploy/Demo (can delete tasks)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Add)
   - Developer B: User Story 2 (View) - can start after US1 has some tasks
   - Developer C: User Story 3 (Complete) - can start after US1 has some tasks
3. After US1-3 complete:
   - Developer A: User Story 4 (Update)
   - Developer B: User Story 5 (Delete)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks include exact file paths for clarity
- Error handling is part of each user story's implementation

