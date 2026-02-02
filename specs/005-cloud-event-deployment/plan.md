# Implementation Plan: Phase V — Advanced Cloud Deployment

**Branch**: `005-cloud-event-deployment` | **Date**: 2026-01-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/005-cloud-event-deployment/spec.md`

## Summary

Extend the Todo App with intermediate features (priorities, tags, search/filter/sort), advanced features (due dates, reminders, recurring tasks), and event-driven architecture (Kafka via Dapr). Deploy to Oracle Cloud OKE with CI/CD via GitHub Actions. The architecture adds Dapr sidecars to all services, introduces two new microservices (notification service, recurring task service), and publishes all task mutations as events to Kafka topics.

## Technical Context

**Language/Version**: Python 3.13+ (backend, new services), TypeScript (frontend, Next.js App Router)
**Primary Dependencies**: FastAPI, SQLModel, Dapr SDK (HTTP), OpenAI Agents SDK, Next.js, Strimzi (Kafka operator)
**Storage**: Neon PostgreSQL (primary), Kafka topics (event streaming, 7-day retention)
**Testing**: pytest (backend), vitest/jest (frontend), manual E2E
**Target Platform**: Oracle Cloud OKE (Arm A1, always-free: 4 OCPUs, 24GB RAM)
**Project Type**: web (monorepo: frontend + backend + services)
**Performance Goals**: Event processing < 500ms, chat response < 3s, 100+ concurrent users
**Constraints**: All infrastructure access through Dapr HTTP APIs (no direct Kafka/DB client libraries for event operations), at-least-once delivery with idempotent consumers, ARM64 Docker images for OKE
**Scale/Scope**: 100 concurrent users, 3 Kafka topics, 4 services (frontend, backend, notification, recurring-task)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Spec-Driven Development** | PASS | Spec complete with 10 stories, 30 FRs, 12 SCs. Plan follows spec. |
| **II. AI-Native Implementation** | PASS | All code generated via Claude Code. |
| **III. Progressive Architecture** | PASS | Phase V builds on Phase IV (K8s), III (chatbot), II (web). |
| **IV. Stateless Services** | PASS | All services stateless. State in Neon DB + Kafka topics. WebSocket connections are ephemeral. |
| **V. Technology Stack** | PASS | Kafka (Strimzi), Dapr, Oracle OKE, GitHub Actions — all mandated stack. |
| **VI. Event-Driven Architecture** | PASS | Task operations publish to Kafka via Dapr. Services communicate via events. Event schemas documented in data-model.md. |
| **VII. Independent Feature Testability** | PASS | Each story is independently testable per spec. Priorities/tags work without events. Events work without cloud deployment. |
| **VIII. Clean Code & Project Structure** | PASS | Monorepo structure with backend/, frontend/, services/. |

**Gate result**: PASS — no violations. Proceed to design.

## Project Structure

### Documentation (this feature)

```text
specs/005-cloud-event-deployment/
├── spec.md                 # Feature specification (complete)
├── plan.md                 # This file
├── research.md             # Phase 0: technology research
├── data-model.md           # Phase 1: entity model + event schemas
├── quickstart.md           # Phase 1: development guide
├── contracts/
│   ├── api-extensions.yaml # Phase 1: OpenAPI contract extensions
│   ├── dapr-components.yaml# Phase 1: Dapr component contracts
│   └── helm-values-schema.yaml # Phase 1: Helm values extensions
├── checklists/
│   └── requirements.md     # Quality checklist
└── tasks.md                # Phase 2: task breakdown (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                    # FastAPI app (existing, extend with Dapr routes)
│   ├── db.py                      # Database engine (existing, unchanged)
│   ├── api/
│   │   ├── routes/
│   │   │   ├── tasks.py           # Task CRUD (extend with filter/sort/search)
│   │   │   ├── chat.py            # Chat endpoint (existing, unchanged)
│   │   │   ├── events.py          # NEW: Dapr subscription handlers
│   │   │   ├── jobs.py            # NEW: Dapr Jobs callback handlers
│   │   │   ├── activity.py        # NEW: Activity log endpoint
│   │   │   └── websocket.py       # NEW: WebSocket endpoint for real-time sync
│   │   └── dependencies.py        # Auth dependencies (existing, unchanged)
│   ├── models/
│   │   ├── task.py                # Task model (extend with new fields)
│   │   ├── activity_log.py        # NEW: ActivityLogEntry model
│   │   ├── schemas.py             # Pydantic schemas (extend TaskCreate/Update/Response)
│   │   └── events.py              # NEW: Event schemas (TaskEvent, ReminderEvent)
│   ├── services/
│   │   ├── task_service.py        # Task logic (extend with filter/sort, event publishing)
│   │   ├── event_service.py       # NEW: Event publishing via Dapr HTTP
│   │   ├── activity_service.py    # NEW: Activity log CRUD
│   │   ├── reminder_service.py    # NEW: Dapr Jobs scheduling for reminders
│   │   └── websocket_manager.py   # NEW: WebSocket connection manager
│   ├── agent/
│   │   ├── agent.py               # Agent config (update instructions for new tools)
│   │   └── tools.py               # MCP tools (extend with priority, tags, due_date, etc.)
│   └── middleware/
│       └── auth.py                # JWT verification (existing, unchanged)
└── tests/

services/
├── notification/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── main.py                # FastAPI app for notification service
│       └── handlers.py            # Dapr subscription handlers (reminders, task-updates)
└── recurring-task/
    ├── Dockerfile
    ├── requirements.txt
    └── src/
        ├── main.py                # FastAPI app for recurring task service
        └── handlers.py            # Dapr subscription handler (task-completed events)

frontend/
├── src/
│   ├── app/
│   │   └── dashboard/page.tsx     # Extend with filter/sort UI
│   ├── components/
│   │   ├── tasks/
│   │   │   ├── task-item.tsx      # Extend with priority badge, tags, due date, overdue indicator
│   │   │   ├── task-form.tsx      # Extend with priority, tags, due date, recurrence inputs
│   │   │   ├── task-filters.tsx   # NEW: Filter/sort controls
│   │   │   └── reminder-banner.tsx# NEW: In-app reminder banner
│   │   ├── activity/
│   │   │   └── activity-log.tsx   # NEW: Activity log component
│   │   └── notifications/
│   │       └── notification-provider.tsx # NEW: WebSocket + browser notification provider
│   ├── lib/
│   │   ├── api.ts                 # Extend with filter/sort params, activity endpoint
│   │   ├── websocket.ts           # NEW: WebSocket client
│   │   └── notifications.ts       # NEW: Browser notification utilities
│   └── types/
│       └── task.ts                # Extend with priority, tags, due_date, etc.
└── tests/

k8s/
├── kafka/
│   └── kafka-cluster.yaml         # NEW: Strimzi Kafka cluster definition
├── dapr/
│   ├── kafka-pubsub.yaml          # NEW: Dapr pub/sub component
│   ├── subscriptions.yaml         # NEW: Declarative subscriptions
│   └── kubernetes-secrets.yaml    # NEW: Dapr secrets store
├── helm/todo-chatbot/
│   ├── templates/
│   │   ├── notification-deployment.yaml  # NEW
│   │   ├── notification-service.yaml     # NEW
│   │   ├── recurring-task-deployment.yaml# NEW
│   │   └── recurring-task-service.yaml   # NEW
│   ├── values.yaml                # Extend with Dapr, Kafka, new services
│   └── values-oke.yaml            # NEW: Oracle OKE overrides
└── base/                          # Existing base manifests (unchanged)

.github/
└── workflows/
    └── deploy.yaml                # NEW: CI/CD pipeline
```

**Structure Decision**: Web application monorepo with `backend/`, `frontend/`, and new `services/` directory for additional microservices. Kubernetes manifests in `k8s/` with separate directories for Kafka and Dapr resources.

## Architecture Overview

### Service Topology

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER (Oracle OKE)                  │
│                                                                         │
│  ┌────────────────────┐    ┌──────────────────────────┐                │
│  │   Frontend Pod     │    │      Backend Pod          │                │
│  │ ┌────────┐┌──────┐│    │ ┌────────┐ ┌────────────┐│                │
│  │ │Next.js ││ Dapr ││    │ │FastAPI │ │    Dapr    ││                │
│  │ │  App   ││Sidecar││───▶│ │ + MCP  │◀▶│  Sidecar   ││──┐            │
│  │ └────────┘└──────┘│    │ │ Tools  │ │(publish/   ││  │            │
│  └────────────────────┘    │ └────────┘ │subscribe/  ││  │            │
│                            │            │jobs/secrets)││  │            │
│                            └────────────┴────────────┘┘  │            │
│                                                          │            │
│     ┌──────────────────────┐     ┌──────────────────┐    │            │
│     │  Notification Pod    │     │ Recurring Task    │    │            │
│     │ ┌────────┐┌────────┐│     │ ┌────────┐┌─────┐│    │            │
│     │ │Notif.  ││ Dapr   ││     │ │Recur.  ││Dapr ││    │            │
│     │ │Service ││Sidecar ││     │ │Service ││Side.││    │            │
│     │ │+WebSock││(subscr.)││     │ │        ││     ││    │            │
│     │ └────────┘└────────┘│     │ └────────┘└─────┘│    │            │
│     └──────────────────────┘     └──────────────────┘    │            │
│              ▲                           ▲                │            │
│              │                           │                │            │
│              └───────────┬───────────────┘                │            │
│                          │                                │            │
│               ┌──────────▼─────────────────┐              │            │
│               │    KAFKA (Strimzi)          │◀─────────────┘            │
│               │  ┌─────────────────────┐   │                           │
│               │  │ task-events         │   │                           │
│               │  │ reminders           │   │                           │
│               │  │ task-updates        │   │                           │
│               │  └─────────────────────┘   │                           │
│               └────────────────────────────┘                           │
│                                                                         │
│  External:  Neon PostgreSQL (managed)    OCIR (container registry)     │
└─────────────────────────────────────────────────────────────────────────┘
```

### Event Flow

```
User action (create/update/complete/delete task)
     │
     ▼
Backend (FastAPI)
     │
     ├── 1. Mutate task in Neon DB
     ├── 2. Publish to task-events topic (via Dapr pub/sub)
     ├── 3. Publish to task-updates topic (via Dapr pub/sub)
     ├── 4. If due_date set: schedule Dapr Job for reminder
     │
     ▼
Kafka Topics
     │
     ├── task-events ──▶ Backend (activity log handler) ──▶ activity_log table
     │                ──▶ Recurring Task Service ──▶ (if completed + recurring) ──▶ create next task via Dapr service invocation
     │
     ├── reminders ───▶ Notification Service ──▶ WebSocket ──▶ Browser notification / in-app banner
     │
     └── task-updates ──▶ Notification Service ──▶ WebSocket ──▶ Real-time UI update in all tabs
```

### CI/CD Pipeline

```
Push to main
     │
     ▼
GitHub Actions
     │
     ├── Stage 1: Checkout + Setup
     ├── Stage 2: Run backend tests (pytest)
     ├── Stage 3: Run frontend tests
     ├── Stage 4: Build Docker images (ARM64 for OKE)
     ├── Stage 5: Push to OCIR
     ├── Stage 6: Configure kubectl for OKE
     └── Stage 7: Helm upgrade on OKE cluster
```

## Implementation Phases

### Phase A: Task Model & API Extensions (P1 features)

**Goal**: Priorities, tags, search, filter, sort — working locally without events.

1. Extend Task SQLModel with new columns (priority, tags, due_date, recurrence fields)
2. Update Pydantic schemas (TaskCreate, TaskUpdate, TaskResponse)
3. Extend task routes with query parameters (priority, tag, search, sort_by, sort_order, overdue)
4. Update TaskService with filtering, sorting, and search logic
5. Update MCP tools (add_task, list_tasks, update_task) to handle new parameters
6. Update agent instructions to recognize new intents (filter, sort, search)
7. Extend frontend task components (priority badge, tags, due date display, filter/sort controls)
8. Update frontend API client and TypeScript types

### Phase B: Dapr & Kafka Infrastructure

**Goal**: Dapr sidecar injection and Kafka cluster running on Minikube.

1. Install Dapr on Minikube cluster
2. Deploy Strimzi operator and Kafka cluster (single broker, ephemeral)
3. Create Dapr pub/sub component (kafka-pubsub)
4. Create declarative subscription CRDs
5. Create Dapr secrets store component
6. Update Helm chart: add Dapr annotations to backend deployment
7. Verify sidecar injection: backend pod has 2 containers (app + daprd)
8. Smoke test: publish event via Dapr HTTP API, verify delivery

### Phase C: Event-Driven Features (P2 features)

**Goal**: Event publishing, activity log, reminders, recurring tasks.

1. Create EventService: publish task events via Dapr HTTP to task-events and task-updates topics
2. Integrate event publishing into TaskService (after each mutation)
3. Create ActivityLogEntry model and ActivityService
4. Create Dapr subscription handler route for task-events → persist to activity_log
5. Create activity log API endpoint (GET /api/{user_id}/activity)
6. Create ReminderService: schedule/cancel Dapr Jobs when due_date changes
7. Create Dapr Jobs callback handler: publish to reminders topic when job fires
8. Build Notification Service (new microservice): subscribe to reminders + task-updates
9. Build Recurring Task Service (new microservice): subscribe to task-events, create next occurrence
10. Create WebSocket endpoint + connection manager in backend
11. Frontend: WebSocket client, browser notification provider, in-app reminder banner
12. Frontend: activity log view

### Phase D: Cloud Deployment (Oracle OKE)

**Goal**: Full application running on Oracle Cloud.

1. Provision Oracle OKE cluster (A1 shapes, always-free)
2. Configure OCIR (Oracle Container Registry)
3. Build ARM64 Docker images for all services
4. Push images to OCIR
5. Create values-oke.yaml with cloud-specific overrides
6. Deploy Dapr, Strimzi, and application to OKE via Helm
7. Configure Ingress / load balancer for external access
8. Verify end-to-end functionality on cloud

### Phase E: CI/CD Pipeline

**Goal**: Automated build-test-deploy on push to main.

1. Create GitHub Actions workflow file
2. Configure GitHub Secrets (OCI credentials, cluster OCID, registry token)
3. Implement stages: checkout → test → build → push → deploy
4. Test pipeline with a sample push
5. Verify zero-downtime deployment (rolling update)

## Complexity Tracking

No constitution violations. No complexity justifications needed.

## Design Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Research | `specs/005-cloud-event-deployment/research.md` | Complete |
| Data Model | `specs/005-cloud-event-deployment/data-model.md` | Complete |
| API Contracts | `specs/005-cloud-event-deployment/contracts/api-extensions.yaml` | Complete |
| Dapr Contracts | `specs/005-cloud-event-deployment/contracts/dapr-components.yaml` | Complete |
| Helm Schema | `specs/005-cloud-event-deployment/contracts/helm-values-schema.yaml` | Complete |
| Quickstart | `specs/005-cloud-event-deployment/quickstart.md` | Complete |
| Tasks | `specs/005-cloud-event-deployment/tasks.md` | Pending (`/sp.tasks`) |
