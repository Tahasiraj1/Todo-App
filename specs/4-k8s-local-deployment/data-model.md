# Data Model: Phase IV - Kubernetes Resources

**Date**: 2026-01-27
**Feature**: 4-k8s-local-deployment
**Purpose**: Define Kubernetes resource specifications for the Todo Chatbot

---

## Overview

This document defines the Kubernetes resources required to deploy the Todo Chatbot application. Unlike traditional data models with database entities, this feature's "data model" consists of Kubernetes resource definitions.

---

## Resource Hierarchy

```
Namespace: todo-app
├── Deployments
│   ├── todo-frontend (1-3 replicas)
│   └── todo-backend (1-3 replicas)
├── Services
│   ├── todo-frontend (NodePort)
│   └── todo-backend (ClusterIP)
├── ConfigMaps
│   ├── frontend-config
│   └── backend-config
└── Secrets
    └── todo-secrets
```

---

## 1. Namespace

**Resource**: `Namespace`
**Name**: `todo-app`

| Field | Value | Description |
|-------|-------|-------------|
| name | `todo-app` | Namespace name |
| labels.app | `todo-chatbot` | Application identifier |
| labels.phase | `phase-4` | Hackathon phase |

**Purpose**: Isolates all Todo Chatbot resources for easy management and cleanup.

---

## 2. Frontend Deployment

**Resource**: `Deployment`
**Name**: `todo-frontend`

### Pod Specification

| Field | Value | Description |
|-------|-------|-------------|
| replicas | 1 (configurable) | Number of pod replicas |
| image | `todo-frontend:latest` | Container image |
| containerPort | 3000 | Next.js default port |
| imagePullPolicy | `IfNotPresent` | Use local image |

### Resource Limits

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 100m | 500m |
| Memory | 256Mi | 512Mi |

### Probes

| Probe | Path | Port | Initial Delay | Period |
|-------|------|------|---------------|--------|
| Liveness | `/api/health` | 3000 | 15s | 10s |
| Readiness | `/api/health` | 3000 | 5s | 5s |

### Environment Variables (from ConfigMap)

| Variable | Source | Description |
|----------|--------|-------------|
| `NEXT_PUBLIC_API_URL` | ConfigMap | Backend API URL |
| `NODE_ENV` | ConfigMap | Runtime environment |

### Environment Variables (from Secret)

| Variable | Source | Description |
|----------|--------|-------------|
| `BETTER_AUTH_SECRET` | Secret | JWT signing key |

---

## 3. Backend Deployment

**Resource**: `Deployment`
**Name**: `todo-backend`

### Pod Specification

| Field | Value | Description |
|-------|-------|-------------|
| replicas | 1 (configurable) | Number of pod replicas |
| image | `todo-backend:latest` | Container image |
| containerPort | 8000 | FastAPI port |
| imagePullPolicy | `IfNotPresent` | Use local image |

### Resource Limits

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 100m | 500m |
| Memory | 256Mi | 512Mi |

### Probes

| Probe | Path | Port | Initial Delay | Period |
|-------|------|------|---------------|--------|
| Liveness | `/health` | 8000 | 15s | 10s |
| Readiness | `/health` | 8000 | 5s | 5s |

### Environment Variables (from ConfigMap)

| Variable | Source | Description |
|----------|--------|-------------|
| `LOG_LEVEL` | ConfigMap | Logging verbosity |
| `CORS_ORIGINS` | ConfigMap | Allowed CORS origins |

### Environment Variables (from Secret)

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | Secret | Neon PostgreSQL connection |
| `OPENAI_API_KEY` | Secret | OpenAI API key |
| `BETTER_AUTH_SECRET` | Secret | JWT signing key |

---

## 4. Frontend Service

**Resource**: `Service`
**Name**: `todo-frontend`

| Field | Value | Description |
|-------|-------|-------------|
| type | `NodePort` | External access via node port |
| port | 3000 | Service port |
| targetPort | 3000 | Container port |
| selector.app | `todo-frontend` | Pod selector |

**Access**: `minikube service todo-frontend -n todo-app`

---

## 5. Backend Service

**Resource**: `Service`
**Name**: `todo-backend`

| Field | Value | Description |
|-------|-------|-------------|
| type | `ClusterIP` | Internal access only |
| port | 8000 | Service port |
| targetPort | 8000 | Container port |
| selector.app | `todo-backend` | Pod selector |

**Internal DNS**: `todo-backend.todo-app.svc.cluster.local:8000`

---

## 6. ConfigMaps

### Frontend ConfigMap

**Resource**: `ConfigMap`
**Name**: `frontend-config`

| Key | Default Value | Description |
|-----|---------------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://todo-backend:8000` | Backend service URL |
| `NODE_ENV` | `production` | Runtime environment |

### Backend ConfigMap

**Resource**: `ConfigMap`
**Name**: `backend-config`

| Key | Default Value | Description |
|-----|---------------|-------------|
| `LOG_LEVEL` | `info` | Logging level |
| `CORS_ORIGINS` | `*` | CORS allowed origins |

---

## 7. Secrets

**Resource**: `Secret`
**Name**: `todo-secrets`
**Type**: `Opaque`

| Key | Required | Description |
|-----|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |
| `OPENAI_API_KEY` | Yes | OpenAI API key for chatbot |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret |

**Creation Command**:
```bash
kubectl create secret generic todo-secrets \
  --namespace=todo-app \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=OPENAI_API_KEY='sk-...' \
  --from-literal=BETTER_AUTH_SECRET='...'
```

---

## Resource Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                     Namespace: todo-app                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   ConfigMap  │         │   ConfigMap  │                  │
│  │frontend-config│         │backend-config│                  │
│  └──────┬───────┘         └──────┬───────┘                  │
│         │                        │                           │
│         ▼                        ▼                           │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │  Deployment  │         │  Deployment  │                  │
│  │todo-frontend │         │ todo-backend │                  │
│  │  (replicas)  │         │  (replicas)  │                  │
│  └──────┬───────┘         └──────┬───────┘                  │
│         │                        │                           │
│         │         ┌──────────────┤                          │
│         │         │              │                           │
│         │         ▼              │                           │
│         │  ┌──────────────┐      │                          │
│         │  │    Secret    │──────┘                          │
│         │  │ todo-secrets │                                  │
│         │  └──────────────┘                                  │
│         │                                                    │
│         ▼                        ▼                           │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   Service    │         │   Service    │                  │
│  │todo-frontend │         │ todo-backend │                  │
│  │  (NodePort)  │         │ (ClusterIP)  │                  │
│  └──────────────┘         └──────────────┘                  │
│         │                        ▲                           │
│         │                        │                           │
│         │        (internal)      │                           │
│         │        ────────────────┘                           │
└─────────┼───────────────────────────────────────────────────┘
          │
          │ (external via NodePort)
          ▼
    ┌──────────┐
    │  Browser │
    │  (User)  │
    └──────────┘
```

---

## Validation Rules

### Deployment Validation

- `replicas` must be >= 1
- `image` must be a valid image reference
- Resource `requests` must be <= `limits`
- Probe `initialDelaySeconds` must be > 0

### Service Validation

- `port` must be between 1-65535
- `targetPort` must match container port
- `selector` must match deployment labels

### Secret Validation

- All required keys must be present
- Values must be base64 encoded (when applied via YAML)
- `DATABASE_URL` must be valid PostgreSQL connection string

---

## State Transitions

### Pod Lifecycle

```
Pending → Running → Terminating → Deleted
    │         │
    │         ├── (liveness fails) → CrashLoopBackOff
    │         │
    │         └── (readiness fails) → Not Ready (traffic stopped)
    │
    └── (image pull fails) → ImagePullBackOff
```

### Deployment Rollout

```
Stable → Rolling Update → Stable
           │
           ├── (new pods ready) → Scale down old
           │
           └── (new pods fail) → Rollback available
```

---

**Data Model Status**: ✅ COMPLETE
