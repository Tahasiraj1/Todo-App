# Phase 4: Kubernetes Deployment - Complete Beginner's Guide

> **Goal**: Take our Todo Chatbot app (which runs on your computer) and make it run inside Kubernetes (a container orchestration system).

---

## Table of Contents

1. [The Big Picture - What Are We Doing?](#1-the-big-picture---what-are-we-doing)
2. [Key Concepts Explained](#2-key-concepts-explained)
3. [Tools We Installed](#3-tools-we-installed)
4. [What We Did Step-by-Step](#4-what-we-did-step-by-step)
5. [All Commands Explained](#5-all-commands-explained)
6. [Files We Created](#6-files-we-created)
7. [Problems We Encountered & How We Fixed Them](#7-problems-we-encountered--how-we-fixed-them)
8. [What's Remaining & Why](#8-whats-remaining--why)
9. [Quick Reference](#9-quick-reference)

---

## 1. The Big Picture - What Are We Doing?

### Before Phase 4 (How the app ran before)
```
Your Computer
├── Frontend (Next.js) → runs with: npm run dev → accessible at localhost:3000
├── Backend (FastAPI)  → runs with: uvicorn src.main:app → accessible at localhost:8000
└── Database (Neon)    → runs in the cloud (Neon PostgreSQL)
```

You had to:
1. Open a terminal, run `npm run dev` for frontend
2. Open another terminal, run `uvicorn` for backend
3. Keep both terminals open
4. If your computer restarts, you start over

### After Phase 4 (How the app runs now)
```
Minikube (Mini Kubernetes Cluster on your computer)
├── Pod: todo-frontend (container running Next.js)
│   └── Automatically restarts if it crashes
│   └── Has health checks to ensure it's working
├── Pod: todo-backend (container running FastAPI)
│   └── Automatically restarts if it crashes
│   └── Has health checks to ensure it's working
└── Services (networking that connects everything)
```

Benefits:
- **One command** deploys everything
- **Auto-restart** if something crashes
- **Health monitoring** built-in
- **Same setup** works on any cloud (AWS, Google Cloud, Azure)
- **Scalable** - can run multiple copies easily

---

## 2. Key Concepts Explained

### 2.1 Docker - The Box Maker

**What is it?**
Docker is like a shipping container for software. Just like shipping containers can hold anything and be transported anywhere, Docker containers hold your application and can run anywhere.

**Analogy**: Imagine you're moving houses. Instead of carrying items one by one (installing dependencies manually), you pack everything into boxes (containers). The boxes work the same whether you're in New York or Tokyo.

**Key terms:**
- **Image**: A blueprint/recipe for creating a container (like a frozen pizza - ready to cook)
- **Container**: A running instance of an image (like a cooked pizza - ready to eat)
- **Dockerfile**: Instructions for creating an image (like the recipe on the pizza box)

```
Dockerfile (recipe) → docker build → Image (frozen pizza) → docker run → Container (cooked pizza)
```

### 2.2 Kubernetes (K8s) - The Orchestra Conductor

**What is it?**
Kubernetes is a system that manages containers. It decides:
- Where containers run
- How many copies to run
- What to do if a container crashes
- How containers talk to each other

**Analogy**: Imagine a restaurant kitchen. Docker makes the ingredients (containers). Kubernetes is the head chef who:
- Decides which cook prepares what dish
- Makes sure enough dishes are ready for customers
- Replaces a cook if they get sick
- Routes orders to the right station

**Key terms:**
- **Cluster**: A group of computers running Kubernetes (our "kitchen")
- **Node**: One computer in the cluster (one "cooking station")
- **Pod**: The smallest unit - usually one container (one "dish being prepared")
- **Deployment**: Instructions for running pods (the "recipe card" for the kitchen)
- **Service**: Networking rules for accessing pods (the "serving window")
- **Namespace**: A way to organize resources (like different sections of the kitchen)

### 2.3 Minikube - Kubernetes on Your Laptop

**What is it?**
Minikube creates a mini Kubernetes cluster on your computer for learning and development.

**Analogy**: Instead of renting a full commercial kitchen (cloud Kubernetes), Minikube is like a small test kitchen in your home where you can practice.

### 2.4 kubectl - The Remote Control

**What is it?**
kubectl (pronounced "cube-control" or "cube-cuddle") is the command-line tool to talk to Kubernetes.

**Analogy**: If Kubernetes is a TV, kubectl is the remote control. You use it to:
- See what's playing (`kubectl get pods`)
- Change channels (`kubectl apply`)
- Adjust settings (`kubectl edit`)

### 2.5 Helm - The Package Manager

**What is it?**
Helm is like npm/pip but for Kubernetes. Instead of installing one thing at a time, you install a "chart" that includes everything.

**Analogy**:
- Without Helm: You buy flour, eggs, sugar, butter separately to make a cake
- With Helm: You buy a cake mix that has everything pre-measured

### 2.6 Container Registry vs Local Images

**What is it?**
A container registry is like a library for Docker images. Docker Hub is a public one.

**Our situation**: We're using local images (not uploaded to any registry). That's why we need to "load" them into Minikube specially.

---

## 3. Tools We Installed

### 3.1 Docker Desktop
```
Purpose: Build and run containers
Installation: Downloaded from docker.com
Verification: docker --version
```

Docker Desktop includes:
- Docker Engine (the container runtime)
- Docker CLI (command-line tool)
- Docker Compose (for multi-container apps)

### 3.2 Minikube
```
Purpose: Run a local Kubernetes cluster
Installation: Downloaded minikube binary
Verification: minikube version
```

### 3.3 kubectl
```
Purpose: Control Kubernetes
Installation: Comes with Docker Desktop or separate install
Verification: kubectl version --client
```

### 3.4 Helm
```
Purpose: Package and deploy Kubernetes apps
Installation: Downloaded helm binary
Verification: helm version
```

---

## 4. What We Did Step-by-Step

### Phase 1: Setup (Creating the folder structure)

```
k8s/
├── base/                    # Raw Kubernetes manifests
│   ├── namespace.yaml       # Creates "todo-app" namespace
│   ├── secrets/             # Secret templates
│   ├── frontend/            # Frontend K8s resources
│   │   ├── configmap.yaml   # Frontend configuration
│   │   ├── deployment.yaml  # Frontend pod definition
│   │   └── service.yaml     # Frontend networking
│   └── backend/             # Backend K8s resources
│       ├── configmap.yaml   # Backend configuration
│       ├── deployment.yaml  # Backend pod definition
│       └── service.yaml     # Backend networking
└── helm/                    # Helm chart
    └── todo-chatbot/        # Our Helm chart
        ├── Chart.yaml       # Chart metadata
        ├── values.yaml      # Default configuration
        ├── values-minikube.yaml  # Minikube-specific config
        └── templates/       # Kubernetes templates
```

### Phase 2: Creating Dockerfiles

#### Frontend Dockerfile (frontend/Dockerfile)

We created a **multi-stage build**. Think of it like cooking in stages:

```dockerfile
# Stage 1: DEPS - Install all ingredients
FROM node:20-alpine AS deps
# Start with a Node.js base image (like starting with a basic kitchen)
# "alpine" means it's a tiny version (smaller = faster)

WORKDIR /app
# Create and move into /app directory (like clearing a workspace)

COPY package.json package-lock.json* ./
# Copy the shopping list (package.json lists what to install)

RUN npm ci --only=production=false
# Install ALL dependencies (including dev ones for building)
# "ci" = clean install, more reliable than "npm install"


# Stage 2: BUILDER - Cook the meal
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
# Grab the ingredients from Stage 1

COPY . .
# Copy all source code

ARG NEXT_PUBLIC_API_URL=http://todo-backend:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
# Set environment variable for API URL
# In Kubernetes, "todo-backend" is the backend service name

RUN npm run build
# Build the production version of Next.js


# Stage 3: RUNNER - Serve the meal
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
# Tell Node.js this is production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
# Create a non-root user (security best practice)

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
# Copy ONLY what's needed to run (not source code, not node_modules)
# This makes the final image much smaller

USER nextjs
# Run as non-root user

EXPOSE 3000
# Document that this container uses port 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1
# Every 30 seconds, check if the app is healthy
# If it fails 3 times, Kubernetes will restart the container

CMD ["node", "server.js"]
# The command to start the app
```

**Why multi-stage?**
- Stage 1 image: ~500MB (has all dev tools)
- Stage 2 image: ~800MB (has build artifacts)
- Stage 3 image: ~298MB (has only runtime needs)

We throw away stages 1 and 2, keeping only the slim stage 3!

#### Backend Dockerfile (backend/Dockerfile)

```dockerfile
# Stage 1: BUILDER
FROM python:3.13-slim AS builder
# Start with Python 3.13 slim image

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh
# Install:
# - gcc: Compiler needed for some Python packages
# - curl: To download UV
# - UV: Fast Python package manager (what you use instead of pip)

ENV PATH="/root/.local/bin:$PATH"
# Add UV to the PATH so we can use it

COPY pyproject.toml uv.lock* ./
# Copy dependency files
# uv.lock ensures exact same versions every time

RUN uv sync --frozen --no-dev
# Install dependencies into a virtual environment
# --frozen: Use exact versions from uv.lock
# --no-dev: Skip development dependencies


# Stage 2: RUNNER
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
# Install PostgreSQL client (for database connections)

COPY --from=builder /app/.venv /app/.venv
# Copy the virtual environment from builder stage

COPY src/ ./src/
COPY pyproject.toml .
# Copy source code

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
# Set up environment to use the virtual environment

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD /app/.venv/bin/python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/health')" || exit 1
# Health check using Python's built-in urllib

CMD ["sh", "-c", "/app/.venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
# Start uvicorn server
# --host 0.0.0.0: Listen on all network interfaces (required in containers)
# --port ${PORT:-8000}: Use PORT env var, default to 8000
```

### Phase 3: Building Docker Images

```bash
# Build frontend image
docker build -t todo-frontend:latest ./frontend

# -t todo-frontend:latest = Tag the image as "todo-frontend" with version "latest"
# ./frontend = Build context (where the Dockerfile is)
```

```bash
# Build backend image
docker build -t todo-backend:latest ./backend
```

**What happens during build:**
1. Docker reads the Dockerfile
2. Executes each instruction (FROM, RUN, COPY, etc.)
3. Creates layers (each instruction = one layer)
4. Caches layers (if nothing changed, reuse the layer)
5. Produces a final image

### Phase 4: Starting Minikube

```bash
minikube start --cpus=2 --memory=3072

# --cpus=2: Give Minikube 2 CPU cores
# --memory=3072: Give Minikube 3GB RAM (originally wanted 4GB but system limit)
```

**What this does:**
1. Creates a virtual machine (or uses Docker)
2. Installs Kubernetes inside it
3. Configures kubectl to talk to this cluster

### Phase 5: Loading Images into Minikube

```bash
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
```

**Why is this needed?**
- Minikube runs in its own environment (like a separate computer)
- It can't see Docker images on your computer
- We must "load" (copy) images into Minikube

**Alternative approaches:**
1. Push to Docker Hub, pull from Minikube (requires internet)
2. Use `minikube docker-env` to build directly in Minikube
3. Use `minikube image load` (what we did - simplest)

### Phase 6: Creating Kubernetes Resources

#### Namespace (k8s/base/namespace.yaml)
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
```

**What is a namespace?**
Like folders on your computer. Keeps resources organized and isolated.

```bash
kubectl apply -f k8s/base/namespace.yaml
# Creates the "todo-app" namespace
```

#### Secrets
```bash
kubectl create secret generic todo-secrets \
  --namespace=todo-app \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=OPENAI_API_KEY='sk-...' \
  --from-literal=BETTER_AUTH_SECRET='...'

# generic: Type of secret (there are also tls, docker-registry types)
# --namespace: Which namespace to create in
# --from-literal: Create key=value pairs
```

**What are secrets?**
Sensitive data (passwords, API keys) stored securely in Kubernetes. Never put these in your code or ConfigMaps!

#### ConfigMap (k8s/base/backend/configmap.yaml)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
  namespace: todo-app
data:
  PORT: "8000"
  LOG_LEVEL: "info"
  CORS_ORIGINS: "http://todo-frontend:3000"
```

**What is a ConfigMap?**
Non-sensitive configuration. Like environment variables but managed by Kubernetes.

#### Deployment (k8s/base/backend/deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  namespace: todo-app
spec:
  replicas: 1                    # How many copies to run
  selector:
    matchLabels:
      app: todo-backend          # How to find pods belonging to this deployment
  template:                      # Pod template
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
        - name: backend
          image: todo-backend:latest    # Which image to use
          imagePullPolicy: IfNotPresent # Don't try to download, use local
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: backend-config    # Load config from ConfigMap
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: todo-secrets
                  key: DATABASE_URL     # Load from Secret
          resources:
            requests:
              memory: "256Mi"           # Minimum memory needed
              cpu: "100m"               # Minimum CPU (100 millicores = 0.1 CPU)
            limits:
              memory: "512Mi"           # Maximum memory allowed
              cpu: "500m"               # Maximum CPU allowed
          livenessProbe:                # Is the container alive?
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15     # Wait 15s before first check
            periodSeconds: 10           # Check every 10s
          readinessProbe:               # Is the container ready for traffic?
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
```

**Deployment vs Pod:**
- Pod: One running container instance
- Deployment: Manages pods - creates, updates, restarts them

#### Service (k8s/base/backend/service.yaml)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
  namespace: todo-app
spec:
  type: ClusterIP              # Internal-only access
  selector:
    app: todo-backend          # Route traffic to pods with this label
  ports:
    - port: 8000               # Service port
      targetPort: 8000         # Container port
```

**Service Types:**
- **ClusterIP**: Internal only (other pods can reach it)
- **NodePort**: External access via node IP + port
- **LoadBalancer**: External access via cloud load balancer

We use:
- Backend: ClusterIP (only frontend needs to reach it)
- Frontend: NodePort (users need to reach it)

### Phase 7: Applying Everything

```bash
kubectl apply -f k8s/base/ -R

# -f k8s/base/: Apply files from this directory
# -R: Recursive (include subdirectories)
```

### Phase 8: Verifying

```bash
kubectl get pods -n todo-app
# List all pods in todo-app namespace

kubectl get svc -n todo-app
# List all services

kubectl logs deployment/todo-backend -n todo-app
# View logs from backend

minikube service todo-frontend -n todo-app --url
# Get URL to access frontend
```

---

## 5. All Commands Explained

### Docker Commands

| Command | What it does |
|---------|--------------|
| `docker build -t name:tag ./path` | Build an image from Dockerfile |
| `docker images` | List all images |
| `docker run -p 3000:3000 image` | Run a container, map port 3000 |
| `docker ps` | List running containers |
| `docker logs container-id` | View container logs |
| `docker exec -it container-id sh` | Open shell inside container |

### Minikube Commands

| Command | What it does |
|---------|--------------|
| `minikube start` | Start the cluster |
| `minikube stop` | Stop the cluster |
| `minikube delete` | Delete the cluster entirely |
| `minikube status` | Check cluster status |
| `minikube image load image:tag` | Load local image into Minikube |
| `minikube service svc-name -n namespace` | Open service in browser |
| `minikube dashboard` | Open Kubernetes dashboard GUI |

### kubectl Commands

| Command | What it does |
|---------|--------------|
| `kubectl get pods -n namespace` | List pods |
| `kubectl get svc -n namespace` | List services |
| `kubectl get all -n namespace` | List everything |
| `kubectl apply -f file.yaml` | Create/update resources |
| `kubectl delete -f file.yaml` | Delete resources |
| `kubectl logs pod-name -n namespace` | View pod logs |
| `kubectl describe pod pod-name -n namespace` | Detailed pod info |
| `kubectl exec -it pod-name -n namespace -- sh` | Shell into pod |
| `kubectl port-forward svc/name 3000:3000 -n namespace` | Forward port to local |
| `kubectl rollout restart deployment/name -n namespace` | Restart deployment |
| `kubectl set image deployment/name container=image:tag -n namespace` | Update image |

### Helm Commands

| Command | What it does |
|---------|--------------|
| `helm install release-name ./chart` | Install a chart |
| `helm upgrade release-name ./chart` | Upgrade a release |
| `helm uninstall release-name` | Remove a release |
| `helm list` | List installed releases |
| `helm template ./chart` | Render templates locally |
| `helm lint ./chart` | Check chart for issues |

---

## 6. Files We Created

### Kubernetes Base Manifests

```
k8s/base/
├── namespace.yaml              # Namespace definition
├── secrets/
│   └── app-secrets.yaml.example  # Template for secrets
├── frontend/
│   ├── configmap.yaml          # Frontend env vars
│   ├── deployment.yaml         # Frontend pod spec
│   └── service.yaml            # Frontend networking (NodePort)
└── backend/
    ├── configmap.yaml          # Backend env vars
    ├── deployment.yaml         # Backend pod spec
    └── service.yaml            # Backend networking (ClusterIP)
```

### Helm Chart

```
k8s/helm/todo-chatbot/
├── Chart.yaml                  # Chart metadata (name, version)
├── values.yaml                 # Default values
├── values-minikube.yaml        # Minikube-specific overrides
├── .helmignore                 # Files to ignore when packaging
├── README.md                   # Chart documentation
└── templates/
    ├── _helpers.tpl            # Template helper functions
    ├── namespace.yaml          # Namespace template
    ├── secrets.yaml            # Secrets template
    ├── frontend-configmap.yaml
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── backend-configmap.yaml
    ├── backend-deployment.yaml
    └── backend-service.yaml
```

### Docker Files

```
frontend/
├── Dockerfile                  # Multi-stage build for Next.js
├── .dockerignore              # Files to exclude from build
└── src/app/api/health/route.ts # Health check endpoint

backend/
├── Dockerfile                  # Multi-stage build for FastAPI
└── .dockerignore              # Files to exclude from build
```

---

## 7. Problems We Encountered & How We Fixed Them

### Problem 1: uv.lock in .dockerignore

**Error:**
```
error: Unable to find lockfile at `uv.lock`, but `--frozen` was provided.
```

**Cause:** The `uv.lock` file was listed in `backend/.dockerignore`, so Docker couldn't copy it.

**Fix:** Removed `uv.lock` from `.dockerignore`.

### Problem 2: Python not using virtual environment

**Error:**
```
ModuleNotFoundError: No module named 'agents'
```

**Cause:** Even though packages were installed in `.venv`, Python was looking in the wrong place.

**Fix:** Updated Dockerfile to explicitly use venv Python:
```dockerfile
CMD ["sh", "-c", "/app/.venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### Problem 3: Minikube using cached old image

**Symptom:** After rebuilding, pod still crashed with same error.

**Cause:** `minikube image load` with same tag (`latest`) doesn't always replace the image.

**Fix:** Tagged image with new version and updated deployment:
```bash
docker tag todo-backend:latest todo-backend:v2
minikube image load todo-backend:v2
kubectl set image deployment/todo-backend backend=todo-backend:v2 -n todo-app
```

### Problem 4: Minikube memory limit

**Error:**
```
Requested memory allocation 4096MB is more than available memory
```

**Fix:** Reduced memory to 3072MB:
```bash
minikube start --cpus=2 --memory=3072
```

---

## 8. What's Remaining & Why

### Completed (User Stories 1 & 2)

| Task | Description | Status |
|------|-------------|--------|
| US1 | Containerize applications | Done |
| US2 | Deploy to Minikube with raw manifests | Done |

### Remaining Tasks

#### T039: Test Chatbot Functionality
**What:** Manually test the app works (login, create todos, chat with AI)
**Why:** We deployed it, but haven't verified all features work
**How:** Open the frontend URL and test each feature

#### Phase 5: User Story 3 - Helm Charts (T055-T062)

**What is Helm again?**
Think of it like this:
- Raw manifests = Cooking from scratch with individual ingredients
- Helm = Using a meal kit with pre-measured ingredients and recipe

**Why Helm?**
1. **One command deployment**: `helm install` vs multiple `kubectl apply`
2. **Easy configuration**: Change values in one file
3. **Upgrades/Rollbacks**: `helm upgrade` / `helm rollback`
4. **Packaging**: Share your app as a single chart

**Tasks:**
| Task | What | Why |
|------|------|-----|
| T055 | Clean up raw manifest deployment | Remove current deployment before Helm install |
| T056 | Install with Helm | Deploy using Helm chart |
| T057 | Verify resources | Confirm everything created |
| T058 | Test helm upgrade | Change replicas to 2 |
| T059 | Verify upgrade | Confirm 2 pods running |
| T060 | Test helm uninstall | Remove everything |
| T061 | Verify clean removal | Confirm nothing left |
| T062 | Create README | Document Helm chart usage |

**Commands we'll use:**
```bash
# Clean up raw manifests
kubectl delete -f k8s/base/ -R

# Install with Helm
helm install todo-chatbot ./k8s/helm/todo-chatbot \
  -f ./k8s/helm/todo-chatbot/values-minikube.yaml \
  --set secrets.databaseUrl="..." \
  --set secrets.openaiApiKey="..." \
  --set secrets.betterAuthSecret="..."

# Or use existing secrets
helm install todo-chatbot ./k8s/helm/todo-chatbot \
  --set secrets.create=false \
  --set secrets.existingSecret=todo-secrets

# Test upgrade (scale to 2 replicas)
helm upgrade todo-chatbot ./k8s/helm/todo-chatbot \
  --set frontend.replicaCount=2

# Uninstall
helm uninstall todo-chatbot -n todo-app
```

#### Phase 6: User Story 4 - AI-Assisted Operations (T063-T068) - OPTIONAL

**What:** Document tools that use AI to help with Kubernetes

**Tools:**
- **kubectl-ai**: Natural language to kubectl commands
- **Docker AI (Gordon)**: AI assistant for Docker
- **kagent**: AI agent for Kubernetes operations

**Example:**
```bash
# Instead of remembering exact command:
kubectl-ai "show me all pods that are crashing"

# AI generates:
kubectl get pods --field-selector=status.phase=Failed
```

**Why optional?** These are nice-to-have productivity tools, not essential for deployment.

#### Phase 7: Polish (T069-T080)

**What:** Documentation and validation

| Task | What |
|------|------|
| T069 | Update main README with Phase IV instructions |
| T070 | Create kubernetes-deployment.md guide |
| T071 | Create troubleshooting.md |
| T072 | Validate quickstart works end-to-end |
| T073-T079 | Verify success criteria (build time, image size, etc.) |
| T080 | Final cleanup and review |

---

## 9. Quick Reference

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         MINIKUBE CLUSTER                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    NAMESPACE: todo-app                     │  │
│  │                                                            │  │
│  │  ┌─────────────────┐         ┌─────────────────┐          │  │
│  │  │   Pod: Frontend │         │   Pod: Backend  │          │  │
│  │  │   ┌───────────┐ │         │   ┌───────────┐ │          │  │
│  │  │   │  Next.js  │ │         │   │  FastAPI  │ │          │  │
│  │  │   │  :3000    │ │         │   │  :8000    │ │          │  │
│  │  │   └───────────┘ │         │   └───────────┘ │          │  │
│  │  └────────┬────────┘         └────────┬────────┘          │  │
│  │           │                           │                    │  │
│  │  ┌────────▼────────┐         ┌────────▼────────┐          │  │
│  │  │ Service:        │         │ Service:        │          │  │
│  │  │ todo-frontend   │────────▶│ todo-backend    │          │  │
│  │  │ (NodePort)      │         │ (ClusterIP)     │          │  │
│  │  │ :32278          │         │ :8000           │          │  │
│  │  └────────┬────────┘         └─────────────────┘          │  │
│  │           │                                                │  │
│  └───────────┼────────────────────────────────────────────────┘  │
│              │                                                    │
└──────────────┼────────────────────────────────────────────────────┘
               │
               ▼
         YOUR BROWSER
         http://127.0.0.1:32278
```

### File Flow

```
Source Code
    │
    ▼
Dockerfile ──────────▶ docker build ──────────▶ Docker Image
                                                      │
                                                      ▼
                                            minikube image load
                                                      │
                                                      ▼
                                              Minikube Image Cache
                                                      │
                                                      ▼
Deployment YAML ─────▶ kubectl apply ──────────▶ Running Pod
                                                      │
                                                      ▼
Service YAML ────────▶ kubectl apply ──────────▶ Network Access
```

### Useful Debugging Commands

```bash
# See what's happening with a pod
kubectl describe pod <pod-name> -n todo-app

# See real-time logs
kubectl logs -f deployment/todo-backend -n todo-app

# Get a shell inside a container
kubectl exec -it <pod-name> -n todo-app -- sh

# See events (useful for debugging)
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n todo-app
```

### Current Status

```bash
# Check everything is running
kubectl get all -n todo-app

# Expected output:
NAME                                 READY   STATUS    RESTARTS   AGE
pod/todo-backend-xxxxx              1/1     Running   0          Xm
pod/todo-frontend-xxxxx             1/1     Running   0          Xm

NAME                    TYPE        CLUSTER-IP      PORT(S)          AGE
service/todo-backend    ClusterIP   10.x.x.x        8000/TCP         Xm
service/todo-frontend   NodePort    10.x.x.x        3000:32278/TCP   Xm

NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/todo-backend    1/1     1            1           Xm
deployment.apps/todo-frontend   1/1     1            1           Xm
```

---

## Next Steps

When you're ready to continue:

1. **Test the app** (T039): Open the frontend URL and verify everything works
2. **Helm deployment** (Phase 5): Deploy using Helm instead of raw manifests
3. **Documentation** (Phase 7): Create deployment guides

Would you like to proceed with any of these?
