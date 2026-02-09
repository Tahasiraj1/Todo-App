# Tasks: Phase 5 Testing Plan

**Input**: Design documents from `/specs/006-phase5-testing-plan/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/ (complete)

**Tests**: This feature IS a testing feature — tasks execute test cases, not write code. No separate test tasks needed.

**Organization**: Tasks are grouped by test execution phase (maps to user stories in spec.md). Phases are sequential — each depends on the previous phase passing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (independent kubectl commands or browser actions)
- **[Story]**: Which user story from spec.md (US1-US9)
- Tool context: `[kubectl]` for infrastructure, `[Playwright]` for browser, `[Report]` for documentation

## Path Conventions

- Infrastructure checks: kubectl against OKE cluster (todo-app, dapr-system, kafka namespaces)
- Browser tests: Playwright MCP against `https://todo.tahasiraj.com`
- Screenshots: `.playwright-mcp/` directory
- Report output: `specs/006-phase5-testing-plan/` directory

---

## Phase 1: Setup (Prerequisites Verification)

**Purpose**: Verify test environment is ready before executing any tests

- [x] T001 Verify WSL /etc/hosts contains `104.21.23.140 todo.tahasiraj.com` entry
- [x] T002 [P] Verify kubectl is configured and can reach OKE cluster via `kubectl get nodes`
- [x] T003 [P] Verify Playwright MCP is available by navigating to a test URL

**Checkpoint**: Test environment confirmed ready — infrastructure checks can begin

---

## Phase 2: Foundational (Infrastructure Verification — kubectl)

**Purpose**: Verify cloud deployment infrastructure is healthy. BLOCKS all browser tests.

**⚠️ CRITICAL**: If any infrastructure check fails, abort browser testing and investigate.

- [x] T004 [P] [US7] Run `kubectl get pods -n todo-app` — verify all 4 app pods (frontend, backend, notification, recurring-task) are in Running state with 2/2 containers (app + Dapr sidecar) as TC-01 in data-model.md
- [x] T005 [P] [US7] Run `kubectl get pods -n dapr-system` — verify Dapr operator, sidecar-injector, placement, and sentry pods are Running as TC-02 in data-model.md
- [x] T006 [P] [US7] Run `kubectl get kafka -n kafka` — verify Kafka cluster status is Ready as TC-03 in data-model.md
- [x] T007 [P] [US7] Run `kubectl get kafkatopics -n kafka` — verify task-events and reminders topics exist as TC-04 in data-model.md
- [x] T008 [US7] Record infrastructure results in test report table

**Checkpoint**: Infrastructure healthy — browser tests can proceed

---

## Phase 3: User Story 9 — Authentication Flow (Priority: P1) 🎯 MVP

**Goal**: Verify sign-in, session persistence, and dashboard access on the cloud deployment

**Independent Test**: Navigate to app URL, sign in, verify dashboard loads, refresh page to confirm session

### Execution

- [x] T009 [US9] [Playwright] Navigate to `https://todo.tahasiraj.com` — verify sign-in page loads as TC-05
- [x] T010 [US9] [Playwright] Sign in with valid credentials (email + password) — verify redirect to dashboard as TC-06
- [x] T011 [US9] [Playwright] Verify dashboard loads with task list visible as TC-07
- [x] T012 [US9] [Playwright] Refresh page — verify session persists (no re-login) as TC-08
- [x] T013 [US9] Take snapshot of authenticated dashboard state

**Checkpoint**: Auth working — all subsequent Playwright tests have a valid session

---

## Phase 4: User Story 1 — Core Task CRUD (Priority: P1)

**Goal**: Verify create, view, edit, complete, and delete operations on live deployment

**Independent Test**: Create a task, edit it, mark complete, delete it — all via dashboard

### Execution

- [x] T014 [US1] [Playwright] Create a task with title "Test: CRUD Verification" and description "Testing basic operations" — verify it appears in list as TC-09/TC-10
- [x] T015 [US1] [Playwright] Click edit on the test task — change title to "Test: CRUD Updated" — verify updated title displays as TC-11
- [x] T016 [US1] [Playwright] Click checkbox on the test task — verify visual completion indicator as TC-12
- [x] T017 [US1] [Playwright] Click delete on the test task — confirm deletion dialog — verify task removed from list as TC-13
- [x] T018 [US1] Take snapshot after CRUD operations

**Checkpoint**: Basic CRUD verified — intermediate feature tests can proceed

---

## Phase 5: User Story 2 — Priority, Tags, Search, Filter & Sort (Priority: P1)

**Goal**: Verify intermediate-level features: priority assignment, tags, search, filter, sort

**Independent Test**: Create tasks with priorities/tags, exercise search/filter/sort controls

### Execution

- [x] T019 [US2] [Playwright] Expand advanced options — create task "Test: High Priority Item" with HIGH priority — verify red HIGH indicator as TC-14
- [x] T020 [US2] [Playwright] Add tags "testing" and "phase5" to the task — verify tag labels display as TC-15
- [x] T021 [US2] [Playwright] Type "High Priority" in search box — verify only matching task shows as TC-16
- [x] T022 [US2] [Playwright] Clear search — select HIGH priority filter — verify only high-priority tasks display as TC-17
- [x] T023 [US2] [Playwright] Clear priority filter — click on tag "testing" filter — verify filtered results as TC-18
- [x] T024 [US2] [Playwright] Click "Clear Filters" — verify all tasks displayed again as TC-19
- [x] T025 [US2] [Playwright] Select sort by priority — verify tasks ordered high → medium → low as TC-20
- [x] T026 [US2] Take snapshot of filtered/sorted view

**Checkpoint**: Intermediate features verified — advanced feature tests can proceed

---

## Phase 6: User Story 3 & 4 — Due Dates, Overdue, Recurring Tasks (Priority: P1)

**Goal**: Verify due date assignment, overdue display, and recurring task creation with validation

**Independent Test**: Create task with past due date (verify overdue), create recurring task with frequency

### Execution

- [x] T027 [US3] [Playwright] Create task "Test: Future Due" with a due date 1 week from now — verify due date displays as TC-21
- [x] T028 [US3] [Playwright] Create task "Test: Overdue Item" with a due date in the past — verify overdue visual indicator (red text, OVERDUE label) as TC-22
- [x] T029 [US4] [Playwright] Expand advanced options — check "repeating task" — select "daily" frequency with interval 1 — create task "Test: Daily Recurring" — verify it saves correctly as TC-23
- [x] T030 [US4] [Playwright] Check "repeating task" but do NOT select frequency — attempt to submit — verify validation error message "Please select a recurrence frequency" as TC-24
- [x] T031 [US3] Take snapshot showing overdue task display

**Checkpoint**: Advanced features verified — chatbot tests can proceed

---

## Phase 7: User Story 5 — AI Chatbot Task Management (Priority: P1)

**Goal**: Verify chatbot creates tasks via natural language and tasks appear on dashboard

**Independent Test**: Navigate to chat, create task via natural language, verify on dashboard

### Execution

- [x] T032 [US5] [Playwright] Navigate to the chat tab/section of the application as TC-25
- [x] T033 [US5] [Playwright] Type "Add a task to review Phase 5 testing results" and submit — wait for chatbot response as TC-26
- [x] T034 [US5] [Playwright] Verify chatbot response confirms task creation (contains confirmation text) as TC-27
- [x] T035 [US5] [Playwright] Navigate back to dashboard — verify "review Phase 5 testing results" task appears in task list as TC-28
- [x] T036 [US5] Take snapshot of chatbot conversation and dashboard

**Checkpoint**: Chatbot verified — event-driven feature tests can proceed

---

## Phase 8: User Story 6 & 8 — Activity Log & WebSocket (Priority: P1/P2)

**Goal**: Verify activity log records operations and WebSocket connection is established

**Independent Test**: Check activity log for entries from previous test operations; verify WS connection

### Execution

- [x] T037 [US6] [Playwright] Navigate to activity log section — verify at least 3 entries appear (from tasks created/edited/deleted in previous phases) as TC-29
- [x] T038 [US6] [Playwright] Verify activity entries show operation type (created/completed/deleted), task title, and timestamp
- [x] T039 [US8] [Playwright] Use browser_evaluate to check WebSocket connection status — verify connection established to backend as TC-30
- [x] T040 [US8] Take snapshot of activity log entries

**Checkpoint**: Event-driven features verified — report generation can proceed

---

## Phase 9: Report & Demo Structure

**Purpose**: Compile test results and create demo video structure

- [x] T041 [Report] Compile pass/fail results for all TC-01 through TC-30 into a markdown summary table per contracts/test-report-schema.yaml
- [x] T042 [Report] [Playwright] Take final dashboard screenshot showing tasks, priorities, tags, and overdue indicators as TC-31
- [x] T043 [Report] Map each test result to hackathon spec requirement (Phase V Part A/B/C) as TC-32
- [x] T044 [Report] Create 90-second demo video structure with timed segments per data-model.md DemoStructure as TC-33
- [x] T045 [Report] Clean up test data — delete all tasks prefixed with "Test:" created during testing

**Checkpoint**: Testing complete — test report and demo structure ready

---

## Phase 10: Polish & Cross-Cutting

**Purpose**: Final documentation and verification

- [x] T046 Update specs/006-phase5-testing-plan/spec.md status from "Draft" to "Complete"
- [x] T047 [P] Verify all screenshots saved in .playwright-mcp/ directory
- [x] T048 Create PHR (Prompt History Record) documenting the test execution session

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──► Phase 2 (Infrastructure) ──► Phase 3 (Auth) ──►
Phase 4 (CRUD) ──► Phase 5 (Intermediate) ──► Phase 6 (Advanced) ──►
Phase 7 (Chatbot) ──► Phase 8 (Event-Driven) ──► Phase 9 (Report) ──►
Phase 10 (Polish)
```

- **Setup (Phase 1)**: No dependencies — verify environment
- **Infrastructure (Phase 2)**: Depends on Setup — BLOCKS all browser tests
- **Auth (Phase 3)**: Depends on Infrastructure — BLOCKS all feature tests (need session)
- **CRUD (Phase 4)**: Depends on Auth (needs authenticated session)
- **Intermediate (Phase 5)**: Depends on CRUD (needs tasks to filter/sort)
- **Advanced (Phase 6)**: Depends on Intermediate (needs existing tasks for context)
- **Chatbot (Phase 7)**: Depends on Auth (independent of CRUD results, but sequential for data)
- **Event-Driven (Phase 8)**: Depends on all previous phases (needs activity entries from operations)
- **Report (Phase 9)**: Depends on all test phases completing
- **Polish (Phase 10)**: Depends on Report

### Within Each Phase

- Tasks within a phase are sequential unless marked [P]
- Infrastructure checks (Phase 2) can all run in parallel [P]
- Browser tests must be sequential (shared browser state/session)
- Report tasks can partially parallelize (table + screenshots)

### User Story Dependencies

| Story | Phase | Depends On | Independent? |
|-------|-------|------------|-------------|
| US7 (Cloud Deploy) | 2 | Setup only | Yes — kubectl only |
| US9 (Auth) | 3 | Infrastructure | Yes — first browser test |
| US1 (CRUD) | 4 | Auth session | Yes after auth |
| US2 (Search/Filter) | 5 | CRUD (needs tasks) | Needs tasks from Phase 4 |
| US3 (Due Dates) | 6 | Auth session | Yes after auth |
| US4 (Recurring) | 6 | Auth session | Yes after auth |
| US5 (Chatbot) | 7 | Auth session | Yes after auth |
| US6 (Activity Log) | 8 | Prior operations | Needs task events |
| US8 (WebSocket) | 8 | Auth session | Yes after auth |

### Parallel Opportunities

```bash
# Phase 2: All kubectl commands can run in parallel
T004, T005, T006, T007 — all independent kubectl queries

# Phase 6: US3 (due dates) and US4 (recurring) are independent
# but share browser state, so run sequentially within phase

# Phase 8: US6 (activity log) and US8 (WebSocket) are independent
# but share browser state, so run sequentially within phase

# Phase 9: Report compilation tasks can partially parallelize
T041 (table) + T042 (screenshot) can run in parallel
```

---

## Implementation Strategy

### MVP First (Phase 1-3 Only)

1. Complete Phase 1: Setup verification
2. Complete Phase 2: Infrastructure verification
3. Complete Phase 3: Auth flow
4. **STOP and VALIDATE**: If auth works, cloud deployment is confirmed functional
5. Report partial results if blocked

### Incremental Delivery

1. Setup + Infrastructure + Auth → Cloud deployment confirmed (MVP!)
2. Add CRUD → Core features verified
3. Add Intermediate → Full Phase 5 Part A: intermediate features verified
4. Add Advanced → Full Phase 5 Part A: advanced features verified
5. Add Chatbot → Phase III features verified on cloud
6. Add Event-Driven → Phase 5 Part A: event architecture verified
7. Compile Report → Hackathon submission ready
8. Each phase adds coverage without breaking previous results

### Estimated Timeline

| Phase | Tasks | Est. Duration | Cumulative |
|-------|-------|---------------|------------|
| Setup | T001-T003 | 2 min | 2 min |
| Infrastructure | T004-T008 | 3 min | 5 min |
| Auth | T009-T013 | 2 min | 7 min |
| CRUD | T014-T018 | 3 min | 10 min |
| Intermediate | T019-T026 | 4 min | 14 min |
| Advanced | T027-T031 | 3 min | 17 min |
| Chatbot | T032-T036 | 3 min | 20 min |
| Event-Driven | T037-T040 | 2 min | 22 min |
| Report | T041-T045 | 5 min | 27 min |
| Polish | T046-T048 | 3 min | 30 min |
| **Total** | **48 tasks** | **~30 min** | |

---

## Notes

- All browser tests use Playwright MCP via Claude Code tool calls (not test scripts)
- Infrastructure checks use kubectl via Bash tool
- Screenshots are taken at phase checkpoints for demo evidence
- Test data is prefixed with "Test:" for easy identification and cleanup
- If recurrence validation test (T030) fails, note that the fix exists in code but may need Docker rebuild
- Task IDs map to Test Case IDs in data-model.md: T004→TC-01, T005→TC-02, etc.
- Avoid creating excessive test tasks — reuse tasks for multiple verifications where possible
