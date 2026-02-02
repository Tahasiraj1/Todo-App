# Research: Phase V — Advanced Cloud Deployment

**Feature**: `005-cloud-event-deployment`
**Date**: 2026-01-31

---

## R1: Dapr on Kubernetes — Sidecar Injection & Component Model

**Decision**: Use Dapr with automatic sidecar injection via Kubernetes annotations.

**Rationale**: Dapr's sidecar model injects a container alongside the application pod. By adding annotations (`dapr.io/enabled: "true"`, `dapr.io/app-id`, `dapr.io/app-port`), the Dapr control plane injects the sidecar automatically. This is the standard Kubernetes deployment model for Dapr and avoids manual sidecar configuration.

**Alternatives considered**:
- Manual sidecar injection (explicitly adding Dapr container in deployment YAML) — rejected because annotation-based injection is simpler, less error-prone, and the recommended approach.
- Dapr standalone mode (no Kubernetes) — rejected because we're deploying on Kubernetes; the Kubernetes mode provides service discovery, mTLS, and component management natively.

**Key findings**:
- Dapr init on Kubernetes: `dapr init -k` installs the Dapr control plane (operator, sentry, placement, dashboard) into the `dapr-system` namespace.
- Sidecar annotations: `dapr.io/enabled: "true"`, `dapr.io/app-id: "todo-backend"`, `dapr.io/app-port: "8000"`.
- Dapr components are Kubernetes CRDs applied to the application namespace.
- The sidecar listens on `localhost:3500` (HTTP) and `localhost:50001` (gRPC) inside the pod.
- Dapr pub/sub subscription: the app exposes `GET /dapr/subscribe` returning topic subscriptions, or uses declarative subscription CRDs.

---

## R2: Kafka on Kubernetes — Strimzi vs Redpanda for Oracle OKE

**Decision**: Use Strimzi operator for Kafka on Oracle OKE. Fall back to Redpanda if Strimzi resource consumption is too high.

**Rationale**: Strimzi is the standard Kafka operator for Kubernetes with the broadest community support. On Oracle OKE's always-free tier (4 OCPUs, 24GB RAM), a single-broker Strimzi cluster with ephemeral storage is feasible. Redpanda is the fallback because it has a smaller memory footprint (no JVM).

**Alternatives considered**:
- Redpanda Cloud (managed) — viable but adds external dependency and network latency. Self-hosted keeps everything in-cluster for simpler networking.
- Confluent Cloud — free credits expire; not suitable for always-free deployment.
- Bitnami Kafka Helm chart — works but Strimzi provides better Kubernetes-native management (CRDs, topics as resources).

**Key findings**:
- Strimzi single-broker: `replicas: 1`, `ephemeral` storage, `listeners: [plain/9092/internal]`.
- Memory estimate: Kafka broker ~512MB-1GB, Strimzi operator ~256MB. Total ~1.5GB on the cluster.
- Strimzi topic CRD: `KafkaTopic` resources define topics declaratively.
- Dapr Kafka component: `pubsub.kafka` type, brokers point to `taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092`.
- Topics needed: `task-events`, `reminders`, `task-updates`.

---

## R3: Oracle OKE Always-Free Cluster Configuration

**Decision**: Use Oracle OKE with Arm-based A1 compute (always-free). Deploy minimal resource configurations.

**Rationale**: Oracle Cloud always-free tier provides 4 OCPUs and 24GB RAM on Arm A1 shapes. This is sufficient for a demo/learning deployment. Docker images must be built for `linux/arm64` architecture.

**Alternatives considered**:
- AMD shapes on Oracle — not always-free; would incur costs.
- Azure AKS / Google GKE — free credits expire (30/90 days); Oracle is indefinitely free.

**Key findings**:
- OKE cluster: 1 node pool with 2 A1.Flex nodes (2 OCPU, 12GB each = 4 OCPU, 24GB total).
- Docker multi-architecture builds required: `docker buildx build --platform linux/arm64`.
- Oracle Container Registry (OCIR) for image hosting: `<region>.ocir.io/<tenancy>/<repo>:<tag>`.
- kubectl access via OCI CLI: `oci ce cluster create-kubeconfig`.
- Ingress: Oracle provides a free cloud load balancer with OKE, or use NGINX Ingress Controller.

---

## R4: GitHub Actions CI/CD for Oracle OKE

**Decision**: GitHub Actions workflow with: build → test → push to OCIR → Helm upgrade on OKE.

**Rationale**: GitHub Actions is the mandated CI/CD tool. OCIR (Oracle Container Registry) is included free with Oracle Cloud. The pipeline uses `oracle-actions/run-oci-cli-command` for OKE authentication and `helm upgrade --install` for deployment.

**Alternatives considered**:
- Docker Hub as registry — works but OCIR is free, in-network with OKE, and avoids rate limits.
- ArgoCD for GitOps deployment — more complex; GitHub Actions with `helm upgrade` is simpler for this scope.

**Key findings**:
- GitHub Secrets needed: `OCI_CLI_USER`, `OCI_CLI_TENANCY`, `OCI_CLI_FINGERPRINT`, `OCI_CLI_KEY_CONTENT`, `OCI_CLI_REGION`, `OKE_CLUSTER_OCID`, `OCIR_USERNAME`, `OCIR_TOKEN`.
- Workflow stages: checkout → build images (multi-arch) → push to OCIR → configure kubectl → helm upgrade.
- Test stage: run backend tests (`pytest`) and frontend tests (`npm test`) before deployment.
- Branch strategy: deploy on push to `main` branch only.

---

## R5: Dapr Pub/Sub with Kafka Component

**Decision**: Use Dapr `pubsub.kafka` component pointing to in-cluster Strimzi Kafka. Application publishes via `POST localhost:3500/v1.0/publish/{pubsub-name}/{topic}` and subscribes via declarative subscription CRDs.

**Rationale**: Dapr abstracts Kafka — the application code makes HTTP POST calls to the Dapr sidecar, which handles Kafka producer/consumer internals. Declarative subscriptions (Kubernetes CRDs) are preferred over programmatic subscriptions because they're version-controlled and don't require application code changes.

**Alternatives considered**:
- Programmatic subscriptions (app exposes `/dapr/subscribe` endpoint) — works but mixes infrastructure concerns with application code.
- Direct Kafka client (aiokafka/kafka-python) — rejected per constitution §VI; Dapr must abstract Kafka.

**Key findings**:
- Dapr component YAML: `type: pubsub.kafka`, metadata: `brokers`, `consumerGroup`, `authRequired: false` (internal cluster).
- Declarative subscription CRD: `apiVersion: dapr.io/v2alpha1`, `kind: Subscription`, specifies topic, route (endpoint path), pubsub name, and scopes (app-ids that receive events).
- Publishing: `POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events` with JSON body.
- Receiving: Dapr POSTs to the configured route (e.g., `/api/events/task-events`) with CloudEvents envelope.

---

## R6: Dapr Jobs API for Scheduled Reminders

**Decision**: Use Dapr Jobs API (`/v1.0-alpha1/jobs/{name}`) for exact-time reminder scheduling instead of cron-based polling.

**Rationale**: The Jobs API schedules a callback at a specific time, avoiding the overhead and latency of periodic polling. When a task gets a due date, a job is scheduled for (due_date - reminder_window). When the job fires, the backend publishes a reminder event to the pub/sub.

**Alternatives considered**:
- Dapr Cron Binding — polls on a schedule (every N minutes), then queries DB for due tasks. Higher latency, unnecessary DB load.
- External scheduler (e.g., Celery Beat) — adds Python-specific dependency; Dapr Jobs is platform-agnostic.

**Key findings**:
- Schedule: `POST http://localhost:3500/v1.0-alpha1/jobs/reminder-{task_id}` with `dueTime` and `data`.
- Cancel: `DELETE http://localhost:3500/v1.0-alpha1/jobs/reminder-{task_id}` (when due date is removed or changed).
- Callback: Dapr calls `POST /api/jobs/reminder-{task_id}` on the backend at the scheduled time.
- The backend handler publishes to the `reminders` topic via pub/sub.
- Jobs API is alpha in Dapr 1.14+ but stable enough for this use case.

---

## R7: Browser Notifications Architecture

**Decision**: Use the Web Notifications API with a server-sent mechanism. The notification service subscribes to the `reminders` topic and delivers notifications to connected clients via WebSocket. If browser permission is denied, show an in-app banner.

**Rationale**: Browser Push Notifications (via service workers and push subscriptions) are complex and require a push server. For this scope, a simpler model works: the frontend maintains a WebSocket connection. When a reminder fires, the notification service pushes it to the user's connected sessions. The frontend uses the Notifications API if permitted, or falls back to an in-app banner.

**Alternatives considered**:
- Full Web Push API (service worker + push subscription) — production-grade but significantly more complex; overkill for a learning project.
- Server-Sent Events (SSE) — simpler than WebSocket but one-directional and less suitable since we also need real-time sync (bidirectional updates).

**Key findings**:
- WebSocket endpoint on the backend (or a dedicated notification service).
- Frontend requests `Notification.permission` on first visit.
- If `granted`: use `new Notification(title, {body, icon})` when a reminder arrives via WebSocket.
- If `denied` or `default`: display an in-app banner component in the task list UI.
- The same WebSocket connection serves both reminders and real-time task sync.

---

## R8: Task Model Extensions — Priority, Tags, Due Date, Recurrence

**Decision**: Extend the existing `Task` SQLModel with new columns. Use a JSON array column for tags (PostgreSQL native JSON support). Use structured fields for recurrence rules.

**Rationale**: Adding columns to the existing table is the simplest migration path. PostgreSQL JSON arrays provide flexible tag storage without a separate tags table. The structured recurrence fields (frequency, interval, day_of_week, day_of_month, end_date) were decided during clarification.

**Alternatives considered**:
- Separate `tags` table with many-to-many relationship — more normalized but adds join overhead and complexity for a simple feature.
- Separate `recurrence_rules` table — unnecessary; the rule is a property of the task, not a shared entity.

**Key findings**:
- New Task columns: `priority` (VARCHAR, default "medium"), `tags` (JSON array, default []), `due_date` (TIMESTAMP WITH TIME ZONE, nullable), `recurrence_frequency` (VARCHAR, nullable), `recurrence_interval` (INT, default 1), `recurrence_day_of_week` (INT, nullable), `recurrence_day_of_month` (INT, nullable), `recurrence_end_date` (TIMESTAMP, nullable), `is_recurring` (BOOL, default false).
- Schema migration: SQLModel `create_all()` handles new columns in development. For production, Alembic migrations recommended.
- MCP tools update: `add_task` gains priority, tags, due_date, recurrence parameters. `list_tasks` gains filter/sort parameters.

---

## R9: New Microservices Architecture

**Decision**: Add 2 new lightweight services alongside the existing backend: a Notification Service and a Recurring Task Service. Both consume events from Kafka via Dapr pub/sub.

**Rationale**: Separating concerns into event consumers follows the event-driven architecture mandate. The notification service handles reminders and WebSocket delivery. The recurring task service handles automatic task re-creation. Both are stateless consumers that can scale independently.

**Alternatives considered**:
- Single monolithic backend that also consumes events — simpler but violates the microservice architecture goal and couples event processing with request handling.
- Three additional services (notification + recurring + audit) — audit log can be handled by the existing backend as a simple database write, avoiding a third service.

**Key findings**:
- **Notification Service**: Subscribes to `reminders` and `task-updates` topics. Maintains WebSocket connections to clients. Delivers browser notifications and real-time updates.
- **Recurring Task Service**: Subscribes to `task-events` topic. When a `completed` event arrives for a recurring task, creates the next occurrence via Dapr service invocation to the backend.
- **Activity Log**: Handled by the backend itself — subscribes to `task-events` and persists to an `activity_log` table. Keeps it simple without a separate service.
- Docker images: Each service gets its own Dockerfile and Helm deployment.
