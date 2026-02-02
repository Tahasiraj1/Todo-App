# Kubernetes Deployment Troubleshooting Guide

**Purpose**: Quick solutions for common issues when deploying the Todo Chatbot to Kubernetes.

---

## Quick Diagnostics

```bash
# Check overall status
kubectl get all -n todo-app

# View recent events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check pod logs
kubectl logs -n todo-app deployment/todo-backend
kubectl logs -n todo-app deployment/todo-frontend
```

---

## Common Issues

### 1. Pod in CrashLoopBackOff

**Symptoms:**
```
NAME                          READY   STATUS             RESTARTS
todo-backend-xxx              0/1     CrashLoopBackOff   5
```

**Diagnosis:**
```bash
# View logs from crashed container
kubectl logs -n todo-app <pod-name> --previous

# Or describe the pod for events
kubectl describe pod -n todo-app <pod-name>
```

**Common Causes & Fixes:**

| Cause | Log Pattern | Fix |
|-------|-------------|-----|
| Missing module | `ModuleNotFoundError` | Rebuild image with `--no-cache` |
| Database connection | `Connection refused` | Check DATABASE_URL secret |
| Port conflict | `Address already in use` | Check PORT env variable |
| Missing secret | `KeyError: 'OPENAI_API_KEY'` | Verify secrets exist |

---

### 2. Pod in ImagePullBackOff

**Symptoms:**
```
NAME                          READY   STATUS             RESTARTS
todo-frontend-xxx             0/1     ImagePullBackOff   0
```

**Fixes:**

```bash
# Verify image exists locally
docker images | grep todo-frontend

# Reload image into Minikube
minikube image load todo-frontend:latest

# Check image is in Minikube
minikube image ls | grep todo-frontend

# Force pod restart
kubectl rollout restart deployment/todo-frontend -n todo-app
```

---

### 3. Liveness/Readiness Probe Failures

**Symptoms:**
```
Warning  Unhealthy  Liveness probe failed: connection refused
```

**Fixes:**

1. **Increase initial delay** (slow startup):
   ```bash
   kubectl edit deployment/todo-backend -n todo-app
   # Change initialDelaySeconds from 15 to 30
   ```

2. **Check health endpoint works**:
   ```bash
   kubectl exec -n todo-app <pod-name> -- wget -qO- http://localhost:8000/health
   ```

3. **Via Helm upgrade**:
   ```bash
   helm upgrade todo-chatbot k8s/helm/todo-chatbot \
     --set backend.probes.liveness.initialDelaySeconds=30
   ```

---

### 4. Service Not Accessible

**Symptoms:**
- Can't reach frontend from browser
- `curl: (7) Failed to connect`

**Fixes:**

```bash
# Get NodePort URL
minikube service todo-frontend -n todo-app --url

# Or use port-forward
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app

# Check service exists
kubectl get svc -n todo-app
```

---

### 5. 401 Unauthorized on API Calls

**Symptoms:**
- Frontend shows sign-in screen after authentication
- API calls fail with 401

**Cause:** JWT issuer mismatch between browser and K8s service URL.

**Fix:**
The backend supports multiple issuers. Verify `BETTER_AUTH_URL` in backend config:

```bash
# Check configmap
kubectl get configmap backend-config -n todo-app -o yaml

# Should include:
# BETTER_AUTH_URL: "http://todo-frontend:3000"
```

---

### 6. Minikube Image Not Updating

**Symptoms:**
- Rebuilt image but pod still has old code
- Same error after `minikube image load`

**Fix - Use new tag:**
```bash
# Tag with new version
docker tag todo-backend:latest todo-backend:v5

# Load new tag
minikube image load todo-backend:v5

# Update deployment
kubectl set image deployment/todo-backend backend=todo-backend:v5 -n todo-app
```

---

### 7. Helm Installation Fails

**Error: Namespace exists:**
```
Error: INSTALLATION FAILED: namespaces "todo-app" already exists
```

**Fix:**
```bash
# Delete namespace and let Helm create it
kubectl delete ns todo-app
helm install todo-chatbot k8s/helm/todo-chatbot ...
```

**Error: Release still in use:**
```
Error: cannot re-use a name that is still in use
```

**Fix:**
```bash
# Check existing releases
helm list -A

# Uninstall if exists
helm uninstall todo-chatbot

# Then reinstall
helm install todo-chatbot k8s/helm/todo-chatbot ...
```

---

### 8. GEMINI_API_KEY Not Set

**Symptoms:**
- AI chat shows "GEMINI_API_KEY environment variable is not set"

**Fix:**
```bash
# Via Helm
helm upgrade todo-chatbot k8s/helm/todo-chatbot \
  --set secrets.geminiApiKey="$(grep GEMINI_API_KEY backend/.env | cut -d'=' -f2-)"
```

---

### 9. Minikube Memory/CPU Issues

**Error:**
```
Requested memory allocation 4096MB is more than available
```

**Fix:**
```bash
# Delete and recreate with lower resources
minikube delete
minikube start --cpus=2 --memory=3072
```

---

### 10. kubectl Connection Refused

**Error:**
```
The connection to the server localhost:8080 was refused
```

**Fixes:**
```bash
# Check Minikube is running
minikube status

# If stopped, start it
minikube start

# Verify kubectl context
kubectl config current-context
# Should show "minikube"

# Fix context if needed
kubectl config use-context minikube
```

---

## Debugging Commands Cheat Sheet

| Command | Purpose |
|---------|---------|
| `kubectl get pods -n todo-app -w` | Watch pods in real-time |
| `kubectl logs -f deployment/todo-backend -n todo-app` | Stream logs |
| `kubectl exec -it <pod> -n todo-app -- sh` | Shell into container |
| `kubectl describe pod <pod> -n todo-app` | Full pod details |
| `kubectl get events -n todo-app --sort-by='.lastTimestamp'` | Recent events |
| `minikube dashboard` | Open web dashboard |
| `helm status todo-chatbot` | Helm release status |
| `helm history todo-chatbot` | Helm release history |

---

## Reset Everything

If all else fails, clean slate:

```bash
# Uninstall Helm release
helm uninstall todo-chatbot

# Delete namespace (removes everything)
kubectl delete ns todo-app

# Delete Minikube cluster
minikube delete

# Start fresh
minikube start --cpus=2 --memory=3072

# Rebuild and reload images
docker build -t todo-frontend:latest ./frontend --no-cache
docker build -t todo-backend:latest ./backend --no-cache
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Install via Helm
helm install todo-chatbot k8s/helm/todo-chatbot \
  -f k8s/helm/todo-chatbot/values-minikube.yaml \
  --set secrets.databaseUrl="..." \
  --set secrets.openaiApiKey="..." \
  --set secrets.betterAuthSecret="..." \
  --set secrets.geminiApiKey="..."
```
