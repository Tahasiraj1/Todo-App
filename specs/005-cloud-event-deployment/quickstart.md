# Quickstart: Phase V — Advanced Cloud Deployment

**Feature**: `005-cloud-event-deployment`
**Date**: 2026-01-31

---

## Prerequisites

- Phase IV complete: Docker images build, Helm chart deploys on Minikube
- Minikube running with `--cpus=4 --memory=8192` (Kafka + Dapr require more resources)
- Dapr CLI installed: `curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash`
- Oracle Cloud account with always-free tier enabled (for cloud deployment)

## Local Development Order (Minikube)

### Step 1: Extend Task Model & API

1. Add new columns to Task SQLModel (priority, tags, due_date, recurrence fields)
2. Update TaskCreate/TaskUpdate schemas with new fields
3. Extend task API endpoints with filter, sort, search query parameters
4. Update MCP tools (add_task, list_tasks, update_task) with new parameters
5. Test locally: `uvicorn src.main:app` → create tasks with priorities, tags, due dates

### Step 2: Install Dapr on Minikube

```bash
dapr init -k                          # Install Dapr control plane
dapr status -k                        # Verify all components running
kubectl get pods -n dapr-system        # Should show operator, sentry, placement, dashboard
```

### Step 3: Deploy Kafka (Strimzi)

```bash
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka
kubectl apply -f k8s/kafka/kafka-cluster.yaml     # Single-broker, ephemeral
kubectl wait kafka/taskflow-kafka --for=condition=Ready --timeout=300s -n kafka
```

### Step 4: Deploy Dapr Components

```bash
kubectl apply -f k8s/dapr/kafka-pubsub.yaml       # Pub/Sub component
kubectl apply -f k8s/dapr/subscriptions.yaml       # Declarative subscriptions
kubectl apply -f k8s/dapr/kubernetes-secrets.yaml   # Secrets store
```

### Step 5: Add Event Publishing to Backend

1. After each task mutation, publish event to `task-events` and `task-updates` topics via Dapr HTTP API
2. Add Dapr subscription handler: `POST /api/events/task-events` → persist to activity_log table
3. Add Dapr Jobs scheduling: when due_date is set, schedule reminder job
4. Add Dapr Jobs handler: `POST /api/jobs/reminder-{task_id}` → publish to `reminders` topic

### Step 6: Build Notification Service

1. New Python service (FastAPI) with Dapr sidecar
2. Subscribes to `reminders` topic → sends WebSocket message to user
3. Subscribes to `task-updates` topic → broadcasts to all user's connected tabs
4. WebSocket endpoint at `/ws/{user_id}`

### Step 7: Build Recurring Task Service

1. New Python service (FastAPI) with Dapr sidecar
2. Subscribes to `task-events` topic, filters for `completed` events where `is_recurring=true`
3. Computes next due date from recurrence rule
4. Creates next task occurrence via Dapr service invocation to backend

### Step 8: Update Frontend

1. Add priority selector, tag input, due date picker to task UI
2. Add filter/sort controls to task list
3. Add WebSocket client for real-time updates
4. Add browser notification permission request
5. Add in-app reminder banner (fallback when notifications denied)
6. Add activity log view

### Step 9: Deploy to Minikube with Dapr

```bash
# Build all images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
docker build -t notification-service:latest ./services/notification
docker build -t recurring-task-service:latest ./services/recurring-task

# Load into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
minikube image load notification-service:latest
minikube image load recurring-task-service:latest

# Deploy via Helm
helm upgrade --install todo-chatbot ./k8s/helm/todo-chatbot \
  -f ./k8s/helm/todo-chatbot/values-minikube.yaml \
  --namespace todo-app --create-namespace
```

## Cloud Deployment Order (Oracle OKE)

### Step 10: Provision Oracle OKE Cluster

1. Create OKE cluster in Oracle Cloud console (always-free A1 shapes)
2. Configure kubectl: `oci ce cluster create-kubeconfig --cluster-id <OCID>`
3. Verify: `kubectl get nodes`

### Step 11: Push Images to OCIR

```bash
# Login to Oracle Container Registry
docker login <region>.ocir.io -u <tenancy>/<username> -p <auth-token>

# Build for ARM64 (OKE free tier uses Arm shapes)
docker buildx build --platform linux/arm64 -t <region>.ocir.io/<tenancy>/todo-app/todo-frontend:latest ./frontend --push
docker buildx build --platform linux/arm64 -t <region>.ocir.io/<tenancy>/todo-app/todo-backend:latest ./backend --push
docker buildx build --platform linux/arm64 -t <region>.ocir.io/<tenancy>/todo-app/notification-service:latest ./services/notification --push
docker buildx build --platform linux/arm64 -t <region>.ocir.io/<tenancy>/todo-app/recurring-task-service:latest ./services/recurring-task --push
```

### Step 12: Deploy to OKE

```bash
# Install Dapr on OKE
dapr init -k

# Deploy Kafka (Strimzi)
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka
kubectl apply -f k8s/kafka/kafka-cluster.yaml

# Deploy Dapr components
kubectl apply -f k8s/dapr/

# Deploy app via Helm
helm upgrade --install todo-chatbot ./k8s/helm/todo-chatbot \
  -f ./k8s/helm/todo-chatbot/values-oke.yaml \
  --namespace todo-app --create-namespace
```

### Step 13: Set Up CI/CD

1. Create GitHub Actions workflow (`.github/workflows/deploy.yaml`)
2. Add GitHub Secrets for OCI CLI and OCIR credentials
3. Push to main → automated build, test, push, deploy

## Verification Checklist

- [ ] Tasks can be created with priority, tags, and due dates via chatbot
- [ ] Tasks can be filtered by priority and tag
- [ ] Tasks can be searched by keyword
- [ ] Overdue tasks are visually marked
- [ ] Completing a recurring task creates the next occurrence
- [ ] Reminder notification appears before due date
- [ ] Activity log shows recent operations
- [ ] Changes in one tab appear in another (real-time sync)
- [ ] Application accessible on Oracle OKE via external URL
- [ ] CI/CD pipeline deploys on push to main
