# Tasks: Phase V — Advanced Cloud Deployment

**Input**: Design documents from `/specs/005-cloud-event-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested. Test tasks omitted. Manual E2E verification at checkpoints.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- **Services**: `services/notification/`, `services/recurring-task/`
- **K8s**: `k8s/`
- **CI/CD**: `.github/workflows/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create new directories, files, and project scaffolding for Phase V services

- [x] T001 Create directory structure for new services: `services/notification/src/`, `services/recurring-task/src/`
- [x] T002 [P] Create `services/notification/requirements.txt` with FastAPI, uvicorn, httpx dependencies
- [x] T003 [P] Create `services/recurring-task/requirements.txt` with FastAPI, uvicorn, httpx dependencies
- [x] T004 [P] Create `services/notification/Dockerfile` (multi-stage Python build, matching backend pattern)
- [x] T005 [P] Create `services/recurring-task/Dockerfile` (multi-stage Python build, matching backend pattern)
- [x] T006 Create Kubernetes resource directories: `k8s/kafka/`, `k8s/dapr/`
- [x] T007 Create `.github/workflows/` directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend Task model and schemas — ALL user stories depend on these changes

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Extend Task SQLModel with new columns (priority, tags, due_date, is_recurring, recurrence_frequency, recurrence_interval, recurrence_day_of_week, recurrence_day_of_month, recurrence_end_date, reminder_sent) in `backend/src/models/task.py`
- [x] T009 Update TaskCreate schema with priority, tags, due_date, is_recurring, recurrence fields, and validation rules in `backend/src/models/schemas.py`
- [x] T010 Update TaskUpdate schema with priority, tags, due_date, is_recurring, recurrence fields in `backend/src/models/schemas.py`
- [x] T011 Update TaskResponse schema with priority, tags, due_date, is_overdue, is_recurring, recurrence fields in `backend/src/models/schemas.py`
- [x] T012 Update TypeScript Task types with priority, tags, due_date, is_overdue, is_recurring, recurrence fields in `frontend/src/types/task.ts`
- [x] T013 Create event schema models (TaskEvent, ReminderEvent, TaskUpdateEvent) per CloudEvents spec in `backend/src/models/events.py`
- [x] T014 Create ActivityLogEntry SQLModel in `backend/src/models/activity_log.py`
- [x] T015 Register new models for table creation in `backend/src/db.py` (import ActivityLogEntry)

**Checkpoint**: Task model extended, schemas updated, all new fields available. Foundation ready.

---

## Phase 3: User Story 1 — Task Priorities and Tags (Priority: P1) MVP

**Goal**: Users can assign priorities (high/medium/low) and tags to tasks via the chatbot

**Independent Test**: Create tasks with priorities and tags via chatbot, verify they persist and display

### Implementation for User Story 1

- [x] T016 [US1] Update TaskService.create_task() to accept and store priority and tags in `backend/src/services/task_service.py`
- [x] T017 [US1] Update TaskService.update_task() to accept and modify priority and tags in `backend/src/services/task_service.py`
- [x] T018 [US1] Update add_task MCP tool to accept priority and tags parameters in `backend/src/agent/tools.py`
- [x] T019 [US1] Update update_task MCP tool to accept priority and tags parameters in `backend/src/agent/tools.py`
- [x] T020 [US1] Update agent instructions to recognize priority/tag intents (e.g., "add a high-priority task", "tag it as work") in `backend/src/agent/agent.py`
- [x] T021 [P] [US1] Update task-item component with priority badge (color-coded) and tag chips in `frontend/src/components/tasks/task-item.tsx`
- [x] T022 [P] [US1] Update task-form component with priority selector dropdown and tag input in `frontend/src/components/tasks/task-form.tsx`
- [x] T023 [US1] Update frontend API client to include priority and tags in create/update requests in `frontend/src/lib/api.ts`

**Checkpoint**: Tasks can be created/updated with priorities and tags. Chatbot understands priority/tag commands.

---

## Phase 4: User Story 2 — Search, Filter, and Sort (Priority: P1)

**Goal**: Users can search tasks by keyword, filter by status/priority/tag, and sort by various fields

**Independent Test**: Create multiple tasks, then use chatbot to filter ("show high-priority tasks"), search ("search for report"), and sort ("sort by due date")

### Implementation for User Story 2

- [x] T024 [US2] Add filter/sort/search query parameters to GET /api/{user_id}/tasks route in `backend/src/api/routes/tasks.py`
- [x] T025 [US2] Implement TaskService.list_tasks() with filtering (priority, tag, status, overdue), search (title + description ILIKE), and sorting (due_date, priority, title, created_at) in `backend/src/services/task_service.py`
- [x] T026 [US2] Update list_tasks MCP tool to accept filter, sort, and search parameters in `backend/src/agent/tools.py`
- [x] T027 [US2] Update agent instructions to recognize filter/sort/search intents in `backend/src/agent/agent.py`
- [x] T028 [P] [US2] Create task-filters component with priority dropdown, tag filter, status toggle, sort selector, and search input in `frontend/src/components/tasks/task-filters.tsx`
- [x] T029 [US2] Integrate task-filters into dashboard page and connect to API with query params in `frontend/src/app/dashboard/page.tsx`
- [x] T030 [US2] Update frontend API client listTasks() to accept filter, sort, search parameters in `frontend/src/lib/api.ts`

**Checkpoint**: Tasks can be filtered, sorted, and searched via chatbot and UI.

---

## Phase 5: User Story 7 — Dapr Sidecar Integration (Priority: P1)

**Goal**: Dapr sidecars run alongside services; event publishing, service invocation, and secrets work via Dapr HTTP APIs

**Independent Test**: Deploy backend with Dapr sidecar on Minikube, publish a test event via Dapr API, verify event reaches subscriber

### Implementation for User Story 7

- [x] T031 [US7] Create Strimzi Kafka cluster manifest (single broker, ephemeral storage, 3 topics) in `k8s/kafka/kafka-cluster.yaml`
- [x] T032 [US7] Create Dapr pub/sub component YAML (kafka-pubsub, pointing to Strimzi broker) in `k8s/dapr/kafka-pubsub.yaml`
- [x] T033 [P] [US7] Create Dapr declarative subscription CRDs for task-events, reminders, and task-updates in `k8s/dapr/subscriptions.yaml`
- [x] T034 [P] [US7] Create Dapr Kubernetes secrets store component in `k8s/dapr/kubernetes-secrets.yaml`
- [x] T035 [US7] Add Dapr sidecar annotations to backend Helm deployment template in `k8s/helm/todo-chatbot/templates/backend-deployment.yaml`
- [x] T036 [US7] Add Dapr, Kafka, and new service configuration blocks to Helm values in `k8s/helm/todo-chatbot/values.yaml`
- [x] T037 [US7] Create EventService for publishing events via Dapr HTTP API (POST to localhost:3500/v1.0/publish/) in `backend/src/services/event_service.py`
- [x] T038 [US7] Integrate EventService into TaskService — publish TaskEvent to task-events and task-updates topics after each create/update/complete/delete in `backend/src/services/task_service.py`
- [x] T039 [US7] Add httpx dependency to backend requirements for Dapr HTTP calls in `backend/requirements.txt`

**Checkpoint**: Dapr sidecar runs with backend. Events publish to Kafka via Dapr. Infrastructure layer operational.

---

## Phase 6: User Story 8 — Cloud Kubernetes Deployment (Priority: P1)

**Goal**: Full application deployed and accessible on Oracle Cloud OKE

**Independent Test**: Access application via external URL on OKE, sign in, create/manage tasks

### Implementation for User Story 8

- [x] T040 [US8] Create values-oke.yaml with Oracle OKE overrides (OCIR image repos, ARM64, reduced resources, ingress enabled) in `k8s/helm/todo-chatbot/values-oke.yaml`
- [x] T041 [P] [US8] Create notification service Helm deployment template with Dapr annotations in `k8s/helm/todo-chatbot/templates/notification-deployment.yaml`
- [x] T042 [P] [US8] Create notification service Helm service template in `k8s/helm/todo-chatbot/templates/notification-service.yaml`
- [x] T043 [P] [US8] Create recurring-task service Helm deployment template with Dapr annotations in `k8s/helm/todo-chatbot/templates/recurring-task-deployment.yaml`
- [x] T044 [P] [US8] Create recurring-task service Helm service template in `k8s/helm/todo-chatbot/templates/recurring-task-service.yaml`
- [x] T045 [US8] Update backend and frontend Dockerfiles for multi-architecture build (ARM64 support) in `backend/Dockerfile` and `frontend/Dockerfile`
- [x] T046 [US8] Document Oracle OKE provisioning steps (create cluster, configure kubectl, OCIR login) in `docs/oke-deployment-guide.md`

**Checkpoint**: Application deployable to Oracle OKE via Helm. All pods reach Running state.

---

## Phase 7: User Story 3 — Due Dates and Reminders (Priority: P2)

**Goal**: Users set due dates on tasks, receive browser notifications or in-app banners when deadlines approach

**Independent Test**: Create task with near-future due date, verify reminder notification/banner appears

**Depends on**: Phase 5 (Dapr infrastructure)

### Implementation for User Story 3

- [x] T047 [US3] Create ReminderService to schedule/cancel Dapr Jobs when due_date is set/changed/removed in `backend/src/services/reminder_service.py`
- [x] T048 [US3] Create Dapr Jobs callback route handler — when job fires, publish to reminders topic in `backend/src/api/routes/jobs.py`
- [x] T049 [US3] Integrate ReminderService into TaskService — call schedule/cancel on create, update, delete when due_date is involved in `backend/src/services/task_service.py`
- [x] T050 [US3] Register jobs route in FastAPI app in `backend/src/main.py`
- [x] T051 [US3] Update add_task and update_task MCP tools to accept due_date parameter in `backend/src/agent/tools.py`
- [x] T052 [US3] Update agent instructions to recognize due date intents (e.g., "due tomorrow at 3pm") in `backend/src/agent/agent.py`
- [x] T053 [P] [US3] Add due date display and overdue indicator styling to task-item in `frontend/src/components/tasks/task-item.tsx`
- [x] T054 [P] [US3] Add date/time picker for due date in task-form in `frontend/src/components/tasks/task-form.tsx`
- [x] T055 [P] [US3] Create browser notification utility module (request permission, show notification) in `frontend/src/lib/notifications.ts`
- [x] T056 [US3] Create in-app reminder banner component (fallback when notifications denied) in `frontend/src/components/tasks/reminder-banner.tsx`

**Checkpoint**: Due dates can be set. Reminders fire via Dapr Jobs and deliver via browser notification or in-app banner.

---

## Phase 8: User Story 4 — Recurring Tasks (Priority: P2)

**Goal**: Completing a recurring task automatically creates the next occurrence

**Independent Test**: Create recurring task (e.g., "every Monday"), mark complete, verify next occurrence auto-created

**Depends on**: Phase 5 (Dapr infrastructure)

### Implementation for User Story 4

- [x] T057 [US4] Create recurring-task service FastAPI app with Dapr subscription handler in `services/recurring-task/src/main.py`
- [x] T058 [US4] Implement task-completed event handler — compute next due date from recurrence rule, create next task via Dapr service invocation to backend in `services/recurring-task/src/handlers.py`
- [x] T059 [US4] Update add_task and update_task MCP tools to accept recurrence parameters (is_recurring, frequency, interval, day_of_week, day_of_month) in `backend/src/agent/tools.py`
- [x] T060 [US4] Update agent instructions to recognize recurrence intents (e.g., "every Monday", "daily", "monthly on the 15th") in `backend/src/agent/agent.py`
- [x] T061 [P] [US4] Add recurrence pattern display to task-item (e.g., "Repeats weekly") in `frontend/src/components/tasks/task-item.tsx`
- [x] T062 [P] [US4] Add recurrence selector (frequency, interval, day) to task-form in `frontend/src/components/tasks/task-form.tsx`

**Checkpoint**: Completing a recurring task creates the next occurrence automatically via event pipeline.

---

## Phase 9: User Story 5 — Event-Driven Activity Log (Priority: P2)

**Goal**: All task operations are recorded; users can view recent activity

**Independent Test**: Perform task operations, ask chatbot "show my recent activity", verify all operations appear

**Depends on**: Phase 5 (Dapr infrastructure)

### Implementation for User Story 5

- [x] T063 [US5] Create ActivityService with methods: log_event(), list_entries(), purge_old_entries() in `backend/src/services/activity_service.py`
- [x] T064 [US5] Create Dapr subscription handler route for task-events topic — persist to activity_log table (idempotent by event ID) in `backend/src/api/routes/events.py`
- [x] T065 [US5] Create activity log API route GET /api/{user_id}/activity with limit/offset pagination in `backend/src/api/routes/activity.py`
- [x] T066 [US5] Register events and activity routes in FastAPI app in `backend/src/main.py`
- [x] T067 [P] [US5] Create activity-log frontend component (list of recent operations with timestamps) in `frontend/src/components/activity/activity-log.tsx`
- [x] T068 [US5] Add activity log API calls (getActivity) to frontend API client in `frontend/src/lib/api.ts`
- [x] T069 [US5] Add activity log view to dashboard or as separate page in `frontend/src/app/dashboard/page.tsx`

**Checkpoint**: Activity log records all task mutations. Users can view recent activity.

---

## Phase 10: User Story 9 — CI/CD Pipeline (Priority: P2)

**Goal**: Push to main triggers automated build, test, and deploy to Oracle OKE

**Independent Test**: Push a commit, verify GitHub Actions runs all stages and updates cloud deployment

**Depends on**: Phase 6 (Cloud deployment)

### Implementation for User Story 9

- [x] T070 [US9] Create GitHub Actions workflow with stages: checkout, test (pytest + npm test), build (multi-arch Docker), push (OCIR), deploy (helm upgrade) in `.github/workflows/deploy.yaml`
- [x] T071 [US9] Document required GitHub Secrets (OCI_CLI_USER, OCI_CLI_TENANCY, OCI_CLI_FINGERPRINT, OCI_CLI_KEY_CONTENT, OCI_CLI_REGION, OKE_CLUSTER_OCID, OCIR_USERNAME, OCIR_TOKEN) in `docs/ci-cd-setup.md`
- [x] T072 [US9] Add test stage to pipeline: run pytest for backend, npm test for frontend, halt on failure in `.github/workflows/deploy.yaml`

**Checkpoint**: CI/CD pipeline deploys on push. Failed tests block deployment.

---

## Phase 11: User Story 6 — Real-Time Sync Across Clients (Priority: P3)

**Goal**: Task changes in one browser tab appear in all other open tabs within 3 seconds

**Independent Test**: Open two browser tabs, create/complete a task in one, verify it appears/updates in the other

**Depends on**: Phase 5 (Dapr infrastructure)

### Implementation for User Story 6

- [x] T073 [US6] Create WebSocket connection manager (track connections per user_id, broadcast, cleanup) in `backend/src/services/websocket_manager.py`
- [x] T074 [US6] Create WebSocket endpoint at /api/ws/{user_id} with JWT auth in `backend/src/api/routes/websocket.py`
- [x] T075 [US6] Create notification service FastAPI app subscribing to reminders and task-updates topics in `services/notification/src/main.py`
- [x] T076 [US6] Implement notification service handlers — forward task-updates to backend WebSocket endpoint, forward reminders to user's WebSocket in `services/notification/src/handlers.py`
- [x] T077 [US6] Register WebSocket route in FastAPI app in `backend/src/main.py`
- [x] T078 [P] [US6] Create WebSocket client library (connect, reconnect, handle messages) in `frontend/src/lib/websocket.ts`
- [x] T079 [US6] Create notification-provider component (WebSocket + browser notifications + task list refresh) in `frontend/src/components/notifications/notification-provider.tsx`
- [x] T080 [US6] Integrate notification-provider into dashboard page for WebSocket connection in `frontend/src/app/dashboard/page.tsx`

**Checkpoint**: Real-time sync operational. Changes in one tab reflect in all open tabs.

---

## Phase 12: User Story 10 — Monitoring and Observability (Priority: P3)

**Goal**: Structured logging, health checks, and event monitoring for production operations

**Independent Test**: Deploy app, verify structured logs appear, health checks pass, Kafka events are logged

### Implementation for User Story 10

- [x] T081 [P] [US10] Add structured JSON logging configuration to backend (replace print statements with structured logger) in `backend/src/main.py`
- [x] T082 [P] [US10] Add structured JSON logging to notification service in `services/notification/src/main.py`
- [x] T083 [P] [US10] Add structured JSON logging to recurring-task service in `services/recurring-task/src/main.py`
- [x] T084 [US10] Add event publishing/consumption logging (topic, event_type, timestamp) to EventService in `backend/src/services/event_service.py`
- [x] T085 [US10] Verify health check endpoints return correct status for all services (backend /health, frontend /api/health, new services /health)

**Checkpoint**: All services produce structured JSON logs. Health checks operational. Event flow observable.

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Integration testing, documentation, cleanup

- [x] T086 End-to-end verification on Minikube: deploy all services, test full event pipeline (create task → event published → activity logged → real-time sync → reminder fires)
- [x] T087 End-to-end verification on Oracle OKE: repeat E2E test on cloud cluster
- [x] T088 [P] Update Helm chart README with Phase V configuration options in `k8s/helm/todo-chatbot/README.md`
- [x] T089 [P] Update project README with Phase V features, architecture diagram, and deployment instructions in `README.md`
- [x] T090 Run quickstart.md verification checklist against deployed application

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational — Task model + schemas)
    │
    ├──▶ Phase 3 (US1: Priorities & Tags) ← MVP
    │       │
    │       ▼
    ├──▶ Phase 4 (US2: Search/Filter/Sort)
    │
    ├──▶ Phase 5 (US7: Dapr & Kafka Infrastructure)
    │       │
    │       ├──▶ Phase 7  (US3: Due Dates & Reminders)
    │       ├──▶ Phase 8  (US4: Recurring Tasks)
    │       ├──▶ Phase 9  (US5: Activity Log)
    │       └──▶ Phase 11 (US6: Real-Time Sync)
    │
    └──▶ Phase 6 (US8: Cloud Deployment)
            │
            └──▶ Phase 10 (US9: CI/CD Pipeline)

Phase 12 (US10: Monitoring) — can start after Phase 2, no hard dependencies
Phase 13 (Polish) — after all desired phases complete
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|-----------|-------------------|
| US1 (Priorities & Tags) | Phase 2 only | US2, US7, US8 |
| US2 (Search/Filter/Sort) | Phase 2 only | US1, US7, US8 |
| US7 (Dapr Integration) | Phase 2 only | US1, US2, US8 |
| US8 (Cloud Deployment) | Phase 2 only | US1, US2, US7 |
| US3 (Due Dates/Reminders) | US7 (Dapr infra) | US4, US5, US6 |
| US4 (Recurring Tasks) | US7 (Dapr infra) | US3, US5, US6 |
| US5 (Activity Log) | US7 (Dapr infra) | US3, US4, US6 |
| US6 (Real-Time Sync) | US7 (Dapr infra) | US3, US4, US5 |
| US9 (CI/CD) | US8 (Cloud deploy) | US3-US6 |
| US10 (Monitoring) | Phase 2 only | All others |

### Within Each User Story

- Models before services
- Services before API routes
- Backend before frontend (API must exist for UI to call)
- MCP tools after service layer (tools delegate to services)
- Agent instructions after tools (agent uses tools)

---

## Parallel Opportunities

### After Phase 2 (Foundational) — 4 parallel streams:

```
Stream A: US1 (Priorities & Tags) → US2 (Search/Filter/Sort)
Stream B: US7 (Dapr Infrastructure) → US3, US4, US5, US6 (event features)
Stream C: US8 (Cloud Deployment) → US9 (CI/CD)
Stream D: US10 (Monitoring)
```

### Within Phase 5 (Dapr Infrastructure):

```
Parallel: T032 (pub/sub) + T033 (subscriptions) + T034 (secrets store)
Then: T035 (Helm annotations) → T036 (values) → T037 (EventService) → T038 (integration)
```

### Within Phase 6 (Cloud Deployment):

```
Parallel: T041 + T042 + T043 + T044 (all Helm templates for new services)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (model + schema changes)
3. Complete Phase 3: US1 — Priorities & Tags
4. **STOP and VALIDATE**: Create tasks with priorities/tags via chatbot
5. Commit and demo

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 (Priorities & Tags) → MVP!
3. US2 (Search/Filter/Sort) → Enhanced listing
4. US7 (Dapr Infrastructure) → Event backbone
5. US3 (Due Dates) + US4 (Recurring) + US5 (Activity Log) → Event-driven features
6. US6 (Real-Time Sync) → Polish
7. US8 (Cloud) → Production deployment
8. US9 (CI/CD) → Automated pipeline
9. US10 (Monitoring) + Polish → Production-ready

### Recommended Execution Order (single developer)

1. Phase 1 → 2 → 3 → 4 (task model + UI features)
2. Phase 5 (Dapr/Kafka infra)
3. Phase 7 → 8 → 9 (event-driven features)
4. Phase 11 (real-time sync)
5. Phase 6 → 10 (cloud deployment + CI/CD)
6. Phase 12 → 13 (monitoring + polish)

---

## Notes

- [P] tasks = different files, no dependencies on other in-progress tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate the story independently
- Total: 90 tasks across 13 phases covering 10 user stories
