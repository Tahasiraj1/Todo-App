# Implementation Plan: Phase IV - Local Kubernetes Deployment

**Branch**: `004-k8s-local-deployment` | **Date**: 2026-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/4-k8s-local-deployment/spec.md`

## Summary

Deploy the Phase III Todo Chatbot (Next.js frontend + FastAPI backend + MCP server) to a local Kubernetes cluster using Minikube and Helm Charts. This involves containerizing both applications, creating Kubernetes manifests, packaging them into Helm charts, and documenting the deployment process.

## Technical Context

**Language/Version**:
- Frontend: Node.js 20+ (Next.js 15)
- Backend: Python 3.13 (FastAPI)
- Infrastructure: YAML (Kubernetes manifests, Helm templates)

**Primary Dependencies**:
- Docker Desktop 4.53+ (containerization)
- Minikube (local Kubernetes)
- Helm 3.x (package manager)
- kubectl (Kubernetes CLI)

**Storage**: External Neon PostgreSQL (not deployed in Kubernetes)

**Testing**:
- Container: `docker build` + `docker run` verification
- Kubernetes: `kubectl get pods`, `kubectl logs`, health endpoints
- Helm: `helm lint`, `helm template`, `helm test`

**Target Platform**: Linux containers on Minikube (local Kubernetes)

**Project Type**: Web application (frontend + backend monorepo)

**Performance Goals**:
- Container build < 5 minutes
- Pod startup < 30 seconds
- Application response < 200ms p95

**Constraints**:
- Combined image size < 1GB
- Minikube default resources (2 CPU, 4GB RAM)
- External database connectivity required

**Scale/Scope**:
- 2 deployments (frontend, backend)
- 2-3 replicas per deployment
- Single namespace

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Specification complete, planning in progress |
| II. AI-Native Implementation | ✅ PASS | All artifacts generated via Claude Code |
| III. Progressive Architecture | ✅ PASS | Building on Phase III, preparing for Phase V |
| IV. Stateless Service Architecture | ✅ PASS | Containers are stateless, state in Neon DB |
| V. Technology Stack Compliance | ✅ PASS | Using Docker, Minikube, Helm as specified |
| VI. Event-Driven Architecture | N/A | Phase V requirement, not applicable |
| VII. Independent Feature Testability | ✅ PASS | Each user story independently testable |
| VIII. Clean Code & Project Structure | ✅ PASS | Following monorepo structure |
| Development Environment (Linux) | ✅ PASS | All scripts and containers target Linux |

**Gate Result**: PASS - Proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/4-k8s-local-deployment/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output - technology decisions
├── data-model.md        # Phase 1 output - Kubernetes resource model
├── quickstart.md        # Phase 1 output - deployment guide
├── contracts/           # Phase 1 output - Helm values schema
│   └── values-schema.yaml
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
# Existing Phase III structure
backend/
├── Dockerfile           # EXISTS - needs review for K8s
├── src/
│   ├── main.py         # FastAPI entry point
│   ├── models/
│   ├── mcp_server/
│   └── ...
├── requirements.txt
└── pyproject.toml

frontend/
├── Dockerfile           # NEW - to be created
├── src/
│   ├── app/            # Next.js App Router
│   ├── components/
│   └── lib/
├── package.json
└── next.config.ts

# NEW Kubernetes infrastructure
k8s/
├── base/                # Raw Kubernetes manifests
│   ├── namespace.yaml
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   └── secrets/
│       └── app-secrets.yaml.example
│
└── helm/
    └── todo-chatbot/    # Helm chart
        ├── Chart.yaml
        ├── values.yaml
        ├── values-minikube.yaml
        ├── templates/
        │   ├── _helpers.tpl
        │   ├── namespace.yaml
        │   ├── frontend-deployment.yaml
        │   ├── frontend-service.yaml
        │   ├── frontend-configmap.yaml
        │   ├── backend-deployment.yaml
        │   ├── backend-service.yaml
        │   ├── backend-configmap.yaml
        │   └── secrets.yaml
        └── README.md
```

**Structure Decision**: Web application structure with dedicated `k8s/` directory for infrastructure-as-code. Helm chart packages all Kubernetes resources for single-command deployment.

## Complexity Tracking

No constitution violations requiring justification.

---

## Phase 0: Research Output

See [research.md](./research.md) for detailed technology decisions.

### Key Decisions Summary

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Container Registry | Minikube internal registry | Simplest for local dev, no external dependencies |
| Frontend Base Image | node:20-alpine | Small size, matches Next.js requirements |
| Backend Base Image | python:3.13-slim | Matches existing Dockerfile, smaller than full image |
| Service Exposure | NodePort | Works out-of-box with Minikube, no ingress needed |
| Health Checks | HTTP endpoints | Standard K8s pattern, already have /health in backend |
| Namespace | `todo-app` | Isolates resources, easy cleanup |

---

## Phase 1: Design Output

### Data Model

See [data-model.md](./data-model.md) for Kubernetes resource specifications.

### Contracts

See [contracts/values-schema.yaml](./contracts/values-schema.yaml) for Helm values schema.

### Quickstart

See [quickstart.md](./quickstart.md) for deployment instructions.

---

## Architecture Decisions

### AD-001: Minikube Internal Registry for Local Development

**Context**: Need to make container images available to Minikube cluster.

**Decision**: Use Minikube's built-in registry addon and `minikube image load` command.

**Alternatives Considered**:
- Docker Hub: Requires account, network upload/download overhead
- Local registry container: Additional complexity
- `minikube docker-env`: Requires building directly in Minikube's Docker

**Consequences**:
- Simplest setup for developers
- No external dependencies
- Images stay local

### AD-002: NodePort Service Type for External Access

**Context**: Need to access the frontend from host browser.

**Decision**: Use NodePort service type with `minikube service` command.

**Alternatives Considered**:
- LoadBalancer: Requires cloud provider or MetalLB
- Ingress: Additional complexity, reserved for Phase V
- Port-forward: Manual step, less production-like

**Consequences**:
- Works out-of-box with Minikube
- Automatic URL generation via `minikube service`
- Mimics cloud LoadBalancer behavior

### AD-003: Single Helm Chart for All Components

**Context**: Need to package frontend and backend for deployment.

**Decision**: Single Helm chart containing both frontend and backend.

**Alternatives Considered**:
- Separate charts per service: More flexible but complex for this scale
- Umbrella chart with subcharts: Overkill for 2 services

**Consequences**:
- Single `helm install` deploys everything
- Simpler version management
- Easier for developers to understand

---

## Post-Design Constitution Re-Check

| Principle | Status | Verification |
|-----------|--------|--------------|
| I. Spec-Driven Development | ✅ PASS | Plan references spec requirements |
| IV. Stateless Service Architecture | ✅ PASS | No PVCs, external DB only |
| V. Technology Stack Compliance | ✅ PASS | Docker, Minikube, Helm as required |
| VIII. Clean Code & Project Structure | ✅ PASS | Clear separation of concerns |

**Final Gate Result**: PASS - Ready for `/sp.tasks`
