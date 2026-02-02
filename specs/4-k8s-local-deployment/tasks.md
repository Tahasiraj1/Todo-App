# Tasks: Phase IV - Local Kubernetes Deployment

**Input**: Design documents from `/specs/4-k8s-local-deployment/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested - focusing on verification via deployment testing.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Infrastructure**: `k8s/` at repository root
- **Dockerfiles**: `frontend/Dockerfile`, `backend/Dockerfile`
- **Helm Chart**: `k8s/helm/todo-chatbot/`
- **Base Manifests**: `k8s/base/`

---

## Phase 1: Setup (Project Infrastructure)

**Purpose**: Create directory structure and verify prerequisites

- [x] T001 Create k8s/ directory structure per plan.md at k8s/
- [x] T002 [P] Verify Docker Desktop is installed and running
- [x] T003 [P] Verify Minikube is installed (minikube version)
- [x] T004 [P] Verify kubectl is installed (kubectl version --client)
- [x] T005 [P] Verify Helm is installed (helm version)
- [x] T006 Verify backend health endpoint exists at backend/src/main.py (GET /health)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prepare base infrastructure and verify Phase III application readiness

**⚠️ CRITICAL**: No Kubernetes deployment work can begin until this phase is complete

- [x] T007 Start Minikube cluster with recommended resources (minikube start --cpus=2 --memory=4096)
- [x] T008 Verify Minikube is running and accessible (minikube status)
- [x] T009 Create namespace manifest at k8s/base/namespace.yaml
- [x] T010 Create secrets example template at k8s/base/secrets/app-secrets.yaml.example
- [x] T011 Verify frontend application builds successfully (cd frontend && npm run build)
- [x] T012 Verify backend application runs successfully (cd backend && uvicorn src.main:app)

**Checkpoint**: Foundation ready - containerization work can now begin

---

## Phase 3: User Story 1 - Developer Containerizes Applications (Priority: P1) 🎯 MVP

**Goal**: Package frontend and backend into production-ready container images

**Independent Test**: Build images with `docker build`, run with `docker run`, verify chatbot works in containerized form

### Implementation for User Story 1

- [x] T013 [P] [US1] Create frontend Dockerfile with multi-stage build at frontend/Dockerfile
- [x] T014 [P] [US1] Create frontend .dockerignore at frontend/.dockerignore
- [x] T015 [P] [US1] Update backend Dockerfile for Kubernetes compatibility at backend/Dockerfile
- [x] T016 [P] [US1] Verify backend .dockerignore exists at backend/.dockerignore
- [x] T017 [US1] Add frontend health check API route at frontend/src/app/api/health/route.ts
- [x] T018 [US1] Build frontend container image (docker build -t todo-frontend:latest ./frontend)
- [x] T019 [US1] Build backend container image (docker build -t todo-backend:latest ./backend)
- [x] T020 [US1] Verify frontend image size is under 500MB (docker images todo-frontend)
- [x] T021 [US1] Verify backend image size is under 500MB (docker images todo-backend)
- [x] T022 [US1] Test frontend container runs standalone (docker run -p 3000:3000 todo-frontend)
- [x] T023 [US1] Test backend container runs standalone (docker run -p 8000:8000 todo-backend)
- [x] T024 [US1] Test containers run together with docker-compose or manual networking

**Checkpoint**: Both container images built and verified working locally with Docker

---

## Phase 4: User Story 2 - Developer Deploys to Local Kubernetes Cluster (Priority: P1)

**Goal**: Deploy containerized Todo Chatbot to Minikube with raw Kubernetes manifests

**Independent Test**: Apply manifests to Minikube, verify pods running, access chatbot via NodePort

### Implementation for User Story 2

- [x] T025 [US2] Load frontend image into Minikube (minikube image load todo-frontend:latest)
- [x] T026 [US2] Load backend image into Minikube (minikube image load todo-backend:latest)
- [x] T027 [P] [US2] Create frontend ConfigMap at k8s/base/frontend/configmap.yaml
- [x] T028 [P] [US2] Create backend ConfigMap at k8s/base/backend/configmap.yaml
- [x] T029 [P] [US2] Create frontend Deployment manifest at k8s/base/frontend/deployment.yaml
- [x] T030 [P] [US2] Create backend Deployment manifest at k8s/base/backend/deployment.yaml
- [x] T031 [P] [US2] Create frontend Service (NodePort) manifest at k8s/base/frontend/service.yaml
- [x] T032 [P] [US2] Create backend Service (ClusterIP) manifest at k8s/base/backend/service.yaml
- [x] T033 [US2] Apply namespace to Minikube (kubectl apply -f k8s/base/namespace.yaml)
- [x] T034 [US2] Create Kubernetes secrets from environment (kubectl create secret generic)
- [x] T035 [US2] Apply all base manifests to Minikube (kubectl apply -f k8s/base/ -R)
- [x] T036 [US2] Verify pods reach Running state (kubectl get pods -n todo-app)
- [x] T037 [US2] Verify services are created (kubectl get svc -n todo-app)
- [x] T038 [US2] Get frontend URL via minikube service (minikube service todo-frontend -n todo-app --url)
- [x] T039 [US2] Test chatbot functionality through Kubernetes deployment

**Checkpoint**: Todo Chatbot deployed and functional on Minikube using raw manifests

---

## Phase 5: User Story 3 - Developer Uses Helm Charts for Deployment (Priority: P2)

**Goal**: Package all Kubernetes resources into a Helm chart for repeatable deployment

**Independent Test**: helm install deploys all resources, helm upgrade modifies deployment, helm uninstall cleans up

### Implementation for User Story 3

- [x] T040 [P] [US3] Create Helm chart structure at k8s/helm/todo-chatbot/
- [x] T041 [P] [US3] Create Chart.yaml with metadata at k8s/helm/todo-chatbot/Chart.yaml
- [x] T042 [P] [US3] Create values.yaml with defaults at k8s/helm/todo-chatbot/values.yaml
- [x] T043 [P] [US3] Create values-minikube.yaml for local overrides at k8s/helm/todo-chatbot/values-minikube.yaml
- [x] T044 [US3] Create _helpers.tpl with template functions at k8s/helm/todo-chatbot/templates/_helpers.tpl
- [x] T045 [P] [US3] Create namespace template at k8s/helm/todo-chatbot/templates/namespace.yaml
- [x] T046 [P] [US3] Create secrets template at k8s/helm/todo-chatbot/templates/secrets.yaml
- [x] T047 [P] [US3] Create frontend-configmap template at k8s/helm/todo-chatbot/templates/frontend-configmap.yaml
- [x] T048 [P] [US3] Create frontend-deployment template at k8s/helm/todo-chatbot/templates/frontend-deployment.yaml
- [x] T049 [P] [US3] Create frontend-service template at k8s/helm/todo-chatbot/templates/frontend-service.yaml
- [x] T050 [P] [US3] Create backend-configmap template at k8s/helm/todo-chatbot/templates/backend-configmap.yaml
- [x] T051 [P] [US3] Create backend-deployment template at k8s/helm/todo-chatbot/templates/backend-deployment.yaml
- [x] T052 [P] [US3] Create backend-service template at k8s/helm/todo-chatbot/templates/backend-service.yaml
- [x] T053 [US3] Lint Helm chart (helm lint k8s/helm/todo-chatbot)
- [x] T054 [US3] Test template rendering (helm template todo-chatbot k8s/helm/todo-chatbot)
- [x] T055 [US3] Clean up previous raw manifest deployment (kubectl delete -f k8s/base/ -R)
- [x] T056 [US3] Install Helm chart to Minikube (helm install todo-chatbot k8s/helm/todo-chatbot -n todo-app)
- [x] T057 [US3] Verify all resources created via Helm (kubectl get all -n todo-app)
- [x] T058 [US3] Test helm upgrade with modified values (helm upgrade todo-chatbot k8s/helm/todo-chatbot --set frontend.replicaCount=2)
- [x] T059 [US3] Verify upgraded deployment (kubectl get pods -n todo-app)
- [x] T060 [US3] Test helm uninstall (helm uninstall todo-chatbot -n todo-app)
- [x] T061 [US3] Verify clean removal (kubectl get all -n todo-app)
- [x] T062 [US3] Create Helm chart README at k8s/helm/todo-chatbot/README.md

**Checkpoint**: Helm chart working for install, upgrade, and uninstall operations

---

## Phase 6: User Story 4 - Developer Uses AI-Assisted Kubernetes Operations (Priority: P3)

**Goal**: Document optional AI-assisted operations using kubectl-ai, kagent, and Docker AI Gordon

**Independent Test**: Execute documented commands and verify AI tools provide correct assistance

### Implementation for User Story 4

- [x] T063 [P] [US4] Document kubectl-ai installation in docs/ai-ops.md
- [x] T064 [P] [US4] Document Docker AI (Gordon) usage examples in docs/ai-ops.md
- [x] T065 [P] [US4] Document kagent installation and usage in docs/ai-ops.md
- [x] T066 [US4] Test kubectl-ai with example deployment command (if available)
- [x] T067 [US4] Test Docker AI Gordon with container build help (if available)
- [x] T068 [US4] Document common AI-assisted operation examples in docs/ai-ops.md

**Checkpoint**: AI-assisted operations documented (optional enhancement complete)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [x] T069 [P] Update main README.md with Phase IV deployment instructions
- [x] T070 [P] Create docs/kubernetes-deployment.md with detailed deployment guide
- [x] T071 [P] Create docs/troubleshooting.md with common issues and solutions
- [x] T072 Validate quickstart.md steps work end-to-end
- [x] T073 Verify SC-001: Build time under 5 minutes
- [x] T074 Verify SC-002: Combined image size under 1GB
- [x] T075 Verify SC-003: Single helm install deploys complete application
- [x] T076 Verify SC-004: Pods reach Running state within 3 minutes
- [x] T077 Verify SC-005: Full chatbot functionality (auth, tasks, AI chat)
- [x] T078 Verify SC-008: New developer can complete deployment in 30 minutes
- [x] T079 Verify SC-009: Pod auto-restart on termination (kubectl delete pod)
- [x] T080 Final cleanup and code review

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ──────────────────────────────────────┐
                                                     │
Phase 2: Foundational ◄──────────────────────────────┘
         (BLOCKS all user stories)                   │
                                                     ▼
                        ┌────────────────────────────┼────────────────────────────┐
                        │                            │                            │
                        ▼                            ▼                            ▼
Phase 3: US1 ──────► Phase 4: US2 ──────────► Phase 5: US3 ──────► Phase 6: US4
Containerization      K8s Manifests             Helm Charts         AI-Ops (Optional)
         │                            │                            │
         └────────────────────────────┴────────────────────────────┘
                                                     │
                                                     ▼
                                          Phase 7: Polish
```

### User Story Dependencies

| Story | Depends On | Can Run In Parallel With |
|-------|-----------|-------------------------|
| US1 (Containerization) | Phase 2 (Foundational) | None (must complete first) |
| US2 (K8s Manifests) | US1 (needs container images) | None |
| US3 (Helm Charts) | US2 (needs working manifests as reference) | None |
| US4 (AI-Ops) | US3 (needs complete deployment) | Polish phase |

**Note**: US1 → US2 → US3 is a strict sequence because each builds on the previous. US4 is optional and independent.

### Parallel Opportunities Within Phases

**Phase 1 (Setup)**:
- T002, T003, T004, T005 can all run in parallel (tool verification)

**Phase 3 (US1 - Containerization)**:
- T013, T014 (frontend Docker files) parallel with T015, T016 (backend Docker files)

**Phase 4 (US2 - K8s Manifests)**:
- T027, T028 (ConfigMaps) can run in parallel
- T029, T030 (Deployments) can run in parallel
- T031, T032 (Services) can run in parallel

**Phase 5 (US3 - Helm Charts)**:
- T040-T043 (chart structure files) can run in parallel
- T045-T052 (all templates) can run in parallel

**Phase 6 (US4 - AI-Ops)**:
- T063, T064, T065 (documentation) can run in parallel

**Phase 7 (Polish)**:
- T069, T070, T071 (documentation files) can run in parallel

---

## Parallel Example: User Story 3 (Helm Charts)

```bash
# Launch all templates in parallel:
Task: "Create namespace template at k8s/helm/todo-chatbot/templates/namespace.yaml"
Task: "Create secrets template at k8s/helm/todo-chatbot/templates/secrets.yaml"
Task: "Create frontend-configmap template at k8s/helm/todo-chatbot/templates/frontend-configmap.yaml"
Task: "Create frontend-deployment template at k8s/helm/todo-chatbot/templates/frontend-deployment.yaml"
Task: "Create frontend-service template at k8s/helm/todo-chatbot/templates/frontend-service.yaml"
Task: "Create backend-configmap template at k8s/helm/todo-chatbot/templates/backend-configmap.yaml"
Task: "Create backend-deployment template at k8s/helm/todo-chatbot/templates/backend-deployment.yaml"
Task: "Create backend-service template at k8s/helm/todo-chatbot/templates/backend-service.yaml"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Containerization)
4. **CHECKPOINT**: Verify containers work with Docker
5. Complete Phase 4: User Story 2 (K8s Manifests)
6. **CHECKPOINT**: Verify deployment works on Minikube
7. **MVP COMPLETE**: Application running on Kubernetes!

### Full Delivery (All User Stories)

1. Complete MVP (above)
2. Complete Phase 5: User Story 3 (Helm Charts)
3. **CHECKPOINT**: Verify helm install/upgrade/uninstall
4. Complete Phase 6: User Story 4 (AI-Ops) - Optional
5. Complete Phase 7: Polish
6. **FEATURE COMPLETE**: Full Phase IV delivered

### Incremental Milestones

| Milestone | Stories Complete | Deliverable |
|-----------|-----------------|-------------|
| M1 | US1 | Container images ready |
| M2 | US1 + US2 | Running on Minikube (MVP) |
| M3 | US1 + US2 + US3 | Helm-based deployment |
| M4 | All | Full Phase IV with AI-Ops |

---

## Task Summary

| Phase | Story | Task Count | Parallel Tasks |
|-------|-------|------------|----------------|
| Phase 1 | Setup | 6 | 4 |
| Phase 2 | Foundational | 6 | 0 |
| Phase 3 | US1 - Containerization | 12 | 4 |
| Phase 4 | US2 - K8s Manifests | 15 | 6 |
| Phase 5 | US3 - Helm Charts | 23 | 11 |
| Phase 6 | US4 - AI-Ops | 6 | 3 |
| Phase 7 | Polish | 12 | 3 |
| **Total** | | **80** | **31** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US1 → US2 → US3 is a strict sequence (each builds on previous)
- US4 is optional and can be done in parallel with Polish phase
- Verify at each checkpoint before proceeding
- Container images must be loaded into Minikube before K8s deployment
- Secrets must be created before applying deployments
- Commit after each completed phase
