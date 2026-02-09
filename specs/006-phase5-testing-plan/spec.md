# Feature Specification: Phase 5 Testing Plan

**Feature Branch**: `006-phase5-testing-plan`
**Created**: 2026-02-09
**Status**: Complete
**Input**: User description: "Write plan for testing our application against Hackathon II spec phase-5"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Core Task CRUD Verification (Priority: P1)

A tester validates that all five basic task operations (create, view, update, delete, mark complete) work correctly on the live cloud-deployed application at `https://todo.tahasiraj.com`.

**Why this priority**: These are the foundational features from Phase I/II that every subsequent feature depends on. If CRUD is broken, nothing else can be tested.

**Independent Test**: Navigate to the app, sign in, create a task, edit it, mark it complete, and delete it — all via the web dashboard.

**Acceptance Scenarios**:

1. **Given** a signed-in user on the dashboard, **When** they fill in a title and click "add_task", **Then** the task appears in the task list immediately.
2. **Given** a task exists, **When** the user clicks the edit icon, changes the title, and saves, **Then** the updated title is displayed.
3. **Given** a task exists, **When** the user clicks the checkbox, **Then** the task is marked complete with visual indication.
4. **Given** a task exists, **When** the user clicks delete and confirms, **Then** the task is removed from the list.
5. **Given** the task list, **When** the user views it, **Then** all their tasks are displayed with title, priority, tags, status, and timestamps.

---

### User Story 2 — Priority, Tags, Search, Filter & Sort (Priority: P1)

A tester validates intermediate-level features: assigning priorities, adding tags, searching by keyword, filtering by priority/tag/status, and sorting tasks.

**Why this priority**: These are required Phase 5 intermediate features (FR-001 through FR-006 in the spec). They must be verified to confirm spec compliance.

**Independent Test**: Create tasks with varying priorities and tags, then exercise search, filter, and sort controls on the dashboard.

**Acceptance Scenarios**:

1. **Given** a user creating a task, **When** they expand advanced options and select "HIGH" priority, **Then** the task is saved and displayed with a red HIGH priority indicator.
2. **Given** a user creating a task, **When** they add tags "work" and "urgent", **Then** the tags appear as labels on the task.
3. **Given** multiple tasks exist, **When** the user types a keyword in the search box, **Then** only tasks matching that keyword in title or description are shown.
4. **Given** tasks with different priorities, **When** the user selects "HIGH" priority filter, **Then** only high-priority tasks are displayed.
5. **Given** tasks with tags, **When** the user clicks on a tag filter, **Then** only tasks with that tag are shown.
6. **Given** a filtered list, **When** the user clicks "Clear Filters", **Then** all tasks are displayed again.

---

### User Story 3 — Due Dates and Overdue Display (Priority: P1)

A tester validates that tasks can have due dates, overdue tasks are visually marked, and the due date is correctly displayed.

**Why this priority**: Due dates are required for recurring tasks and reminders (FR-007, FR-012). Overdue display is a key visual indicator.

**Independent Test**: Create a task with a past due date and verify it shows as overdue. Create one with a future due date and verify it shows normally.

**Acceptance Scenarios**:

1. **Given** a user creates a task with a due date, **When** the task is saved, **Then** the due date is displayed in the task list.
2. **Given** a task has a due date in the past, **When** the user views the task list, **Then** the task is visually marked as overdue (e.g., red text, "OVERDUE" label).
3. **Given** a task has a due date in the future, **When** the user views the task list, **Then** the task shows the due date without overdue indication.

---

### User Story 4 — Recurring Tasks (Priority: P1)

A tester validates that recurring task creation works via the dashboard form, including selecting recurrence frequency and interval.

**Why this priority**: Recurring tasks are a required advanced feature (FR-010, FR-011). The frontend form was recently fixed to require frequency selection.

**Independent Test**: Create a recurring daily task, verify it saves correctly with recurrence metadata visible.

**Acceptance Scenarios**:

1. **Given** a user checks "repeating task" in advanced options, **When** they select "daily" frequency and interval "1", **Then** the task is created with `is_recurring=true` and `recurrence_frequency=daily`.
2. **Given** a user checks "repeating task" but does NOT select a frequency, **When** they submit, **Then** a validation error is displayed: "Please select a recurrence frequency".
3. **Given** a recurring task exists, **When** the user marks it complete, **Then** a new occurrence is automatically created (via event-driven processing) with the next due date.

---

### User Story 5 — AI Chatbot Task Management (Priority: P1)

A tester validates that the AI chatbot can create, list, update, complete, and delete tasks via natural language commands.

**Why this priority**: The chatbot is a core Phase III feature that must work on the cloud deployment. It validates MCP tools, OpenAI Agents SDK, and the full AI pipeline.

**Independent Test**: Navigate to the chat tab, issue natural language commands, and verify tasks appear on the dashboard.

**Acceptance Scenarios**:

1. **Given** the user is in the chat tab, **When** they type "Add a task to buy groceries", **Then** the chatbot creates the task and confirms it.
2. **Given** tasks exist, **When** the user asks "Show my tasks", **Then** the chatbot lists the tasks.
3. **Given** a task exists, **When** the user says "Mark task X as complete", **Then** the chatbot completes it and confirms.
4. **Given** the chatbot, **When** the user types "Delete the groceries task", **Then** the chatbot deletes it and confirms.
5. **Given** the chat, **When** the user navigates back to the dashboard, **Then** chatbot-created tasks are visible in the task list.

---

### User Story 6 — Activity Log Verification (Priority: P1)

A tester validates that all task operations are recorded in the activity log and viewable by the user.

**Why this priority**: Activity log validates the event-driven architecture end-to-end (FR-013, FR-014). This is a key Phase 5 differentiator.

**Independent Test**: Perform several task operations, then check the activity log to verify all are recorded.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** they check the activity log, **Then** a "created" entry appears with the task title and timestamp.
2. **Given** a user completes a task, **When** they check the activity log, **Then** a "completed" entry appears.
3. **Given** multiple operations performed, **When** viewing the activity log, **Then** entries appear in reverse chronological order.

---

### User Story 7 — Cloud Deployment Verification (Priority: P1)

A tester validates that the application is fully operational on Oracle Cloud OKE, accessible via `https://todo.tahasiraj.com`, with all Kubernetes pods running.

**Why this priority**: Cloud deployment is the primary deliverable of Phase 5 (FR-021, FR-022, FR-024).

**Independent Test**: Access the live URL, sign in, and verify all features work. Also check pod status via kubectl.

**Acceptance Scenarios**:

1. **Given** the OKE cluster, **When** checking pod status, **Then** all application pods (frontend, backend, notification, recurring-task) are in Running state with Dapr sidecars.
2. **Given** the external URL, **When** accessing it in a browser, **Then** the frontend loads and the user can sign in.
3. **Given** a signed-in user, **When** they perform task operations, **Then** the backend API responds correctly (no 401, 403, or 500 errors).
4. **Given** the deployment, **When** checking Dapr and Kafka, **Then** Dapr system pods are running and Kafka cluster is Ready.

---

### User Story 8 — WebSocket Real-Time Sync (Priority: P2)

A tester validates that task changes in one browser tab are reflected in another open tab without manual refresh.

**Why this priority**: Real-time sync demonstrates the full pub/sub pipeline (FR-015) but is a polish feature.

**Independent Test**: Open two browser tabs, make a change in one, verify it appears in the other.

**Acceptance Scenarios**:

1. **Given** two browser tabs open to the dashboard, **When** a task is created in tab A, **Then** the task appears in tab B within a few seconds.
2. **Given** a task is marked complete in one tab, **When** viewing the other tab, **Then** the completion is reflected.

---

### User Story 9 — Authentication Flow (Priority: P1)

A tester validates the full authentication flow: sign up, sign in, session persistence, and sign out on the cloud deployment.

**Why this priority**: Without working auth, no features can be tested. JWT token validation through Cloudflare Tunnel is a critical path.

**Independent Test**: Navigate to the app, sign in with credentials, verify session persists across page refreshes, and sign out.

**Acceptance Scenarios**:

1. **Given** the app URL, **When** accessing it without a session, **Then** the user is directed to the sign-in page.
2. **Given** valid credentials, **When** signing in, **Then** the user is redirected to the dashboard and their tasks load.
3. **Given** a signed-in session, **When** refreshing the page, **Then** the session persists (no re-login required).
4. **Given** a signed-in user, **When** they sign out, **Then** the session ends and they see the sign-in page.
5. **Given** invalid credentials, **When** attempting to sign in, **Then** an appropriate error message is displayed.

---

### Edge Cases

- What happens when the user creates a task with a title of exactly 200 characters? It should succeed (boundary value).
- What happens when the user tries to add an 11th tag? The form should prevent it (max 10 tags).
- What happens when Cloudflare Tunnel is temporarily down? The app becomes inaccessible, but pods remain running.
- What happens when the user creates a recurring task without a due date? The recurrence rule is saved, but no reminder is scheduled.
- What happens when the user accesses the API directly without a JWT token? They receive a 401 Unauthorized.
- What happens when the user's session expires mid-use? They should be redirected to sign-in.

---

## Requirements *(mandatory)*

### Functional Requirements

**Test Infrastructure:**

- **FR-001**: Testing MUST use Playwright MCP for automated browser-based testing against the live deployment at `https://todo.tahasiraj.com`.
- **FR-002**: Tests MUST cover all Phase 5 hackathon requirements: basic CRUD, intermediate features (priorities, tags, search, filter, sort), and advanced features (due dates, recurring tasks, activity log, real-time sync).
- **FR-003**: Tests MUST verify the cloud deployment (OKE pods, Dapr sidecars, Kafka cluster) via kubectl commands.
- **FR-004**: Tests MUST produce a clear pass/fail summary table mapping each test to the hackathon spec requirement.

**Feature Coverage:**

- **FR-005**: Tests MUST verify all 5 basic task operations (create, read, update, delete, complete) on the live deployment.
- **FR-006**: Tests MUST verify priority assignment (high/medium/low) and visual indicators.
- **FR-007**: Tests MUST verify tag creation, display, and filtering.
- **FR-008**: Tests MUST verify search by keyword in task title/description.
- **FR-009**: Tests MUST verify filter by priority and by tag.
- **FR-010**: Tests MUST verify sort by priority and due date.
- **FR-011**: Tests MUST verify due date assignment and overdue visual marking.
- **FR-012**: Tests MUST verify recurring task creation with frequency validation.
- **FR-013**: Tests MUST verify AI chatbot task creation via natural language.
- **FR-014**: Tests MUST verify activity log records task operations.
- **FR-015**: Tests MUST verify WebSocket connection for real-time sync.
- **FR-016**: Tests MUST verify authentication flow (sign in, session persistence, sign out).

**Demo Preparation:**

- **FR-017**: Testing MUST capture screenshots at key milestones for demo video evidence.
- **FR-018**: A demo video structure MUST be produced that fits within the 90-second hackathon limit.

### Key Entities

- **Test Case**: A single verifiable check with an ID, description, steps, expected result, and pass/fail status. Maps to a hackathon spec requirement.
- **Test Suite**: A collection of test cases grouped by feature area (CRUD, search/filter, chatbot, activity log, etc.).
- **Test Report**: A summary table showing all test cases, their status, and any notes/screenshots.
- **Demo Video Structure**: A timed script for the 90-second demo video, covering which features to show and in what order.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All basic CRUD tests (create, view, edit, delete, complete) pass on the live cloud deployment.
- **SC-002**: All intermediate feature tests (priority, tags, search, filter, sort) pass on the live deployment.
- **SC-003**: Recurring task creation with frequency validation passes (including the recently fixed frontend validation).
- **SC-004**: AI chatbot successfully creates a task via natural language and the task appears on the dashboard.
- **SC-005**: Activity log displays at least 3 recorded operations after performing task actions.
- **SC-006**: WebSocket connection is established and real-time sync is functional.
- **SC-007**: Authentication flow (sign in, session persistence, sign out) works without errors through Cloudflare Tunnel.
- **SC-008**: All Kubernetes pods (frontend, backend, notification, recurring-task) plus Dapr sidecars are in Running state.
- **SC-009**: Kafka cluster and topics are operational on the OKE cluster.
- **SC-010**: A test report with pass/fail results covers at least 20 distinct test cases.
- **SC-011**: A 90-second demo video structure covers all required Phase 5 features.

---

## Assumptions

- The application is already deployed and accessible at `https://todo.tahasiraj.com` via Cloudflare Tunnel routing to OKE.
- Cloudflare Tunnel routes are configured: `/api/auth` -> frontend, `/api` -> backend, `*` -> frontend.
- The tester has valid credentials to sign in (email/password via Better Auth).
- Playwright MCP is available in the local WSL environment for browser automation.
- WSL `/etc/hosts` has `104.21.23.140 todo.tahasiraj.com` entry for DNS resolution.
- The recurrence frequency validation fix in `task-form.tsx` may or may not be deployed (the fix exists in code but may need a Docker image rebuild).
- kubectl is configured with OKE cluster credentials for infrastructure verification.

---

## Scope

### In Scope

- Automated browser testing of all Phase 5 features via Playwright
- kubectl-based infrastructure verification (pods, Dapr, Kafka)
- Test report generation with pass/fail summary
- Demo video structure creation for 90-second hackathon presentation
- Screenshot capture for demo evidence

### Out of Scope

- Load testing or performance benchmarking
- Security penetration testing
- CI/CD pipeline testing (pipeline itself is not set up yet)
- Notification service end-to-end testing (requires waiting for reminder timing)
- Multi-user concurrent testing
- Mobile or responsive layout testing

---

## Dependencies

- **Live deployment**: `https://todo.tahasiraj.com` must be accessible
- **OKE cluster**: kubectl access for infrastructure checks
- **Playwright MCP**: Browser automation tool installed locally
- **Phase 5 spec**: `specs/005-cloud-event-deployment/spec.md` defines the features to test against
- **Hackathon spec**: `Hackathon II - Todo Spec-Driven Development.md` defines grading criteria

---

## Risks

- **Frontend image not rebuilt**: The recurrence frequency validation fix may not be deployed, causing one test to fail. Mitigation: rebuild and push the frontend image before testing, or test with the workaround (manually select frequency).
- **Cloudflare Tunnel instability**: Tunnel may drop connections during testing. Mitigation: retry failed tests and monitor tunnel status.
- **WSL DNS resolution**: May fail for `todo.tahasiraj.com`. Mitigation: `/etc/hosts` entry already added.

---

## Test Execution Plan

### Phase 1: Infrastructure Verification (kubectl)
1. Verify all app pods running (`kubectl get pods -n todo-app`)
2. Verify Dapr system pods (`kubectl get pods -n dapr-system`)
3. Verify Kafka cluster ready (`kubectl get kafka -n kafka`)
4. Verify Kafka topics exist (`kubectl get kafkatopics -n kafka`)

### Phase 2: Authentication Flow (Playwright)
5. Navigate to `https://todo.tahasiraj.com`
6. Sign in with valid credentials
7. Verify dashboard loads with task list
8. Verify session persists after page refresh

### Phase 3: Core CRUD (Playwright)
9. Create a task with title and description
10. Verify task appears in list
11. Edit the task (change title)
12. Mark task as complete
13. Delete task with confirmation dialog

### Phase 4: Intermediate Features (Playwright)
14. Create task with HIGH priority — verify visual indicator
15. Create task with tags — verify tag display
16. Search tasks by keyword
17. Filter by HIGH priority
18. Filter by tag
19. Clear filters — verify all tasks shown
20. Sort by priority

### Phase 5: Advanced Features (Playwright)
21. Create task with due date
22. Create task with past due date — verify overdue display
23. Create recurring task with frequency — verify validation
24. Attempt recurring task without frequency — verify error

### Phase 6: AI Chatbot (Playwright)
25. Navigate to chat tab
26. Create task via natural language ("Add a task to...")
27. Verify chatbot response confirms creation
28. Navigate back to dashboard — verify chatbot task appears

### Phase 7: Event-Driven Features (Playwright)
29. Check activity log — verify entries for recent operations
30. Open second tab — verify WebSocket connection

### Phase 8: Screenshot & Report
31. Take final dashboard screenshot
32. Compile pass/fail test report table
33. Create demo video structure (90 seconds)
