# Oracle OKE Deployment Guide

**Task**: T046 | **Feature**: Phase V — Advanced Cloud Deployment

## Prerequisites

- Oracle Cloud Infrastructure (OCI) account with always-free tier
- OCI CLI installed and configured (`oci setup config`)
- kubectl installed
- Helm 3 installed
- Docker with buildx support (for multi-arch builds)

## 1. Provision OKE Cluster

### Create the cluster via OCI Console or CLI

```bash
# Create a VCN for the cluster (if not already existing)
oci ce cluster create \
  --compartment-id <compartment-ocid> \
  --name todo-app-cluster \
  --kubernetes-version v1.28.2 \
  --vcn-id <vcn-ocid> \
  --service-lb-subnet-ids '["<subnet-ocid>"]' \
  --endpoint-subnet-id <subnet-ocid>

# Create a node pool with ARM64 A1 shapes (always-free)
oci ce node-pool create \
  --compartment-id <compartment-ocid> \
  --cluster-id <cluster-ocid> \
  --name todo-app-pool \
  --node-shape VM.Standard.A1.Flex \
  --node-shape-config '{"memoryInGBs": 12, "ocpus": 2}' \
  --size 2 \
  --node-image-id <oracle-linux-arm-image-ocid> \
  --placement-configs '[{"availabilityDomain": "<ad-name>", "subnetId": "<worker-subnet-ocid>"}]'
```

### Configure kubectl

```bash
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region <region> \
  --token-version 2.0.0

kubectl get nodes  # Verify connectivity
```

## 2. Configure OCIR (Oracle Container Registry)

```bash
# Login to OCIR
docker login <region>.ocir.io \
  -u '<tenancy-namespace>/<username>' \
  -p '<auth-token>'

# Create a Kubernetes secret for image pulling
kubectl create namespace todo-app

kubectl create secret docker-registry ocir-secret \
  --namespace todo-app \
  --docker-server=<region>.ocir.io \
  --docker-username='<tenancy-namespace>/<username>' \
  --docker-password='<auth-token>' \
  --docker-email='<email>'
```

## 3. Build and Push Multi-Architecture Images

```bash
# Create buildx builder for multi-arch
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap

# Build and push backend
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t <region>.ocir.io/<tenancy>/todo-backend:latest \
  --push \
  -f backend/Dockerfile \
  backend/

# Build and push frontend
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t <region>.ocir.io/<tenancy>/todo-frontend:latest \
  --push \
  -f frontend/Dockerfile \
  frontend/

# Build and push notification service
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t <region>.ocir.io/<tenancy>/todo-notification:latest \
  --push \
  -f services/notification/Dockerfile \
  services/notification/

# Build and push recurring-task service
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t <region>.ocir.io/<tenancy>/todo-recurring-task:latest \
  --push \
  -f services/recurring-task/Dockerfile \
  services/recurring-task/
```

## 4. Install Infrastructure Components

### Install Dapr

```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system --create-namespace \
  --wait
```

### Install Strimzi Kafka Operator

```bash
helm repo add strimzi https://strimzi.io/charts/
helm repo update
helm install strimzi-kafka strimzi/strimzi-kafka-operator \
  --namespace kafka --create-namespace \
  --wait

# Deploy Kafka cluster
kubectl apply -f k8s/kafka/kafka-cluster.yaml

# Wait for Kafka to be ready
kubectl wait kafka/taskflow-kafka --for=condition=Ready \
  --timeout=300s -n kafka
```

### Deploy Dapr Components

```bash
kubectl apply -f k8s/dapr/kafka-pubsub.yaml
kubectl apply -f k8s/dapr/subscriptions.yaml
kubectl apply -f k8s/dapr/kubernetes-secrets.yaml
```

## 5. Deploy Application via Helm

```bash
# Update values-oke.yaml with your OCIR paths
# Replace <region> and <tenancy> in image repository fields

helm upgrade --install todo-chatbot ./k8s/helm/todo-chatbot \
  -f k8s/helm/todo-chatbot/values-oke.yaml \
  --namespace todo-app \
  --create-namespace \
  --set secrets.databaseUrl="<your-neon-db-url>" \
  --set secrets.openaiApiKey="<your-openai-key>" \
  --set secrets.betterAuthSecret="<your-auth-secret>" \
  --set secrets.geminiApiKey="<your-gemini-key>" \
  --wait
```

## 6. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check Dapr sidecars are injected
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.name}{","}{end}{"\n"}{end}'

# Test health endpoints
kubectl port-forward svc/todo-backend 8000:8000 -n todo-app &
curl http://localhost:8000/health

kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app &
curl http://localhost:3000/api/health
```

## 7. Configure Ingress (Optional)

```bash
# Install NGINX ingress controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=LoadBalancer

# Get the external IP
kubectl get svc nginx-ingress-ingress-nginx-controller -n ingress-nginx

# Point your DNS to the external IP, then access via todo.example.com
```

## Troubleshooting

| Issue | Check |
|-------|-------|
| Pods stuck in ImagePullBackOff | Verify OCIR secret and image paths |
| Dapr sidecar not injecting | Check `dapr.io/enabled: "true"` annotation, verify Dapr is installed |
| Kafka connection errors | Verify Strimzi cluster is Ready, check broker address |
| OOM kills | Increase resource limits in values-oke.yaml |
| Health check failures | Port-forward and test /health endpoint directly |
