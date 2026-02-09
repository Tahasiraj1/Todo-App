# Quickstart: Phase 5 Testing Plan

**Feature**: 006-phase5-testing-plan
**Date**: 2026-02-09

---

## Prerequisites

1. **WSL2 environment** with kubectl configured for OKE cluster
2. **DNS resolution**: Verify `/etc/hosts` contains `104.21.23.140 todo.tahasiraj.com`
3. **Playwright MCP**: Available via Claude Code (already configured in project)
4. **Valid credentials**: Email and password for the app at `https://todo.tahasiraj.com`
5. **kubectl access**: OKE cluster credentials configured (`~/.kube/config`)

## Verify Prerequisites

```bash
# Check DNS resolution
ping -c 1 todo.tahasiraj.com

# Check kubectl access
kubectl get nodes

# Check app pods are running
kubectl get pods -n todo-app
```

## Execute Test Plan

### Step 1: Infrastructure Verification

Run via Bash:
```bash
# TC-01: App pods
kubectl get pods -n todo-app

# TC-02: Dapr system
kubectl get pods -n dapr-system

# TC-03: Kafka cluster
kubectl get kafka -n kafka

# TC-04: Kafka topics
kubectl get kafkatopics -n kafka
```

**Expected**: All pods Running, Kafka cluster Ready, topics exist.

### Step 2: Browser Testing

Use Playwright MCP via Claude Code:

1. Navigate to `https://todo.tahasiraj.com`
2. Sign in with credentials
3. Execute test cases TC-05 through TC-30 sequentially
4. Take screenshots at key milestones

### Step 3: Report Generation

After all tests complete:
1. Compile pass/fail results into a markdown table
2. Map each result to hackathon requirement
3. Create 90-second demo video structure

## Quick Commands

```bash
# Check if frontend image needs rebuild (recurrence fix)
kubectl get pods -n todo-app -o jsonpath='{.items[*].spec.containers[*].image}' | tr ' ' '\n'

# Rebuild and push frontend (if needed)
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ap-hyderabad-1.ocir.io/<tenancy>/todo-frontend:latest \
  --push -f frontend/Dockerfile frontend/

# Restart frontend deployment
kubectl rollout restart deployment/todo-frontend -n todo-app

# Port-forward fallback (if Cloudflare Tunnel is down)
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app &
kubectl port-forward svc/todo-backend 8000:8000 -n todo-app &
```

## Expected Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Prerequisites check | 2 min | 2 min |
| Infrastructure verification | 3 min | 5 min |
| Auth + CRUD tests | 3 min | 8 min |
| Intermediate feature tests | 3 min | 11 min |
| Advanced feature tests | 2 min | 13 min |
| AI Chatbot tests | 3 min | 16 min |
| Event-driven tests | 2 min | 18 min |
| Report + demo structure | 5 min | 23 min |
| **Total** | **~23 min** | |
