# Todo Chatbot Helm Chart

<!-- [Task]: T062, T088 [From]: spec.md FR-013, FR-016 -->

A Helm chart for deploying the Todo Chatbot application to Kubernetes, including the event-driven microservices (notification and recurring-task services), Dapr sidecar integration, and Kafka infrastructure.

## Prerequisites

- Kubernetes 1.28+
- Helm 3.13+
- Container images built and loaded into cluster
- **Phase V (optional)**: Dapr runtime installed (`dapr init -k`), Strimzi Kafka operator deployed

## Installation

### Quick Start (Minikube)

```bash
# 1. Build and load images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
docker build -t notification-service:latest ./services/notification
docker build -t recurring-task-service:latest ./services/recurring-task
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
minikube image load notification-service:latest
minikube image load recurring-task-service:latest

# 2. Install with secrets
helm install todo-chatbot ./k8s/helm/todo-chatbot \
  -f ./k8s/helm/todo-chatbot/values-minikube.yaml \
  --set secrets.databaseUrl="postgresql://user:pass@host/db?sslmode=require" \
  --set secrets.openaiApiKey="sk-your-key" \
  --set secrets.betterAuthSecret="your-secret"

# 3. Access the application
minikube service todo-frontend -n todo-app
```

### Quick Start (Oracle OKE)

```bash
helm upgrade --install todo-chatbot ./k8s/helm/todo-chatbot \
  -f ./k8s/helm/todo-chatbot/values-oke.yaml \
  --namespace todo-app --create-namespace
```

### Using Existing Secrets

If you've already created secrets via kubectl:

```bash
# Create secrets first
kubectl create secret generic todo-chatbot-secrets \
  --namespace=todo-app \
  --from-literal=DATABASE_URL='...' \
  --from-literal=OPENAI_API_KEY='...' \
  --from-literal=BETTER_AUTH_SECRET='...'

# Install without creating secrets
helm install todo-chatbot ./k8s/helm/todo-chatbot \
  --set secrets.create=false \
  --set secrets.existingSecret=todo-chatbot-secrets
```

## Configuration

### Core Services

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.namespace` | Kubernetes namespace | `todo-app` |
| `frontend.enabled` | Enable frontend deployment | `true` |
| `frontend.replicaCount` | Number of frontend replicas | `1` |
| `frontend.image.repository` | Frontend image repository | `todo-frontend` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `frontend.service.type` | Frontend service type | `NodePort` |
| `frontend.resources.requests.memory` | Frontend memory request | `256Mi` |
| `frontend.resources.limits.memory` | Frontend memory limit | `512Mi` |
| `backend.enabled` | Enable backend deployment | `true` |
| `backend.replicaCount` | Number of backend replicas | `1` |
| `backend.image.repository` | Backend image repository | `todo-backend` |
| `backend.image.tag` | Backend image tag | `latest` |
| `backend.service.type` | Backend service type | `ClusterIP` |
| `backend.resources.requests.memory` | Backend memory request | `256Mi` |
| `backend.resources.limits.memory` | Backend memory limit | `512Mi` |

### Secrets

| Parameter | Description | Default |
|-----------|-------------|---------|
| `secrets.create` | Create secrets from values | `true` |
| `secrets.existingSecret` | Use existing secret name | `""` |
| `secrets.databaseUrl` | PostgreSQL connection string | `""` |
| `secrets.openaiApiKey` | OpenAI API key | `""` |
| `secrets.betterAuthSecret` | Better Auth JWT secret | `""` |

### Dapr & Kafka (Phase V)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `dapr.enabled` | Enable Dapr sidecar injection | `false` |
| `kafka.brokers` | Kafka bootstrap servers | `taskflow-kafka-bootstrap.kafka:9092` |
| `backend.dapr.appId` | Backend Dapr app ID | `todo-backend` |
| `backend.dapr.appPort` | Backend Dapr app port | `8000` |

### Notification Service (Phase V)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `notification.enabled` | Enable notification service | `false` |
| `notification.replicaCount` | Notification replicas | `1` |
| `notification.image.repository` | Notification image repository | `notification-service` |
| `notification.image.tag` | Notification image tag | `latest` |
| `notification.service.port` | Notification service port | `8001` |
| `notification.dapr.appId` | Notification Dapr app ID | `notification-service` |

### Recurring Task Service (Phase V)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `recurringTask.enabled` | Enable recurring task service | `false` |
| `recurringTask.replicaCount` | Recurring task replicas | `1` |
| `recurringTask.image.repository` | Recurring task image repository | `recurring-task-service` |
| `recurringTask.image.tag` | Recurring task image tag | `latest` |
| `recurringTask.service.port` | Recurring task service port | `8002` |
| `recurringTask.dapr.appId` | Recurring task Dapr app ID | `recurring-task-service` |

## Operations

### Upgrade

```bash
helm upgrade todo-chatbot ./k8s/helm/todo-chatbot \
  --set frontend.replicaCount=2
```

### Uninstall

```bash
helm uninstall todo-chatbot -n todo-app
kubectl delete namespace todo-app
```

### Check Status

```bash
helm status todo-chatbot -n todo-app
kubectl get all -n todo-app
```

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod -l app=todo-frontend -n todo-app
kubectl logs -l app=todo-frontend -n todo-app
```

### Dapr sidecar issues

```bash
kubectl logs -l app=todo-backend -n todo-app -c daprd
dapr status -k
```

### Kafka connectivity

```bash
kubectl get kafka -n kafka
kubectl logs -l app=todo-backend -n todo-app | grep -i kafka
```

### Secret issues

```bash
kubectl get secret -n todo-app
kubectl describe secret todo-chatbot-secrets -n todo-app
```

### Service access

```bash
minikube service todo-frontend -n todo-app --url
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app
```

## Values Files

| File | Target | Description |
|------|--------|-------------|
| `values.yaml` | Default | Base configuration, Dapr/Kafka disabled |
| `values-minikube.yaml` | Minikube | Local dev with NodePort services |
| `values-oke.yaml` | Oracle OKE | ARM64 images, OCIR repos, Dapr+Kafka enabled |
