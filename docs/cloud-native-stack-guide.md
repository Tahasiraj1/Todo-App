# The Cloud-Native Stack — A Practitioner's Guide

**Context**: This guide documents what was learned building Phase IV of the Todo App — taking a Next.js frontend and FastAPI backend from local development to a fully orchestrated Kubernetes deployment.

**Audience**: Developers who have heard the terms but want to understand what each layer actually does and why it exists.

---

## The Stack at a Glance

```
Layer 4:  Helm          ──→  Package & configure deployments
Layer 3:  Kubernetes    ──→  Orchestrate containers across machines
Layer 2:  Containers    ──→  Isolate and standardize applications
Layer 1:  Docker Images ──→  Package application + dependencies
Layer 0:  Your Code     ──→  The actual app
```

Each layer solves a specific problem. Remove any layer and something breaks — either portability, reliability, scalability, or operability.

---

## Layer 0: Your Code

This is your application. In our case:

- **Frontend**: Next.js (TypeScript, React)
- **Backend**: FastAPI (Python, Uvicorn)

Cloud-native doesn't change how you write application code. It changes how you **ship and run** it.

The only requirement cloud-native places on your code:

- Expose a **health endpoint** (`GET /health`) so the infrastructure can check if you're alive
- Read configuration from **environment variables**, not hardcoded values
- Log to **stdout/stderr**, not to files
- Be **stateless** — don't store session data in memory or on the local filesystem

These are the [12-factor app](https://12factor.net/) principles. They existed before Kubernetes. Kubernetes just made them mandatory.

---

## Layer 1: Docker Images

### What It Is

An image is a filesystem snapshot — your code, its dependencies, a base OS, and instructions for how to start the process. It's immutable. Once built, it never changes.

### What We Did

```dockerfile
# backend/Dockerfile (simplified)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build the image
docker build -t todo-backend:v4 ./backend

# The image now exists locally
docker images | grep todo-backend
# todo-backend   v4   abc123   834MB
```

### The Problem It Solves

"Works on my machine" — the most common phrase in software. Your laptop has Python 3.11, your colleague has 3.9, the server has 3.10. Different OS, different system libraries, different behavior.

An image freezes everything. The same image produces the same behavior on any machine that can run Docker.

### Cloud-Native Concept: Immutable Artifacts

You never patch a running server. You never SSH in and `pip install` something. You build a new image with the fix and replace the old one. This makes deployments predictable and rollbacks trivial — just switch back to the previous image tag.

### Key Commands

```bash
docker build -t <name>:<tag> <path>     # Build an image
docker images                            # List local images
docker run -p 8000:8000 <image>          # Run a container from an image
docker push <registry>/<name>:<tag>      # Push to a registry (Docker Hub, ECR)
```

---

## Layer 2: Containers

### What It Is

A container is a running instance of an image. It's an isolated process with its own filesystem (from the image), its own network interface, and enforced resource limits. It doesn't know what else is running on the same machine.

### How It Differs From an Image

| Image | Container |
|-------|-----------|
| A blueprint | A running process |
| Stored on disk | Running in memory |
| Immutable | Has runtime state |
| One image → many containers | Each container is independent |

Think of it like: image = recipe, container = the cooked meal. You can cook the same recipe multiple times and get identical meals.

### The Problem It Solves

Without containers, two applications on the same server can conflict — different Python versions, port collisions, shared filesystem corruption. Containers isolate each application completely.

### Cloud-Native Concept: Process Isolation

Each service runs in its own container. The frontend can't accidentally corrupt the backend's files, steal its memory, or crash it. If the backend container dies, the frontend container keeps running.

### What Containers Are NOT

Containers are not virtual machines. A VM emulates an entire computer with its own kernel. A container shares the host's kernel but isolates the userspace (filesystem, processes, network). This makes containers much lighter — they start in seconds, not minutes.

```
Virtual Machine              Container
┌──────────────┐            ┌──────────────┐
│  Application │            │  Application │
│  Libraries   │            │  Libraries   │
│  Guest OS    │            │              │
│  Hypervisor  │            │  (shares     │
│  Host OS     │            │   host       │
│  Hardware    │            │   kernel)    │
└──────────────┘            └──────────────┘
~200MB+ overhead            ~10MB overhead
Minutes to start            Seconds to start
```

---

## Layer 3: Kubernetes

This is the largest layer. Kubernetes (K8s) is a container orchestrator — it decides where containers run, keeps them running, and connects them to each other.

### Why Not Just Run Docker?

`docker run` works for one container on one machine. When you need:
- Multiple replicas for reliability
- Automatic restarts on failure
- Service discovery between containers
- Rolling updates with zero downtime
- Resource management across machines

...you need an orchestrator. That's Kubernetes.

### Core Concepts (What We Used)

#### Pods

The smallest deployable unit. A pod wraps one or more containers that share network and storage.

```yaml
# What Kubernetes creates from a Deployment
Pod: todo-backend-57b578f5b9-l26df
  Container: todo-backend (image: todo-backend:v4)
  IP: 10.244.0.15 (internal, ephemeral)
  Status: Running
```

In practice, one pod = one container. Multi-container pods are for sidecars (logging agents, service mesh proxies) — an advanced pattern.

**Key point**: Pods are **ephemeral**. They can be killed, restarted, or moved to a different node at any time. Never store important data inside a pod.

#### Deployments

A declaration of desired state. You say what you want; Kubernetes makes it happen.

```yaml
# k8s/base/backend/deployment.yaml (simplified)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  replicas: 1                    # "I want 1 instance running"
  selector:
    matchLabels:
      app: todo-backend
  template:
    spec:
      containers:
        - name: todo-backend
          image: todo-backend:v4
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: DATABASE_URL
```

**Cloud-native concept: Declarative infrastructure.** You don't write scripts that say "start the server, then check if it's running, then restart if it crashed." You describe the desired end state. Kubernetes continuously reconciles reality with your declaration.

```
You declare:        "1 replica of todo-backend running image v4"
Kubernetes does:    Creates pod → monitors it → restarts if it dies
                    → replaces if the node goes down
```

#### Services

Pods get random IPs that change on every restart. A Service provides a stable network address.

```yaml
# k8s/base/backend/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
spec:
  selector:
    app: todo-backend          # "Route traffic to pods with this label"
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP              # Only accessible inside the cluster
```

**Service types we used:**

| Type | Accessible From | Use Case |
|------|----------------|----------|
| `ClusterIP` | Inside cluster only | Backend service (frontend talks to it internally) |
| `NodePort` | Cluster node IP + a port | Development access from your machine |
| `LoadBalancer` | Public internet | Production (requires cloud provider or ingress) |

**Cloud-native concept: Service discovery.** The frontend doesn't need to know the backend's IP. It calls `http://todo-backend:8000` and Kubernetes DNS resolves it. If the backend pod restarts with a new IP, the service updates automatically.

```
Frontend Pod                     Service                      Backend Pod
     │                             │                              │
     ├── GET todo-backend:8000 ──→ │ ── routes to 10.244.0.15 ──→│
     │                             │    (current pod IP)          │
     │   (pod dies, new one: .16)  │                              │
     │                             │                              │
     ├── GET todo-backend:8000 ──→ │ ── routes to 10.244.0.16 ──→│ (new pod)
     │                             │    (auto-updated)            │
```

#### ConfigMaps

Non-sensitive configuration injected as environment variables.

```yaml
# k8s/base/backend/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  LOG_LEVEL: "info"
  CORS_ORIGINS: "*"
  PORT: "8000"
```

#### Secrets

Sensitive configuration (API keys, database URLs, auth secrets). Base64-encoded in YAML, injected as environment variables at runtime.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  DATABASE_URL: <base64-encoded>
  GEMINI_API_KEY: <base64-encoded>
  BETTER_AUTH_SECRET: <base64-encoded>
```

**Cloud-native concept: Externalized configuration (12-factor principle #3).** The same image runs in development, staging, and production. What changes is the config injected into it. The code never contains environment-specific values.

#### Namespaces

Virtual partitions of a cluster. Resources in different namespaces are isolated.

```bash
kubectl get namespaces
# default       Active   (built-in)
# kube-system   Active   (K8s internals)
# todo-app      Active   (our app)
# kagent        Active   (AI tools)
```

**Cloud-native concept: Multi-tenancy.** One cluster can host staging and production in separate namespaces with different resource quotas and access controls.

#### Health Probes

Kubernetes checks if your app is healthy. Two types:

```yaml
livenessProbe:               # "Is the process alive?"
  httpGet:                   # If this fails → restart the pod
    path: /health
    port: 8000
  initialDelaySeconds: 30    # Wait 30s before first check
  periodSeconds: 10          # Check every 10s

readinessProbe:              # "Can it accept traffic?"
  httpGet:                   # If this fails → stop sending traffic
    path: /health            # (but don't restart)
    port: 8000
  initialDelaySeconds: 5
```

**Cloud-native concept: Self-healing.** The system detects failures and recovers without human intervention. We tested this by running `kubectl delete pod todo-backend-xxx` — Kubernetes immediately created a replacement.

### Key Commands

```bash
kubectl get pods -n todo-app           # List pods in namespace
kubectl get services -n todo-app       # List services
kubectl describe pod <name>            # Detailed pod info + events
kubectl logs <pod-name>                # Application logs
kubectl delete pod <name>              # Kill a pod (deployment recreates it)
kubectl apply -f <file.yaml>           # Apply a manifest
kubectl get events -n todo-app         # Cluster events (debugging)
```

---

## Layer 4: Helm

### What It Is

A package manager for Kubernetes. It templates YAML manifests and manages deployments as versioned releases.

### The Problem It Solves

Without Helm, deploying our app requires applying 8+ YAML files in the right order:

```bash
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
kubectl apply -f backend-configmap.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f frontend-configmap.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
```

With Helm:

```bash
helm install todo-chatbot ./k8s/helm/todo-chatbot -f values-minikube.yaml
```

One command. All resources. Correct order. Configurable.

### How It Works

A Helm chart has three parts:

```
k8s/helm/todo-chatbot/
├── Chart.yaml              # Chart metadata (name, version)
├── values.yaml             # Default configuration values
├── values-minikube.yaml    # Override values for local dev
└── templates/              # Parameterized Kubernetes YAML
    ├── _helpers.tpl        # Reusable template functions
    ├── namespace.yaml
    ├── secrets.yaml
    ├── backend-configmap.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-configmap.yaml
    ├── frontend-deployment.yaml
    └── frontend-service.yaml
```

Templates use Go templating to inject values:

```yaml
# templates/backend-deployment.yaml
spec:
  replicas: {{ .Values.backend.replicaCount }}
  template:
    spec:
      containers:
        - name: backend
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
```

```yaml
# values.yaml
backend:
  replicaCount: 1
  image:
    repository: todo-backend
    tag: "v4"
```

### Same Chart, Different Environments

```bash
# Local development
helm install todo ./chart -f values-minikube.yaml

# Staging
helm install todo ./chart -f values-staging.yaml

# Production
helm install todo ./chart -f values-production.yaml
```

The chart doesn't change. The values file swaps in the right images, replicas, domains, and secrets per environment.

### Cloud-Native Concept: Repeatable Deployments

Helm provides:

| Feature | What it means |
|---------|--------------|
| **Versioned releases** | `helm history` shows every deployment with revision numbers |
| **Atomic installs** | If any resource fails, the entire install is rolled back |
| **Upgrades** | `helm upgrade` applies changes incrementally |
| **Rollbacks** | `helm rollback todo-chatbot 1` reverts to a previous version |
| **Uninstall** | `helm uninstall` removes all resources cleanly |

### Key Commands

```bash
helm install <name> <chart> -f <values>   # Deploy
helm upgrade <name> <chart> -f <values>   # Update
helm rollback <name> <revision>           # Rollback
helm uninstall <name>                     # Remove everything
helm list                                 # Show releases
helm history <name>                       # Show revision history
```

---

## How the Layers Connect

A request from a user to your app traverses every layer:

```
User's Browser
     │
     ▼
[Service: todo-frontend]     ← Layer 3: Kubernetes routes traffic
     │
     ▼
[Pod: todo-frontend-xxx]     ← Layer 2: Container running the process
     │
     ▼
[Image: todo-frontend:v4]    ← Layer 1: Immutable artifact with the app
     │
     ▼
[Next.js app code]           ← Layer 0: Your application
     │
     │  (API call to backend)
     ▼
[Service: todo-backend]      ← Layer 3: Service discovery by name
     │
     ▼
[Pod: todo-backend-xxx]      ← Layer 3: Kubernetes picks a healthy pod
     │
     ▼
[Image: todo-backend:v4]     ← Layer 1: Same image everywhere
     │
     ▼
[FastAPI app code]           ← Layer 0: Business logic
```

Helm (Layer 4) isn't in the runtime path. It's the tool that **set up** all of the above.

---

## The Mental Model Shift

| Traditional Deployment | Cloud-Native Deployment |
|----------------------|----------------------|
| SSH into a server | Never touch the server directly |
| `apt install`, `npm start` | Docker image has everything baked in |
| Edit config files on the server | ConfigMaps + Secrets, injected at deploy time |
| Restart manually when things crash | Kubernetes restarts automatically |
| One server, one app | Pods can run on any node in the cluster |
| Scale by buying a bigger server | Scale by adding more replicas |
| "Works on my machine" | Image is identical everywhere |
| Deploy by copying files | `helm install` / `helm upgrade` |
| Monitor by SSHing and reading logs | `kubectl logs`, centralized observability |
| Rollback by reverting files and praying | `helm rollback` to a known-good revision |

---

## What This Stack Does NOT Cover (Yet)

These are the natural next layers in a cloud-native journey:

| Layer | What It Is | When You Need It |
|-------|-----------|-----------------|
| **Container Registry** | Central image store (Docker Hub, ECR, GCR) | Deploying to any cluster beyond local Minikube |
| **Ingress Controller** | Route external HTTP traffic by domain/path | Exposing the app publicly with a domain name |
| **TLS / cert-manager** | Automatic HTTPS certificates via Let's Encrypt | Adding a real domain |
| **CI/CD Pipeline** | Automate: `git push` → build → test → deploy | Automating deployments (GitHub Actions, ArgoCD) |
| **Horizontal Pod Autoscaler** | Scale replicas based on CPU/memory/custom metrics | Handling variable traffic loads |
| **Persistent Volumes** | Durable storage that survives pod restarts | Real databases (PostgreSQL, not SQLite) |
| **Network Policies** | Firewall rules between pods | Security hardening |
| **Observability Stack** | Prometheus + Grafana (metrics), Loki (logs), Jaeger (traces) | Operating in production |
| **Service Mesh** (Istio/Linkerd) | mTLS between services, advanced traffic management | At scale with many microservices |
| **GitOps** (ArgoCD/Flux) | Git repo is the source of truth for cluster state | Mature team workflows |

---

## Quick Reference

### Build and Deploy (Local)

```bash
# Build images
docker build -t todo-frontend:v4 ./frontend
docker build -t todo-backend:v4 ./backend

# Load into Minikube
minikube image load todo-frontend:v4
minikube image load todo-backend:v4

# Deploy with Helm
helm install todo-chatbot ./k8s/helm/todo-chatbot \
  --namespace todo-app \
  --create-namespace \
  -f k8s/helm/todo-chatbot/values-minikube.yaml

# Verify
kubectl get pods -n todo-app
```

### Day-to-Day Operations

```bash
# Check status
kubectl get pods -n todo-app
helm list

# View logs
kubectl logs -n todo-app -l app=todo-backend

# Update after code change
docker build -t todo-backend:v5 ./backend
minikube image load todo-backend:v5
helm upgrade todo-chatbot ./k8s/helm/todo-chatbot --set backend.image.tag=v5

# Rollback if something breaks
helm rollback todo-chatbot 1

# Tear down
helm uninstall todo-chatbot -n todo-app
```

---

## Summary

Cloud-native is not a single technology. It's a stack of layers, each solving a distinct problem:

- **Docker images** solve "works on my machine" → immutable, portable artifacts
- **Containers** solve "apps interfering with each other" → process isolation
- **Kubernetes** solves "keeping containers running reliably" → orchestration, self-healing, service discovery
- **Helm** solves "deploying consistently across environments" → packaging, versioning, configuration

Each layer builds on the one below it. Together they give you: portability, reliability, scalability, and operability — the four pillars of cloud-native infrastructure.
