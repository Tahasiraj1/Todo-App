# Quickstart: Phase IV - Local Kubernetes Deployment

**Date**: 2026-01-27
**Feature**: 4-k8s-local-deployment
**Purpose**: Step-by-step guide to deploy Todo Chatbot on Minikube

---

## Prerequisites

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| Docker Desktop | 4.53+ | https://docs.docker.com/get-docker/ |
| Minikube | 1.32+ | https://minikube.sigs.k8s.io/docs/start/ |
| kubectl | 1.28+ | https://kubernetes.io/docs/tasks/tools/ |
| Helm | 3.13+ | https://helm.sh/docs/intro/install/ |

### Verify Installation

```bash
# Verify all tools are installed
docker --version
minikube version
kubectl version --client
helm version
```

---

## Quick Deploy (5 Minutes)

### 1. Start Minikube

```bash
# Start with recommended resources
minikube start --cpus=2 --memory=4096

# Verify cluster is running
minikube status
```

### 2. Build Container Images

```bash
# From repository root
cd /path/to/Todo-App

# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Build backend image
docker build -t todo-backend:latest ./backend

# Load images into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
```

### 3. Create Secrets

```bash
# Create namespace first
kubectl create namespace todo-app

# Create secrets from your environment
kubectl create secret generic todo-secrets \
  --namespace=todo-app \
  --from-literal=DATABASE_URL='your-neon-connection-string' \
  --from-literal=OPENAI_API_KEY='your-openai-api-key' \
  --from-literal=BETTER_AUTH_SECRET='your-better-auth-secret'
```

### 4. Deploy with Helm

```bash
# Install the chart
helm install todo-chatbot ./k8s/helm/todo-chatbot \
  --namespace todo-app \
  --values ./k8s/helm/todo-chatbot/values-minikube.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod \
  --all \
  --namespace=todo-app \
  --timeout=180s
```

### 5. Access the Application

```bash
# Get the frontend URL
minikube service todo-frontend -n todo-app --url

# This will output something like:
# http://192.168.49.2:31234

# Open in browser or use curl to test
curl http://192.168.49.2:31234/api/health
```

---

## Detailed Steps

### Step 1: Environment Setup

#### 1.1 Start Docker Desktop

Ensure Docker Desktop is running before starting Minikube.

#### 1.2 Configure Minikube

```bash
# Start Minikube with Docker driver (recommended)
minikube start \
  --driver=docker \
  --cpus=2 \
  --memory=4096 \
  --disk-size=20g

# Enable useful addons
minikube addons enable metrics-server
minikube addons enable dashboard
```

#### 1.3 Verify Cluster

```bash
# Check cluster info
kubectl cluster-info

# List nodes
kubectl get nodes

# Expected output:
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   1m    v1.28.x
```

---

### Step 2: Build Container Images

#### 2.1 Frontend Image

```bash
# Navigate to repository root
cd /path/to/Todo-App

# Build the frontend image
docker build \
  --tag todo-frontend:latest \
  --file frontend/Dockerfile \
  ./frontend

# Verify image was created
docker images | grep todo-frontend
```

#### 2.2 Backend Image

```bash
# Build the backend image
docker build \
  --tag todo-backend:latest \
  --file backend/Dockerfile \
  ./backend

# Verify image was created
docker images | grep todo-backend
```

#### 2.3 Load Images into Minikube

```bash
# Load both images
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Verify images are in Minikube
minikube image ls | grep todo
```

---

### Step 3: Configure Secrets

#### 3.1 Prepare Secret Values

Get your credentials from:
- **DATABASE_URL**: Neon dashboard → Connection string
- **OPENAI_API_KEY**: OpenAI platform → API keys
- **BETTER_AUTH_SECRET**: Generate or use existing from .env

#### 3.2 Create Kubernetes Secrets

```bash
# Method 1: From command line
kubectl create secret generic todo-secrets \
  --namespace=todo-app \
  --from-literal=DATABASE_URL='postgresql://user:pass@host/db?sslmode=require' \
  --from-literal=OPENAI_API_KEY='sk-xxx' \
  --from-literal=BETTER_AUTH_SECRET='your-secret'

# Method 2: From .env file
kubectl create secret generic todo-secrets \
  --namespace=todo-app \
  --from-env-file=backend/.env

# Verify secret was created
kubectl get secrets -n todo-app
```

---

### Step 4: Deploy Application

#### 4.1 Using Helm (Recommended)

```bash
# Install the Helm chart
helm install todo-chatbot ./k8s/helm/todo-chatbot \
  --namespace todo-app \
  --values ./k8s/helm/todo-chatbot/values-minikube.yaml \
  --set secrets.create=false

# Check deployment status
helm status todo-chatbot -n todo-app
```

#### 4.2 Using Raw Manifests (Alternative)

```bash
# Apply all manifests
kubectl apply -f ./k8s/base/ --namespace=todo-app

# Check resources
kubectl get all -n todo-app
```

---

### Step 5: Verify Deployment

#### 5.1 Check Pod Status

```bash
# List all pods
kubectl get pods -n todo-app

# Expected output:
# NAME                            READY   STATUS    RESTARTS   AGE
# todo-frontend-xxx-yyy           1/1     Running   0          1m
# todo-backend-xxx-yyy            1/1     Running   0          1m
```

#### 5.2 Check Pod Logs

```bash
# Frontend logs
kubectl logs -l app=todo-frontend -n todo-app

# Backend logs
kubectl logs -l app=todo-backend -n todo-app
```

#### 5.3 Check Services

```bash
# List services
kubectl get services -n todo-app

# Expected output:
# NAME            TYPE        CLUSTER-IP       PORT(S)          AGE
# todo-frontend   NodePort    10.96.xxx.xxx    3000:3xxxx/TCP   1m
# todo-backend    ClusterIP   10.96.xxx.xxx    8000/TCP         1m
```

---

### Step 6: Access Application

#### 6.1 Get Frontend URL

```bash
# Get the service URL
minikube service todo-frontend -n todo-app --url

# Or open directly in browser
minikube service todo-frontend -n todo-app
```

#### 6.2 Test Health Endpoints

```bash
# Get the URL first
FRONTEND_URL=$(minikube service todo-frontend -n todo-app --url)

# Test frontend health
curl $FRONTEND_URL/api/health

# Test backend via port-forward (internal service)
kubectl port-forward svc/todo-backend 8000:8000 -n todo-app &
curl http://localhost:8000/health
```

#### 6.3 Use the Application

1. Open the frontend URL in your browser
2. Sign up or log in
3. Create, update, and complete tasks
4. Test the AI chatbot functionality

---

## Common Operations

### View Dashboard

```bash
minikube dashboard
```

### Scale Deployment

```bash
# Scale frontend to 2 replicas
kubectl scale deployment todo-frontend --replicas=2 -n todo-app

# Or with Helm
helm upgrade todo-chatbot ./k8s/helm/todo-chatbot \
  --namespace todo-app \
  --set frontend.replicaCount=2
```

### Update Deployment

```bash
# Rebuild and reload images
docker build -t todo-frontend:v2 ./frontend
minikube image load todo-frontend:v2

# Update with Helm
helm upgrade todo-chatbot ./k8s/helm/todo-chatbot \
  --namespace todo-app \
  --set frontend.image.tag=v2
```

### View Logs

```bash
# Follow frontend logs
kubectl logs -f -l app=todo-frontend -n todo-app

# Follow backend logs
kubectl logs -f -l app=todo-backend -n todo-app
```

### Debug Pod

```bash
# Exec into pod
kubectl exec -it deployment/todo-backend -n todo-app -- /bin/sh

# Describe pod for events
kubectl describe pod -l app=todo-backend -n todo-app
```

---

## Cleanup

### Remove Application

```bash
# Uninstall Helm release
helm uninstall todo-chatbot -n todo-app

# Delete namespace (removes all resources)
kubectl delete namespace todo-app

# Remove images from Minikube
minikube image rm todo-frontend:latest
minikube image rm todo-backend:latest
```

### Stop Minikube

```bash
# Stop cluster (preserves state)
minikube stop

# Delete cluster (removes everything)
minikube delete
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n todo-app

# Common issues:
# - ImagePullBackOff: Image not loaded into Minikube
# - CrashLoopBackOff: Application error, check logs
# - Pending: Insufficient resources
```

### Database Connection Failed

```bash
# Verify secret exists
kubectl get secret todo-secrets -n todo-app -o yaml

# Test from pod
kubectl exec -it deployment/todo-backend -n todo-app -- \
  python -c "import os; print(os.environ.get('DATABASE_URL', 'NOT SET'))"
```

### Cannot Access Frontend

```bash
# Verify service is running
kubectl get svc todo-frontend -n todo-app

# Check if minikube tunnel is needed
minikube tunnel

# Try port-forward as alternative
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app
```

---

## Next Steps

After successful local deployment:

1. **Test all functionality**: Authentication, tasks, chatbot
2. **Document any issues**: Create GitHub issues if needed
3. **Prepare for Phase V**: Review cloud deployment requirements

---

**Quickstart Status**: ✅ COMPLETE
