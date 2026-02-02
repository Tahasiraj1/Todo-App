# Research: Phase IV - Local Kubernetes Deployment

**Date**: 2026-01-27
**Feature**: 4-k8s-local-deployment
**Purpose**: Resolve technical decisions and best practices for Kubernetes deployment

---

## 1. Container Image Strategy

### Research Question
What is the optimal approach for building production-ready container images for Next.js and FastAPI applications?

### Findings

#### Frontend (Next.js)

**Decision**: Multi-stage build with `node:20-alpine` base

**Rationale**:
- Alpine variant is ~5x smaller than full Node image (~140MB vs ~700MB)
- Next.js 15 standalone output mode reduces final image size significantly
- Multi-stage separates build dependencies from runtime

**Best Practices**:
```dockerfile
# Build stage with full Node for compilation
FROM node:20-alpine AS builder
# ... build steps

# Runtime stage with minimal dependencies
FROM node:20-alpine AS runner
# Copy only production artifacts
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
```

**Alternatives Considered**:
- `node:20-slim`: Larger (~250MB), Debian-based
- `gcr.io/distroless/nodejs`: Smaller but harder to debug

#### Backend (FastAPI)

**Decision**: Use existing multi-stage Dockerfile with `python:3.13-slim`

**Rationale**:
- Already implemented and tested for Hugging Face deployment
- Slim variant balances size (~150MB) with compatibility
- Multi-stage separates build tools from runtime

**Required Changes**:
- Add health check endpoint for Kubernetes probes
- Parameterize port via environment variable
- Remove Hugging Face-specific defaults

---

## 2. Minikube Image Loading Strategy

### Research Question
How to efficiently make locally built images available to Minikube?

### Findings

**Decision**: Use `minikube image load` command

**Rationale**:
- Native Minikube functionality, no setup required
- Directly loads image into Minikube's container runtime
- Works with both Docker and containerd drivers

**Command**:
```bash
# Build locally
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# Load into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
```

**Alternatives Considered**:
- `minikube docker-env`: Requires building inside Minikube's Docker
- Local registry: Additional complexity, requires addon
- Docker Hub: Network overhead, requires authentication

---

## 3. Service Exposure Strategy

### Research Question
What is the simplest way to expose services for local development?

### Findings

**Decision**: NodePort service type + `minikube service` command

**Rationale**:
- Works immediately without additional configuration
- `minikube service <name>` opens browser automatically
- Mimics LoadBalancer behavior for local development

**Configuration**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
spec:
  type: NodePort
  selector:
    app: todo-frontend
  ports:
    - port: 3000
      targetPort: 3000
```

**Access**:
```bash
minikube service todo-frontend --url
# Returns: http://192.168.49.2:31234 (dynamic port)
```

**Alternatives Considered**:
- LoadBalancer: Requires MetalLB or cloud provider
- Ingress: More complex, better for production/Phase V
- ClusterIP + port-forward: Manual, less production-like

---

## 4. Health Check Strategy

### Research Question
What health check endpoints are needed for Kubernetes probes?

### Findings

**Decision**: HTTP health endpoints with standard paths

**Backend Health Endpoint** (exists, verify):
```
GET /health -> 200 OK {"status": "healthy"}
```

**Frontend Health Endpoint** (to verify/create):
```
GET /api/health -> 200 OK {"status": "ok"}
```

**Kubernetes Probes**:
```yaml
livenessProbe:
  httpGet:
    path: /health  # or /api/health for frontend
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 5
```

**Rationale**:
- Liveness: Restart container if application hangs
- Readiness: Don't send traffic until app is ready
- HTTP checks are standard and informative

---

## 5. Configuration Management Strategy

### Research Question
How to manage environment-specific configuration in Kubernetes?

### Findings

**Decision**: ConfigMaps for non-sensitive, Secrets for sensitive data

**Non-Sensitive (ConfigMap)**:
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NODE_ENV` - Runtime environment
- `LOG_LEVEL` - Logging verbosity

**Sensitive (Secret)**:
- `DATABASE_URL` - Neon PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key
- `BETTER_AUTH_SECRET` - JWT signing secret

**Implementation**:
```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-backend-config
data:
  LOG_LEVEL: "info"

# Secret (base64 encoded)
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
type: Opaque
data:
  DATABASE_URL: <base64-encoded>
  OPENAI_API_KEY: <base64-encoded>
```

**Best Practice**: Use `kubectl create secret` from .env file:
```bash
kubectl create secret generic todo-secrets \
  --from-env-file=backend/.env
```

---

## 6. Helm Chart Structure

### Research Question
What is the recommended Helm chart structure for a multi-service application?

### Findings

**Decision**: Single chart with templates per service

**Structure**:
```
helm/todo-chatbot/
├── Chart.yaml           # Chart metadata
├── values.yaml          # Default values
├── values-minikube.yaml # Minikube overrides
├── templates/
│   ├── _helpers.tpl     # Template helpers
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

**Values Structure**:
```yaml
global:
  namespace: todo-app

frontend:
  replicaCount: 1
  image:
    repository: todo-frontend
    tag: latest
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"

backend:
  replicaCount: 1
  image:
    repository: todo-backend
    tag: latest
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"

secrets:
  # Populated at install time
  databaseUrl: ""
  openaiApiKey: ""
  betterAuthSecret: ""
```

---

## 7. Resource Allocation

### Research Question
What resource requests/limits are appropriate for Minikube development?

### Findings

**Decision**: Conservative defaults suitable for 4GB Minikube

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|------------|-----------|----------------|--------------|
| Frontend  | 100m       | 500m      | 256Mi          | 512Mi        |
| Backend   | 100m       | 500m      | 256Mi          | 512Mi        |
| **Total** | 200m       | 1000m     | 512Mi          | 1024Mi       |

**Rationale**:
- Leaves headroom for Kubernetes system pods
- Prevents OOM kills during development
- Can scale up in production values file

**Minikube Start Command**:
```bash
minikube start --cpus=2 --memory=4096
```

---

## 8. Namespace Strategy

### Research Question
Should we use a dedicated namespace or the default namespace?

### Findings

**Decision**: Dedicated `todo-app` namespace

**Rationale**:
- Isolates resources from system and other applications
- Enables easy cleanup: `kubectl delete namespace todo-app`
- Best practice for production patterns
- Resource quotas can be applied per namespace

**Implementation**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
  labels:
    app.kubernetes.io/name: todo-chatbot
```

---

## Summary of Decisions

| Topic | Decision | Impact |
|-------|----------|--------|
| Frontend Base Image | `node:20-alpine` | Small image, fast startup |
| Backend Base Image | `python:3.13-slim` | Reuse existing, balanced size |
| Image Loading | `minikube image load` | No registry setup needed |
| Service Exposure | NodePort | Works out-of-box |
| Health Checks | HTTP probes on /health | Standard K8s practice |
| Configuration | ConfigMap + Secret | Secure, flexible |
| Helm Structure | Single chart | Simple deployment |
| Resources | 256Mi/512Mi per pod | Fits 4GB Minikube |
| Namespace | `todo-app` | Isolated, easy cleanup |

---

**Research Status**: ✅ COMPLETE - No NEEDS CLARIFICATION items remain
