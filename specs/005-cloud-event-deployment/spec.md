# Feature Specification: Phase V — Advanced Cloud Deployment

**Feature Branch**: `005-cloud-event-deployment`
**Created**: 2026-01-31
**Status**: Draft
**Input**: User description: "Write specification for phase-5 advanced cloud deployment with Kafka, Dapr, CI/CD, and cloud Kubernetes"

---

## Clarifications

### Session 2026-01-31

- Q: Which cloud provider for production deployment? → A: Oracle OKE (always-free tier, 4 OCPUs, 24GB RAM, no credit expiry)
- Q: What event delivery guarantee for the message broker? → A: At-least-once delivery; all event consumers must be idempotent
- Q: How are recurrence rules stored? → A: Simple structured fields — frequency (daily/weekly/monthly), interval (number), day_of_week (optional), day_of_month (optional)
- Q: How long are activity log entries retained? → A: 90 days rolling retention; entries older than 90 days are automatically purged
- Q: What happens when browser notification permission is denied? → A: Show in-app reminder banner in the task list UI for pending/missed reminders

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Task Priorities and Tags (Priority: P1)

A user wants to organize their tasks by importance and category. They assign a priority level (high, medium, low) to each task and attach one or more tags (e.g., "work", "home", "urgent") so they can focus on what matters most.

**Why this priority**: Priorities and tags are the foundation that all other intermediate and advanced features build on. Filtering, sorting, search, and event-driven features all depend on tasks having structured metadata. This is the smallest change that delivers immediate organizational value.

**Independent Test**: Can be fully tested by creating tasks with various priority levels and tags via the chatbot, then verifying those properties persist and display correctly in the task list.

**Acceptance Scenarios**:

1. **Given** a user is creating a task via the chatbot, **When** they specify a priority (e.g., "Add a high-priority task: finish report"), **Then** the task is saved with that priority level and displays a visual priority indicator.
2. **Given** a user is creating a task, **When** they include tags (e.g., "Tag it as work and urgent"), **Then** the task is saved with those tags and they appear as labels on the task.
3. **Given** a task exists, **When** the user asks the chatbot to change its priority or tags, **Then** the task is updated accordingly.
4. **Given** a task has no explicit priority, **When** it is created, **Then** it defaults to "medium" priority.

---

### User Story 2 — Search, Filter, and Sort (Priority: P1)

A user with many tasks wants to quickly find specific tasks. They can search by keyword, filter by status/priority/tag, and sort by due date, priority, or alphabetical order.

**Why this priority**: Finding tasks efficiently is critical for usability once the task list grows beyond a handful of items. This directly enhances the chatbot experience — users ask natural language questions like "show my high-priority work tasks."

**Independent Test**: Can be tested by creating multiple tasks with varying properties, then requesting filtered/sorted views through the chatbot.

**Acceptance Scenarios**:

1. **Given** a user has 20+ tasks, **When** they ask "show my high-priority tasks", **Then** only tasks with high priority are displayed.
2. **Given** tasks with various tags, **When** the user asks "show tasks tagged work", **Then** only tasks with the "work" tag are displayed.
3. **Given** tasks exist, **When** the user asks "search for report", **Then** tasks whose title or description contain "report" are returned.
4. **Given** a filtered or full task list, **When** the user asks "sort by priority", **Then** tasks are ordered high → medium → low.
5. **Given** tasks with due dates, **When** the user asks "sort by due date", **Then** tasks are ordered by nearest due date first.
6. **Given** the user applies a filter, **When** no tasks match, **Then** the system informs the user clearly (e.g., "No tasks match that filter").

---

### User Story 3 — Due Dates and Reminders (Priority: P2)

A user sets a deadline on a task. As the deadline approaches, they receive a notification reminding them. The reminder is sent automatically by the system without the user needing to check manually.

**Why this priority**: Due dates are a prerequisite for recurring tasks and for the reminder/notification event pipeline. This story introduces time-based task management and the first event-driven use case (reminder events published to a message topic).

**Independent Test**: Can be tested by creating a task with a near-future due date and verifying that the system triggers a reminder notification at the configured lead time.

**Acceptance Scenarios**:

1. **Given** a user creates a task via the chatbot, **When** they specify a due date (e.g., "due tomorrow at 3pm"), **Then** the task is saved with that due date and it displays in the task list.
2. **Given** a task has a due date, **When** the due date is within the reminder window (default: 30 minutes before), **Then** the system publishes a reminder event.
3. **Given** a reminder event is published, **When** the notification service processes it, **Then** the user receives a browser notification with the task title and due time.
4. **Given** a task's due date has passed, **When** the user views their task list, **Then** the task is visually marked as overdue.
5. **Given** a user updates or removes a due date, **When** the change is saved, **Then** any existing scheduled reminder for that task is cancelled or updated.
6. **Given** a user has denied browser notification permission, **When** a reminder is triggered, **Then** the system displays an in-app reminder banner in the task list UI showing the task title and due time.

---

### User Story 4 — Recurring Tasks (Priority: P2)

A user has tasks that repeat on a schedule (daily, weekly, monthly, or custom). When they complete a recurring task, the system automatically creates the next occurrence without user intervention.

**Why this priority**: Recurring tasks require event-driven processing — completing a task publishes an event, and a separate service consumes it to create the next occurrence. This is a natural fit for the Kafka/Dapr architecture and demonstrates decoupled microservice communication.

**Independent Test**: Can be tested by creating a recurring task, marking it complete, and verifying that the next occurrence is automatically created with the correct next due date.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** they specify a recurrence pattern (e.g., "every Monday", "daily", "monthly on the 15th"), **Then** the task is saved with that recurrence rule.
2. **Given** a recurring task exists, **When** the user marks it complete, **Then** the system publishes a task-completed event and a new task is automatically created with the next due date according to the recurrence pattern.
3. **Given** a recurring task is completed, **When** the next occurrence is created, **Then** it inherits the same title, priority, tags, and recurrence rule as the original.
4. **Given** a recurring task, **When** the user edits the recurrence pattern, **Then** future occurrences follow the updated pattern.
5. **Given** a recurring task, **When** the user deletes it (not just completes), **Then** no further occurrences are created.

---

### User Story 5 — Event-Driven Activity Log (Priority: P2)

All task operations (create, update, delete, complete) are recorded in an activity log. The user can view their recent activity to understand what changed and when.

**Why this priority**: The activity log is a direct consumer of the task-events topic, validating that the event-driven architecture is working end-to-end. It also provides auditability, which is valuable for both users and system operators.

**Independent Test**: Can be tested by performing several task operations, then requesting the activity log and verifying all operations appear with correct timestamps and details.

**Acceptance Scenarios**:

1. **Given** a user creates, updates, completes, or deletes a task, **When** the operation succeeds, **Then** an event is published to the task-events topic with the operation type, task data, user ID, and timestamp.
2. **Given** events are published, **When** the audit service consumes them, **Then** each event is persisted in an activity log.
3. **Given** a user asks "show my recent activity", **Then** the system returns the last 20 activity entries in reverse chronological order.
4. **Given** the activity log, **When** displayed, **Then** each entry shows the operation type, task title, and when it happened (e.g., "Completed 'Buy groceries' — 5 minutes ago").

---

### User Story 6 — Real-Time Sync Across Clients (Priority: P3)

When a user has the app open in multiple browser tabs or devices, changes made in one tab are immediately reflected in all other open tabs without manual refresh.

**Why this priority**: Real-time sync is a polish feature that demonstrates the full pub/sub pipeline — a task change publishes to a topic, a WebSocket service consumes it, and all connected clients receive the update. Important for demonstrating the architecture but not required for core functionality.

**Independent Test**: Can be tested by opening two browser tabs, making a task change in one, and verifying the change appears in the other within a few seconds.

**Acceptance Scenarios**:

1. **Given** a user has the app open in two browser tabs, **When** they create a task in tab A, **Then** the task appears in tab B within 3 seconds without manual refresh.
2. **Given** a user completes a task in one tab, **When** the update is published, **Then** all connected tabs reflect the completion status.
3. **Given** a user's browser loses the WebSocket connection, **When** the connection is re-established, **Then** the client fetches the latest state to avoid stale data.

---

### User Story 7 — Dapr Sidecar Integration (Priority: P1)

All service-to-service communication, event publishing, state management, and secret access happen through the Dapr sidecar rather than direct library dependencies. The application code communicates with Dapr via HTTP APIs, and infrastructure details (Kafka broker addresses, database connection strings, secret stores) are configured in Dapr component YAML files.

**Why this priority**: Dapr is the foundational runtime that all event-driven features depend on. Without Dapr, every service would need direct Kafka client libraries, manual service discovery, and hardcoded connection strings. This must be established before any event-driven feature can work.

**Independent Test**: Can be tested by deploying the backend with its Dapr sidecar, publishing a test event via the Dapr pub/sub API, and verifying the event is received by a subscriber — without any Kafka client library in the application code.

**Acceptance Scenarios**:

1. **Given** the backend service is deployed, **When** it starts, **Then** a Dapr sidecar runs alongside it and is accessible at `localhost:3500`.
2. **Given** Dapr components are configured (pub/sub, state, secrets), **When** the backend publishes an event via `POST /v1.0/publish/{pubsub}/{topic}`, **Then** the event reaches the configured message broker.
3. **Given** a service subscribes to a topic, **When** an event is published to that topic, **Then** Dapr delivers the event to the subscriber's configured endpoint.
4. **Given** Dapr secrets component is configured, **When** the backend requests a secret via the Dapr API, **Then** the correct secret value is returned without the app knowing the underlying secret store implementation.
5. **Given** the frontend needs to call the backend, **When** it uses Dapr service invocation, **Then** the call succeeds with automatic retries and service discovery, without hardcoded backend URLs.

---

### User Story 8 — Cloud Kubernetes Deployment (Priority: P1)

The entire application (frontend, backend, Dapr sidecars, message broker) is deployed to a managed Kubernetes cluster on Oracle Cloud OKE (always-free tier). The deployment uses the same Helm charts from Phase IV, adapted for the cloud environment.

**Why this priority**: Cloud deployment is the culmination of the entire project evolution — from console app to production cloud infrastructure. Without this, the application remains local-only, defeating the purpose of Phase V.

**Independent Test**: Can be tested by deploying the Helm chart to a cloud cluster and accessing the application via its external URL, verifying frontend loads, backend responds, and authentication works.

**Acceptance Scenarios**:

1. **Given** a managed Kubernetes cluster is provisioned on a cloud provider, **When** the Helm chart is deployed, **Then** all pods (frontend, backend, message broker, Dapr) reach Running status.
2. **Given** the deployment succeeds, **When** a user accesses the external URL, **Then** the frontend loads and they can sign in and manage tasks.
3. **Given** the cloud deployment, **When** a pod crashes, **Then** Kubernetes automatically restarts it and the application recovers without manual intervention.
4. **Given** the deployment uses environment-specific values, **When** deploying to cloud vs. Minikube, **Then** only the values file differs — the templates remain the same.

---

### User Story 9 — CI/CD Pipeline (Priority: P2)

When code is pushed to the repository, a CI/CD pipeline automatically builds Docker images, runs tests, and deploys to the cloud Kubernetes cluster. Developers do not manually build or deploy.

**Why this priority**: CI/CD automates the build-test-deploy cycle, eliminating manual errors and enabling rapid iteration. It's essential for any production system but depends on the cloud deployment (Story 8) being functional first.

**Independent Test**: Can be tested by pushing a commit and verifying that the pipeline triggers, builds images, runs tests, and updates the cloud deployment.

**Acceptance Scenarios**:

1. **Given** a developer pushes to the main branch, **When** the push is received by GitHub, **Then** a GitHub Actions workflow triggers automatically.
2. **Given** the workflow triggers, **When** it executes, **Then** it builds Docker images for frontend and backend, runs tests, and pushes images to a container registry.
3. **Given** images are pushed to the registry, **When** the deploy step runs, **Then** the Helm chart is upgraded on the cloud cluster with the new image tags.
4. **Given** a test fails in the pipeline, **When** the failure is detected, **Then** the deployment step is skipped and the developer is notified.
5. **Given** the pipeline completes successfully, **When** a user accesses the application, **Then** they see the updated version.

---

### User Story 10 — Monitoring and Observability (Priority: P3)

The deployed system has logging, metrics, and health monitoring configured. Operators can observe system health, debug issues, and receive alerts when something goes wrong.

**Why this priority**: Monitoring is critical for production operations but is a supporting concern — the app functions without it. It's the last piece that turns a deployed app into a production-ready system.

**Independent Test**: Can be tested by accessing the monitoring dashboard, verifying logs are flowing, metrics are collected, and health checks report correctly.

**Acceptance Scenarios**:

1. **Given** the application is deployed, **When** an operator accesses the logging system, **Then** structured logs from all services are visible and searchable.
2. **Given** a task operation occurs, **When** the log is written, **Then** it includes the operation type, user ID, timestamp, and request duration in structured JSON format.
3. **Given** health check endpoints exist, **When** Kubernetes probes them, **Then** pod health status is accurately reflected in the cluster dashboard.
4. **Given** a pod becomes unhealthy, **When** the liveness probe fails, **Then** Kubernetes restarts the pod and an event is logged.

---

### Edge Cases

- What happens when Kafka/message broker is temporarily unavailable? Events must be retried or buffered; task operations should not fail for the user.
- What happens when a recurring task is completed but the event consumer is down? The event must be persisted in the topic and processed when the consumer recovers (at-least-once delivery). The consumer must be idempotent — if the same completion event is delivered twice, only one new occurrence is created.
- What happens when a user sets a due date in the past? The system should mark it as overdue immediately rather than scheduling a reminder.
- What happens when two clients simultaneously update the same task? The last write wins, and both clients receive the final state via real-time sync.
- What happens when the Dapr sidecar is not available? The application should fail with a clear error rather than silently dropping events.
- What happens when the CI/CD pipeline is deploying and a user is mid-session? Rolling updates must ensure zero downtime — old pods serve until new pods are ready.
- What happens when the Oracle Cloud always-free tier resource limits are reached? The deployment must fit within 4 OCPUs and 24GB RAM; resource requests must be tuned accordingly.

---

## Requirements *(mandatory)*

### Functional Requirements

**Intermediate Features:**

- **FR-001**: System MUST allow users to assign a priority level (high, medium, low) to any task, defaulting to medium if unspecified.
- **FR-002**: System MUST allow users to attach one or more tags to any task, with tags being free-form text labels.
- **FR-003**: System MUST support searching tasks by keyword match against task title and description.
- **FR-004**: System MUST support filtering tasks by status (complete/incomplete), priority level, and tag.
- **FR-005**: System MUST support sorting tasks by due date, priority level, or alphabetical order.
- **FR-006**: System MUST allow combining filters (e.g., high-priority + work tag + incomplete).

**Advanced Features:**

- **FR-007**: System MUST allow users to set a due date and time on any task.
- **FR-008**: System MUST automatically publish a reminder event when a task's due date is within the configurable reminder window (default: 30 minutes).
- **FR-009**: System MUST deliver browser notifications to the user when a reminder event is processed by the notification service. If browser notification permission is denied, the system MUST display an in-app reminder banner in the task list UI showing pending and missed reminders.
- **FR-010**: System MUST support defining recurrence patterns on tasks using structured fields: frequency (daily/weekly/monthly), interval (default 1), optional day_of_week, optional day_of_month, and optional end_date. The chatbot interprets natural language and maps to these fields.
- **FR-011**: System MUST automatically create the next occurrence of a recurring task when the current one is marked complete, via event-driven processing.
- **FR-012**: System MUST visually mark tasks as overdue when their due date has passed.

**Event-Driven Architecture:**

- **FR-013**: System MUST publish all task operations (create, update, delete, complete) as events to a task-events topic.
- **FR-014**: System MUST maintain an activity log by consuming task-events and persisting each event with operation type, task data, user ID, and timestamp. Entries older than 90 days MUST be automatically purged.
- **FR-015**: System MUST support real-time synchronization of task changes across multiple connected clients via WebSocket, driven by events from a task-updates topic.
- **FR-016**: System MUST use Dapr pub/sub as the abstraction layer for event publishing and subscription — no direct message broker client libraries in application code.
- **FR-016a**: System MUST guarantee at-least-once delivery for all events. All event consumers MUST be idempotent — processing the same event multiple times produces the same result as processing it once.

**Dapr Integration:**

- **FR-017**: System MUST use Dapr service invocation for inter-service communication with automatic retry and service discovery.
- **FR-018**: System MUST use Dapr secrets management to access API keys, database credentials, and other sensitive configuration.
- **FR-019**: System MUST use Dapr scheduled jobs (Jobs API) for time-based reminder triggers rather than polling-based cron.
- **FR-020**: All Dapr component configurations (pub/sub, state, secrets, bindings) MUST be defined in YAML files, separate from application code.

**Cloud Deployment:**

- **FR-021**: System MUST be deployable to a managed Kubernetes cluster on Oracle Cloud OKE using Helm charts.
- **FR-022**: System MUST use environment-specific Helm values files to differentiate local (Minikube) from cloud deployments.
- **FR-023**: System MUST deploy Kafka (via Strimzi operator or Redpanda) within the Kubernetes cluster, or connect to a managed Kafka service (Redpanda Cloud, Confluent Cloud).
- **FR-024**: System MUST expose the application externally via an Ingress controller or cloud load balancer with a valid URL.

**CI/CD:**

- **FR-025**: System MUST have a GitHub Actions workflow that triggers on push to the main branch.
- **FR-026**: The CI/CD pipeline MUST build Docker images, run tests, push images to a container registry, and deploy to the cloud cluster.
- **FR-027**: The CI/CD pipeline MUST halt deployment if any test fails.

**Monitoring:**

- **FR-028**: System MUST produce structured JSON logs for all services.
- **FR-029**: System MUST expose health check endpoints that Kubernetes probes can use for liveness and readiness.
- **FR-030**: System MUST log all Kafka event publishing and consumption with topic, event type, and timestamp.

### Key Entities

- **Task**: Extended with `priority` (enum: high/medium/low), `tags` (list of strings), `due_date` (datetime, nullable), `recurrence_rule` (string pattern, nullable), `is_overdue` (derived from due_date).
- **Task Event**: Represents a state change — contains event_type (created/updated/completed/deleted), task_data (full task snapshot), user_id, and timestamp. Published to Kafka topics.
- **Reminder Event**: Contains task_id, task title, due_at, remind_at, and user_id. Published when a task's due date enters the reminder window.
- **Activity Log Entry**: A persisted task event consumed from the task-events topic. Stores operation type, task title, user_id, and timestamp for user-facing activity history. Retained for 90 days; older entries are automatically purged.
- **Recurrence Rule**: Defines the repeat pattern for a task using simple structured fields: `frequency` (enum: daily/weekly/monthly), `interval` (integer, default 1 — e.g., interval=2 + frequency=weekly means every 2 weeks), `day_of_week` (optional, 0-6 for weekly patterns), `day_of_month` (optional, 1-31 for monthly patterns), and `end_date` (optional datetime). The chatbot interprets natural language ("every Monday") and maps it to these fields.
- **Dapr Component**: Configuration entity defining infrastructure bindings — pub/sub (Kafka), state store (PostgreSQL), secrets (Kubernetes secrets), and scheduler (Jobs API).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can assign priorities and tags to tasks and retrieve filtered results in under 2 seconds via the chatbot.
- **SC-002**: Users can search across all their tasks by keyword and receive results in under 1 second.
- **SC-003**: When a task's due date enters the reminder window, a notification is delivered to the user within 60 seconds.
- **SC-004**: When a recurring task is completed, the next occurrence is created within 5 seconds without user intervention.
- **SC-005**: All task operations (create, update, delete, complete) appear in the activity log within 10 seconds of occurring.
- **SC-006**: Task changes made in one browser tab appear in another open tab within 3 seconds.
- **SC-007**: The application is fully operational on a cloud Kubernetes cluster, accessible via an external URL, with all services in Running state.
- **SC-008**: A code push to the main branch results in an automated build, test, and deploy cycle that completes and updates the cloud deployment.
- **SC-009**: Application code contains no direct infrastructure client libraries — all event publishing, state access, and secret retrieval use the distributed runtime abstraction layer (Dapr), making infrastructure swappable via configuration.
- **SC-010**: System handles message broker unavailability gracefully — user-facing task operations succeed, and events are delivered when the broker recovers.
- **SC-011**: The system supports at least 100 concurrent users on the cloud deployment without degradation.
- **SC-012**: Zero-downtime deployments — users experience no interruption when a new version is deployed via the CI/CD pipeline.

---

## Assumptions

- The existing Phase IV Helm charts, Docker images, and Kubernetes configurations provide the foundation. This phase extends them rather than replacing them.
- Oracle Cloud OKE always-free tier (4 OCPUs, 24GB RAM) provides sufficient resources for the deployment. No credit expiry eliminates time pressure.
- Neon PostgreSQL remains the primary database. Dapr state management is used for auxiliary state (e.g., conversation cache), not as a replacement for the main database.
- The chatbot (OpenAI Agents SDK + MCP tools) from Phase III remains the primary user interface. New features (priorities, tags, search, filter, sort, recurring, due dates) are exposed as new or enhanced MCP tools.
- Browser notifications require user permission grant. If permission is denied, the system falls back to displaying an in-app reminder banner in the task list UI, ensuring users still see pending and missed reminders.
- Kafka topic retention is configured for at least 7 days to handle consumer downtime without data loss.
- The CI/CD pipeline pushes to a public or authenticated container registry (Docker Hub, GitHub Container Registry, or cloud-specific registry).

---

## Scope

### In Scope

- Intermediate features: priorities, tags, search, filter, sort
- Advanced features: due dates, reminders, recurring tasks
- Event-driven architecture with Kafka topics (task-events, reminders, task-updates)
- Dapr integration: pub/sub, state management, service invocation, secrets, Jobs API
- Cloud Kubernetes deployment on Oracle Cloud OKE
- CI/CD pipeline with GitHub Actions
- Monitoring: structured logging, health checks
- Activity log service
- Real-time client sync via WebSocket
- Notification service for reminders

### Out of Scope

- Email or SMS notifications (browser notifications only)
- Multi-tenant architecture (each user has their own data, but there is no organizational hierarchy)
- Custom recurrence patterns beyond daily/weekly/monthly (e.g., "every third Tuesday")
- Horizontal pod autoscaling configuration (covered conceptually in Phase IV guides, not implemented here)
- Cost optimization or multi-region deployment
- Service mesh (Istio/Linkerd) beyond what Dapr provides
- Mobile app or native desktop app

---

## Dependencies

- **Phase IV**: Docker images, Helm charts, Kubernetes manifests, Minikube deployment
- **Phase III**: Chatbot interface, MCP tools, OpenAI Agents SDK integration
- **Phase II**: Authentication (Better Auth + JWT), task CRUD API, Neon PostgreSQL database
- **Cloud Provider**: An active Oracle Cloud account with always-free tier enabled
- **Dapr**: Dapr CLI and runtime installed on the Kubernetes cluster
- **Kafka/Message Broker**: Strimzi operator or Redpanda deployed in-cluster, or a managed Kafka service
- **GitHub Actions**: Repository hosted on GitHub with Actions enabled
- **Container Registry**: Docker Hub, GHCR, or cloud-specific registry for storing built images

---

## Risks

- **Oracle Cloud always-free limitations**: The always-free tier has fixed resource limits (4 OCPUs, 24GB RAM). Mitigation: use minimal replica counts and resource requests; monitor cluster capacity.
- **Kafka resource consumption on Minikube**: Kafka/Strimzi can be resource-heavy on local machines. Mitigation: use Redpanda (lighter footprint) or minimal single-broker configuration.
- **Dapr learning curve**: Dapr introduces a new programming model. Mitigation: start with pub/sub only, add other building blocks incrementally.
