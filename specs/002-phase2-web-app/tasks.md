# Tasks: Phase II - Todo Full-Stack Web Application

**Input**: Design documents from `/specs/002-phase2-web-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - not explicitly requested in specification, so test tasks are not included. Focus on implementation tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2], [US3])
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/` (monorepo structure)
- Paths follow plan.md structure: separate frontend and backend directories

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create monorepo structure with `backend/` and `frontend/` directories at repository root
- [ ] T002 Initialize Next.js 16+ project in `frontend/` with TypeScript and App Router
- [ ] T003 [P] Initialize FastAPI project in `backend/` with Python 3.13+ and requirements.txt
- [ ] T004 [P] Configure Tailwind CSS in `frontend/` for styling
- [ ] T005 [P] Initialize shadcn/ui in `frontend/` with components.json configuration
- [ ] T006 [P] Setup environment variable management (`.env.local` for frontend, `.env` for backend)
- [ ] T007 [P] Configure ESLint and Prettier in `frontend/` for code quality
- [ ] T008 [P] Configure Ruff or Black in `backend/` for Python code formatting
- [ ] T009 Create README.md with project overview and setup instructions
- [ ] T010 Create CLAUDE.md with Claude Code instructions (already exists, update for Phase II)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 Setup Neon PostgreSQL database connection in `backend/src/db.py` with SQLModel
- [ ] T012 Create database migration script or SQL schema file in `backend/migrations/` for users and tasks tables
- [ ] T013 [P] Create User SQLModel in `backend/src/models/user.py` (minimal, Better Auth manages auth)
- [ ] T014 [P] Create Task SQLModel in `backend/src/models/task.py` with all fields and relationships
- [ ] T015 [P] Create Pydantic schemas for Task (TaskCreate, TaskUpdate, TaskResponse) in `backend/src/models/schemas.py`
- [ ] T016 Implement database session management and connection pooling in `backend/src/db.py`
- [ ] T017 [P] Create JWT verification middleware in `backend/src/middleware/auth.py` to extract user_id from token
- [ ] T018 [P] Configure Better Auth in `frontend/src/lib/auth.ts` with JWT plugin enabled
- [ ] T019 [P] Create API client utility in `frontend/src/lib/api.ts` with JWT token attachment and error handling
- [ ] T020 Setup FastAPI app structure in `backend/src/main.py` with CORS configuration
- [ ] T021 Configure FastAPI dependency for authenticated user extraction in `backend/src/api/dependencies.py`
- [ ] T022 [P] Add zxcvbn password validation library to frontend dependencies
- [ ] T023 Setup error handling middleware in `backend/src/middleware/error_handler.py` for consistent error responses
- [ ] T024 Create TypeScript types for Task entity in `frontend/src/types/task.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts and sign in securely using Better Auth with JWT tokens

**Independent Test**: Create a new account, sign in, and verify that the session is established with JWT token. Can be tested independently without any task management features.

### Implementation for User Story 1

- [ ] T025 [P] [US1] Install and configure Better Auth in `frontend/package.json` with JWT plugin
- [ ] T026 [P] [US1] Create sign-up page at `frontend/src/app/(auth)/sign-up/page.tsx` with email, password, and name fields
- [ ] T027 [P] [US1] Create sign-in page at `frontend/src/app/(auth)/sign-in/page.tsx` with email and password fields
- [ ] T028 [US1] Implement password validation using zxcvbn with minimum pass score of 3 in `frontend/src/components/auth/password-input.tsx`
- [ ] T029 [US1] Add email format validation in sign-up form at `frontend/src/app/(auth)/sign-up/page.tsx`
- [ ] T030 [US1] Implement Better Auth sign-up handler in `frontend/src/app/(auth)/sign-up/page.tsx` with error handling
- [ ] T031 [US1] Implement Better Auth sign-in handler in `frontend/src/app/(auth)/sign-in/page.tsx` with error handling
- [ ] T032 [US1] Create sign-out functionality in `frontend/src/components/auth/sign-out-button.tsx`
- [ ] T033 [US1] Implement redirect to dashboard after successful sign-up in `frontend/src/app/(auth)/sign-up/page.tsx`
- [ ] T034 [US1] Implement redirect to dashboard after successful sign-in in `frontend/src/app/(auth)/sign-in/page.tsx`
- [ ] T035 [US1] Add user-friendly error messages for duplicate email registration in `frontend/src/app/(auth)/sign-up/page.tsx`
- [ ] T036 [US1] Add user-friendly error messages for invalid credentials in `frontend/src/app/(auth)/sign-in/page.tsx`
- [ ] T037 [US1] Use shadcn/ui Button, Input, and Label components in authentication forms
- [ ] T038 [US1] Create protected route middleware to redirect unauthenticated users in `frontend/src/middleware.ts`

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, sign in, and receive JWT tokens. Authentication is complete and testable independently.

---

## Phase 4: User Story 2 - Create and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable authenticated users to create new tasks and view all their tasks through a web interface

**Independent Test**: Sign in, create a task with title and optional description, and verify it appears in the task list. Can be tested independently after authentication is complete.

### Implementation for User Story 2

- [ ] T039 [P] [US2] Create TaskService in `backend/src/services/task_service.py` with create and list methods
- [ ] T040 [US2] Implement create_task method in `backend/src/services/task_service.py` with user_id filtering and validation
- [ ] T041 [US2] Implement list_tasks method in `backend/src/services/task_service.py` filtering by authenticated user_id
- [ ] T042 [P] [US2] Create POST /api/tasks endpoint in `backend/src/api/routes/tasks.py` for task creation
- [ ] T043 [P] [US2] Create GET /api/tasks endpoint in `backend/src/api/routes/tasks.py` for listing tasks
- [ ] T044 [US2] Add request validation for task creation (title required, 1-200 chars, description optional, max 1000 chars) in `backend/src/api/routes/tasks.py`
- [ ] T045 [US2] Add user_id extraction from JWT token in task endpoints using auth dependency in `backend/src/api/routes/tasks.py`
- [ ] T046 [P] [US2] Create dashboard page at `frontend/src/app/dashboard/page.tsx` with task list display
- [ ] T047 [P] [US2] Create TaskForm component in `frontend/src/components/tasks/task-form.tsx` with title and description fields
- [ ] T048 [US2] Implement task creation API call in `frontend/src/lib/api.ts` for POST /api/tasks
- [ ] T049 [US2] Implement task list API call in `frontend/src/lib/api.ts` for GET /api/tasks
- [ ] T050 [US2] Add client-side validation for task form (title required, length constraints) in `frontend/src/components/tasks/task-form.tsx`
- [ ] T051 [US2] Create TaskList component in `frontend/src/components/tasks/task-list.tsx` to display tasks
- [ ] T052 [US2] Create TaskItem component in `frontend/src/components/tasks/task-item.tsx` to display individual task with title, description, status, timestamps
- [ ] T053 [US2] Implement empty state message with "Add your first task" call-to-action in `frontend/src/components/tasks/task-list.tsx`
- [ ] T054 [US2] Add error handling for task creation validation errors in `frontend/src/components/tasks/task-form.tsx`
- [ ] T055 [US2] Use shadcn/ui components (Button, Input, Label) in task form and list components
- [ ] T056 [US2] Implement task list refresh after successful task creation in `frontend/src/app/dashboard/page.tsx`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can authenticate, create tasks, and view their task list.

---

## Phase 5: User Story 3 - Update Task Details (Priority: P2)

**Goal**: Enable authenticated users to modify existing task details (title and description)

**Independent Test**: Create a task, then edit its title or description, and verify the changes are saved and displayed. Can be tested independently.

### Implementation for User Story 3

- [ ] T057 [US3] Implement update_task method in `backend/src/services/task_service.py` with user_id verification
- [ ] T058 [P] [US3] Create PUT /api/tasks/{id} endpoint in `backend/src/api/routes/tasks.py` for task updates
- [ ] T059 [US3] Add authorization check in update endpoint to verify task belongs to authenticated user in `backend/src/api/routes/tasks.py`
- [ ] T060 [US3] Add request validation for task updates (title optional but 1-200 chars if provided, description optional, max 1000 chars) in `backend/src/api/routes/tasks.py`
- [ ] T061 [P] [US3] Create TaskEditDialog component in `frontend/src/components/tasks/task-edit-dialog.tsx` using shadcn/ui Dialog
- [ ] T062 [US3] Implement task update API call in `frontend/src/lib/api.ts` for PUT /api/tasks/{id}
- [ ] T063 [US3] Add edit button to TaskItem component in `frontend/src/components/tasks/task-item.tsx`
- [ ] T064 [US3] Implement edit form with pre-filled task data in `frontend/src/components/tasks/task-edit-dialog.tsx`
- [ ] T065 [US3] Add client-side validation for task updates in `frontend/src/components/tasks/task-edit-dialog.tsx`
- [ ] T066 [US3] Add error handling for update validation errors and authorization errors in `frontend/src/components/tasks/task-edit-dialog.tsx`
- [ ] T067 [US3] Update task list after successful task update in `frontend/src/components/tasks/task-list.tsx`
- [ ] T068 [US3] Display updated timestamp in TaskItem component in `frontend/src/components/tasks/task-item.tsx`

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - users can authenticate, create, view, and update tasks.

---

## Phase 6: User Story 4 - Mark Tasks as Complete (Priority: P2)

**Goal**: Enable authenticated users to mark tasks as complete or incomplete to track progress

**Independent Test**: Create a task, mark it as complete, verify the visual indicator changes, then toggle it back to incomplete. Can be tested independently.

### Implementation for User Story 4

- [ ] T069 [US4] Implement toggle_task_completion method in `backend/src/services/task_service.py` with user_id verification
- [ ] T070 [P] [US4] Create PATCH /api/tasks/{id}/complete endpoint in `backend/src/api/routes/tasks.py` for toggling completion
- [ ] T071 [US4] Add authorization check in toggle endpoint to verify task belongs to authenticated user in `backend/src/api/routes/tasks.py`
- [ ] T072 [P] [US4] Implement task toggle completion API call in `frontend/src/lib/api.ts` for PATCH /api/tasks/{id}/complete
- [ ] T073 [US4] Add checkbox or toggle button to TaskItem component in `frontend/src/components/tasks/task-item.tsx`
- [ ] T074 [US4] Implement visual indicator for completed tasks (strikethrough, different color) in `frontend/src/components/tasks/task-item.tsx`
- [ ] T075 [US4] Add click handler for completion toggle in TaskItem component in `frontend/src/components/tasks/task-item.tsx`
- [ ] T076 [US4] Update task list after successful completion toggle in `frontend/src/components/tasks/task-list.tsx`
- [ ] T077 [US4] Use shadcn/ui Checkbox component for completion indicator in `frontend/src/components/tasks/task-item.tsx`

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently - users can authenticate, create, view, update, and toggle task completion.

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P2)

**Goal**: Enable authenticated users to delete tasks with confirmation dialog

**Independent Test**: Create a task, delete it with confirmation, and verify it no longer appears in the task list. Can be tested independently.

### Implementation for User Story 5

- [ ] T078 [US5] Implement delete_task method in `backend/src/services/task_service.py` with user_id verification
- [ ] T079 [P] [US5] Create DELETE /api/tasks/{id} endpoint in `backend/src/api/routes/tasks.py` for task deletion
- [ ] T080 [US5] Add authorization check in delete endpoint to verify task belongs to authenticated user in `backend/src/api/routes/tasks.py`
- [ ] T081 [P] [US5] Implement task delete API call in `frontend/src/lib/api.ts` for DELETE /api/tasks/{id}
- [ ] T082 [US5] Create DeleteTaskDialog component in `frontend/src/components/tasks/delete-task-dialog.tsx` using shadcn/ui Dialog
- [ ] T083 [US5] Add "Are you sure you want to delete this task?" message in DeleteTaskDialog component
- [ ] T084 [US5] Add Cancel and Delete buttons in DeleteTaskDialog component using shadcn/ui Button
- [ ] T085 [US5] Add delete button to TaskItem component in `frontend/src/components/tasks/task-item.tsx`
- [ ] T086 [US5] Implement delete confirmation flow (open dialog, confirm/cancel) in TaskItem component
- [ ] T087 [US5] Add error handling for delete authorization errors in DeleteTaskDialog component
- [ ] T088 [US5] Update task list after successful task deletion in `frontend/src/components/tasks/task-list.tsx`

**Checkpoint**: At this point, User Stories 1, 2, 3, 4, AND 5 should all work independently - users can authenticate, create, view, update, toggle completion, and delete tasks. Basic CRUD functionality is complete.

---

## Phase 8: User Story 6 - Responsive Web Interface (Priority: P3)

**Goal**: Ensure the application works on desktop, tablet, and mobile devices with responsive design

**Independent Test**: Access the application on different screen sizes (320px to 2560px) and verify all functionality remains accessible and usable. Can be tested independently.

### Implementation for User Story 6

- [ ] T089 [US6] Add responsive Tailwind CSS classes to dashboard layout in `frontend/src/app/dashboard/page.tsx`
- [ ] T090 [US6] Make task form responsive for mobile screens in `frontend/src/components/tasks/task-form.tsx`
- [ ] T091 [US6] Make task list responsive with proper mobile layout in `frontend/src/components/tasks/task-list.tsx`
- [ ] T092 [US6] Make task item components touch-friendly for mobile in `frontend/src/components/tasks/task-item.tsx`
- [ ] T093 [US6] Add responsive navigation and layout in `frontend/src/app/layout.tsx`
- [ ] T094 [US6] Ensure authentication forms are responsive in `frontend/src/app/(auth)/sign-in/page.tsx` and `frontend/src/app/(auth)/sign-up/page.tsx`
- [ ] T095 [US6] Test responsive design at breakpoints: 320px (mobile), 768px (tablet), 1024px (desktop), 2560px (large desktop)
- [ ] T096 [US6] Ensure all shadcn/ui components are responsive and work on mobile devices

**Checkpoint**: At this point, all user stories should work independently and the application is fully responsive across all device sizes.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T097 [P] Implement silent token refresh on 401 responses in `frontend/src/lib/api.ts`
- [ ] T098 [P] Add redirect to sign-in page if token refresh fails in `frontend/src/lib/api.ts`
- [ ] T099 [P] Add loading states for all API operations in frontend components
- [ ] T100 [P] Add error boundary components for graceful error handling in `frontend/src/components/error-boundary.tsx`
- [ ] T101 [P] Implement consistent error message display across all forms using shadcn/ui components
- [ ] T102 [P] Add logging for all task operations in `backend/src/services/task_service.py`
- [ ] T103 [P] Add logging for authentication events in backend middleware
- [ ] T104 [P] Optimize database queries with proper indexing (verify indexes exist from migration)
- [ ] T105 [P] Add input sanitization for special characters and unicode in task titles/descriptions
- [ ] T106 [P] Update README.md with complete setup instructions and deployment guide
- [ ] T107 [P] Validate quickstart.md instructions by following them step-by-step
- [ ] T108 [P] Add API response time monitoring to ensure SC-005 (500ms response time) is met
- [ ] T109 [P] Test concurrent user scenarios to ensure SC-011 (no data corruption) is met
- [ ] T110 [P] Verify all success criteria from spec.md are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Authentication**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1) - Create/View Tasks**: Can start after Foundational (Phase 2) - Depends on US1 (authentication required)
- **User Story 3 (P2) - Update Tasks**: Can start after Foundational (Phase 2) - Depends on US2 (tasks must exist to update)
- **User Story 4 (P2) - Mark Complete**: Can start after Foundational (Phase 2) - Depends on US2 (tasks must exist to toggle)
- **User Story 5 (P2) - Delete Tasks**: Can start after Foundational (Phase 2) - Depends on US2 (tasks must exist to delete)
- **User Story 6 (P3) - Responsive Design**: Can start after Foundational (Phase 2) - Can work on existing UI components, no functional dependencies

### Within Each User Story

- Backend services before API endpoints
- API endpoints before frontend components
- Models before services (already in Foundational phase)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes:
  - US1 can start immediately
  - US2 can start after US1 completes (needs authentication)
  - US3, US4, US5 can start after US2 completes (need tasks to exist)
  - US6 can start in parallel with any story (responsive design improvements)
- All tasks marked [P] within a user story can run in parallel
- Different user stories can be worked on in parallel by different team members (respecting dependencies)

---

## Parallel Example: User Story 2

```bash
# Launch all parallel tasks for User Story 2 together:
Task: "Create TaskService in backend/src/services/task_service.py"
Task: "Create POST /api/tasks endpoint in backend/src/api/routes/tasks.py"
Task: "Create GET /api/tasks endpoint in backend/src/api/routes/tasks.py"
Task: "Create dashboard page at frontend/src/app/dashboard/page.tsx"
Task: "Create TaskForm component in frontend/src/components/tasks/task-form.tsx"
Task: "Create TaskList component in frontend/src/components/tasks/task-list.tsx"
Task: "Create TaskItem component in frontend/src/components/tasks/task-item.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. Complete Phase 4: User Story 2 (Create/View Tasks)
5. **STOP and VALIDATE**: Test User Stories 1 & 2 independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Authentication) → Test independently → Deploy/Demo
3. Add User Story 2 (Create/View Tasks) → Test independently → Deploy/Demo (MVP!)
4. Add User Story 3 (Update Tasks) → Test independently → Deploy/Demo
5. Add User Story 4 (Mark Complete) → Test independently → Deploy/Demo
6. Add User Story 5 (Delete Tasks) → Test independently → Deploy/Demo
7. Add User Story 6 (Responsive Design) → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication) - BLOCKS others
   - Once US1 complete:
     - Developer A: User Story 2 (Create/View Tasks)
     - Developer B: User Story 3 (Update Tasks) - can start after US2
     - Developer C: User Story 4 (Mark Complete) - can start after US2
   - Once US2 complete:
     - Developer A: User Story 5 (Delete Tasks)
     - Developer B: User Story 6 (Responsive Design) - can work in parallel
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks must reference Task IDs in code comments: `[Task]: T-XXX [From]: spec.md §X.X, plan.md §Y.Y`
- Use shadcn MCP server to discover and implement UI components
- Follow constitution principles: Spec-Driven Development, AI-Native Implementation, Stateless Architecture

---

## Task Summary

**Total Tasks**: 110

**Tasks by Phase**:
- Phase 1 (Setup): 10 tasks
- Phase 2 (Foundational): 14 tasks
- Phase 3 (US1 - Authentication): 14 tasks
- Phase 4 (US2 - Create/View Tasks): 18 tasks
- Phase 5 (US3 - Update Tasks): 12 tasks
- Phase 6 (US4 - Mark Complete): 9 tasks
- Phase 7 (US5 - Delete Tasks): 11 tasks
- Phase 8 (US6 - Responsive Design): 8 tasks
- Phase 9 (Polish): 14 tasks

**Tasks by User Story**:
- US1 (Authentication): 14 tasks
- US2 (Create/View Tasks): 18 tasks
- US3 (Update Tasks): 12 tasks
- US4 (Mark Complete): 9 tasks
- US5 (Delete Tasks): 11 tasks
- US6 (Responsive Design): 8 tasks

**Parallel Opportunities**: 45+ tasks marked with [P] can run in parallel

**Suggested MVP Scope**: Phases 1-4 (Setup + Foundational + US1 + US2) = 56 tasks

