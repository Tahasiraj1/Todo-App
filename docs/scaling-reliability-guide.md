# Scaling and Reliability — Keeping Your App Running Under Pressure

**Context**: This guide picks up where the cloud-native stack guide left off. You have a working Kubernetes deployment with `replicas: 1`. The app works, but one pod crash means downtime. This guide covers how to make the app resilient, self-scaling, and zero-downtime.

**Prerequisites**: Understanding of Pods, Deployments, and Services from `docs/cloud-native-stack-guide.md`.

---

## The Problem

With `replicas: 1`:

```
User Request  ──→  Service  ──→  [Pod]  (the only one)
                                   │
                                   ╳  Pod crashes
                                   │
                                   ⏳ Kubernetes restarts (10-30 seconds)
                                   │
                                   ✓  Pod is back
```

During those 10-30 seconds, the app is down. If traffic spikes, one pod handles everything until it's overwhelmed. If you deploy a new version, the old pod dies before the new one is ready.

---

## Concept 1: Horizontal Scaling

### What It Is

Run multiple identical copies of your application. If one fails, others keep serving. If traffic increases, add more copies.

### How It Works

```yaml
# deployment.yaml
spec:
  replicas: 3
```

That's it. Kubernetes creates 3 pods from the same image. The Service load-balances across all of them.

```
Service: todo-backend
    │
    ├──→ todo-backend-pod-1  (10.244.0.15)
    ├──→ todo-backend-pod-2  (10.244.0.16)
    └──→ todo-backend-pod-3  (10.244.0.17)
```

If pod-2 crashes:

```
Service: todo-backend
    │
    ├──→ todo-backend-pod-1  (10.244.0.15)    ← still serving
    ├──→ todo-backend-pod-2  ╳ crashed         ← Kubernetes restarting
    └──→ todo-backend-pod-3  (10.244.0.17)    ← still serving
```

Users don't notice. Two pods handle traffic while the third restarts.

### Horizontal vs. Vertical Scaling

| | Horizontal | Vertical |
|---|---|---|
| **What changes** | Number of pods | Pod CPU/memory |
| **Example** | 1 pod → 3 pods | 256MB → 1GB RAM |
| **Ceiling** | Effectively none | Limited by largest machine |
| **Failure impact** | One pod fails, others survive | The one pod fails, everything's down |
| **Cost** | Linear (more pods = more cost) | Exponential (bigger machines cost disproportionately more) |
| **Cloud-native preference** | This one | Avoid when possible |

**The principle**: Scale out (horizontal), not up (vertical). Small, replaceable instances are cheaper and more resilient than one big server.

### When Horizontal Scaling Doesn't Work

Your app must be **stateless** for horizontal scaling. That means:

- No session data stored in memory (use Redis or database sessions)
- No local file storage that other pods need (use S3 or Persistent Volumes)
- No in-memory caches that must be consistent (use Redis)

Our todo app is stateless — it reads/writes to a database, doesn't store anything locally. So horizontal scaling works directly.

---

## Concept 2: Resource Requests and Limits

### What They Are

Every container should declare how much CPU and memory it needs. This is how Kubernetes makes scheduling decisions.

```yaml
containers:
  - name: todo-backend
    resources:
      requests:
        memory: "128Mi"       # "I need at least 128MB to run"
        cpu: "100m"           # "I need at least 0.1 CPU cores"
      limits:
        memory: "512Mi"       # "Never let me use more than 512MB"
        cpu: "500m"           # "Never let me use more than 0.5 CPU cores"
```

### Requests vs. Limits

| | Requests | Limits |
|---|---|---|
| **Purpose** | Scheduling (where to place the pod) | Protection (prevent resource hogging) |
| **When enforced** | At pod creation time | At runtime |
| **What happens** | Pod won't be scheduled if node doesn't have this much free | Pod gets killed (OOM) or throttled (CPU) if it exceeds |

### CPU Units

CPU is measured in **millicores** (m).

```
1000m = 1 full CPU core
500m  = half a CPU core
100m  = 10% of a CPU core
```

If a container exceeds its CPU limit, it's **throttled** — slowed down, not killed.

### Memory Units

```
128Mi = 128 mebibytes (~134 MB)
1Gi   = 1 gibibyte (~1.07 GB)
```

If a container exceeds its memory limit, it's **OOMKilled** (Out of Memory Killed) — Kubernetes terminates it and restarts.

### Why This Matters

Without resource declarations:
- Kubernetes places pods blindly → nodes run out of memory → everything crashes
- One pod can consume all CPU → starves other pods on the same node

This is exactly what happened when kagent's 30 pods ran on our 3GB Minikube — no resource limits, everything fighting for memory.

### How to Choose Values

```
requests: What the app needs under normal load
          Measure by running the app and observing actual usage

limits:   What the app might spike to under peak load
          Set to 2-4x the request as a safety margin
```

```bash
# Observe actual resource usage
kubectl top pods -n todo-app

# Output:
# NAME                            CPU(cores)   MEMORY(bytes)
# todo-backend-57b578f5b9-l26df   15m          85Mi
# todo-frontend-77787fb4d7-kfbxm  10m          120Mi
```

From this, reasonable settings would be:

```yaml
# Backend
requests: { cpu: "50m", memory: "128Mi" }
limits:   { cpu: "200m", memory: "512Mi" }

# Frontend
requests: { cpu: "50m", memory: "150Mi" }
limits:   { cpu: "200m", memory: "512Mi" }
```

### Quality of Service (QoS) Classes

Kubernetes assigns a QoS class to each pod based on resource settings:

| QoS Class | Condition | Eviction Priority |
|-----------|-----------|------------------|
| **Guaranteed** | requests == limits for all containers | Last to be evicted |
| **Burstable** | requests < limits (or only requests set) | Evicted after BestEffort |
| **BestEffort** | No requests or limits set | First to be evicted |

Under memory pressure, Kubernetes evicts BestEffort pods first, then Burstable, then Guaranteed. Set requests and limits on production workloads to avoid being evicted first.

---

## Concept 3: Horizontal Pod Autoscaler (HPA)

### What It Is

Instead of manually deciding how many replicas to run, let Kubernetes scale based on actual resource usage.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: todo-backend-hpa
  namespace: todo-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todo-backend
  minReplicas: 2             # Never go below 2 (high availability)
  maxReplicas: 10            # Never go above 10 (cost control)
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70    # Scale up when avg CPU > 70%
```

### How It Works

```
Normal traffic:
  CPU avg: 30%  →  HPA keeps 2 replicas (minReplicas)

Traffic spike:
  CPU avg: 75%  →  Exceeds 70% target
                →  HPA calculates: need ~3 replicas to bring avg below 70%
                →  Creates 1 new pod
                →  Service routes traffic to 3 pods
                →  CPU avg drops to ~50%

Traffic drops:
  CPU avg: 20%  →  Below 70% with too many pods
                →  HPA waits (cooldown period, default 5 min)
                →  Removes 1 pod
                →  Back to minReplicas: 2
```

### Prerequisites

HPA needs to know current CPU/memory usage. This requires the **metrics-server**.

```bash
# On Minikube
minikube addons enable metrics-server

# On managed clusters (EKS, GKE), usually pre-installed

# Verify it's running
kubectl get deployment metrics-server -n kube-system
```

### Creating an HPA

Two ways:

```bash
# Command line (quick)
kubectl autoscale deployment todo-backend \
  --min=2 --max=10 --cpu-percent=70 \
  -n todo-app

# Or apply YAML (for version control)
kubectl apply -f hpa.yaml
```

### Monitoring the HPA

```bash
# Watch scaling in real-time
kubectl get hpa -n todo-app --watch

# Output:
# NAME               REFERENCE                 TARGETS   MINPODS   MAXPODS   REPLICAS
# todo-backend-hpa   Deployment/todo-backend   30%/70%   2         10        2
```

### Scaling on Multiple Metrics

You can scale on CPU, memory, or custom metrics:

```yaml
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

HPA scales to satisfy **all** metrics. If CPU says 3 replicas and memory says 5, HPA uses 5.

### Scaling Behavior (Tuning)

By default, HPA scales up quickly but scales down slowly (to avoid flapping). You can tune this:

```yaml
spec:
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60      # Wait 60s before scaling up
      policies:
        - type: Pods
          value: 4                        # Add at most 4 pods at a time
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300     # Wait 5 min before scaling down
      policies:
        - type: Percent
          value: 25                       # Remove at most 25% of pods at a time
          periodSeconds: 60
```

---

## Concept 4: Rolling Updates

### What It Is

When you update an image (v4 → v5), Kubernetes doesn't kill all pods and start new ones. It **gradually replaces** them, ensuring the app is always available.

### How It Works

```
Time 0:  [v4] [v4] [v4]         ← 3 pods running v4
         ─────────────────
Time 1:  [v4] [v4] [v4] [v5]   ← 1 new v5 pod starts (maxSurge: 1)
         ─────────────────────
Time 2:  [v4] [v4] [v5]         ← v5 passes readiness probe, 1 v4 terminates
         ───────────────
Time 3:  [v4] [v4] [v5] [v5]   ← another v5 starts
         ─────────────────────
Time 4:  [v4] [v5] [v5]         ← another v4 terminates
         ───────────────
Time 5:  [v4] [v5] [v5] [v5]   ← last v5 starts
         ─────────────────────
Time 6:  [v5] [v5] [v5]         ← fully rolled out, zero downtime
         ─────────────────
```

At no point are zero pods running. Users always have a working app.

### Configuration

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1              # Allow 1 extra pod during update (total = replicas + 1)
      maxUnavailable: 0        # Never have fewer than desired replicas
```

| Setting | Effect |
|---------|--------|
| `maxSurge: 1, maxUnavailable: 0` | Safest. Always starts new pod first, waits for it to be ready, then kills old. Uses extra resources temporarily. |
| `maxSurge: 0, maxUnavailable: 1` | No extra resources. Kills one old pod, then starts one new. Brief capacity reduction. |
| `maxSurge: 2, maxUnavailable: 1` | Faster rollout. Allows both extra pods and reduced capacity. |

For most apps, `maxSurge: 1, maxUnavailable: 0` is the right choice. It guarantees zero downtime at the cost of briefly running one extra pod.

### How Readiness Probes Enable This

The rolling update depends on readiness probes:

```
New pod starts  →  readinessProbe fails (app still booting)
                   └── Service does NOT route traffic to it

App finishes booting  →  readinessProbe passes
                         └── Service starts routing traffic
                         └── Kubernetes terminates one old pod
```

Without readiness probes, Kubernetes sends traffic to the new pod immediately — while it's still starting. Users get errors. Readiness probes prevent this.

### Triggering a Rolling Update

```bash
# Method 1: Update image via kubectl
kubectl set image deployment/todo-backend \
  todo-backend=todo-backend:v5 -n todo-app

# Method 2: Update via Helm
helm upgrade todo-chatbot ./k8s/helm/todo-chatbot \
  --set backend.image.tag=v5

# Method 3: Edit deployment directly
kubectl edit deployment todo-backend -n todo-app
```

### Watching the Rollout

```bash
# Watch progress
kubectl rollout status deployment/todo-backend -n todo-app

# Output:
# Waiting for deployment "todo-backend" rollout to finish: 1 out of 3 new replicas have been updated...
# Waiting for deployment "todo-backend" rollout to finish: 2 out of 3 new replicas have been updated...
# deployment "todo-backend" successfully rolled out
```

---

## Concept 5: Rollbacks

### What It Is

If a new version has a bug, revert to the previous known-good version.

### Deployment Rollback

```bash
# See rollout history
kubectl rollout history deployment/todo-backend -n todo-app

# Output:
# REVISION  CHANGE-CAUSE
# 1         Initial deployment
# 2         Updated image to v5

# Roll back to the previous version
kubectl rollout undo deployment/todo-backend -n todo-app

# Roll back to a specific revision
kubectl rollout undo deployment/todo-backend --to-revision=1 -n todo-app
```

This triggers the same rolling update process — but in reverse. Pods are gradually replaced with the old version.

### Helm Rollback

```bash
# See Helm release history
helm history todo-chatbot

# Output:
# REVISION  STATUS      CHART               DESCRIPTION
# 1         superseded  todo-chatbot-0.1.0   Install complete
# 2         deployed    todo-chatbot-0.1.0   Upgrade complete

# Roll back to revision 1
helm rollback todo-chatbot 1

# Verify
helm history todo-chatbot
# REVISION  STATUS      CHART               DESCRIPTION
# 1         superseded  todo-chatbot-0.1.0   Install complete
# 2         superseded  todo-chatbot-0.1.0   Upgrade complete
# 3         deployed    todo-chatbot-0.1.0   Rollback to 1
```

Helm rollback reverts **all** resources (deployments, configmaps, secrets) to their state at that revision. More comprehensive than a single deployment rollback.

---

## Concept 6: Pod Disruption Budgets (PDB)

### What It Is

When Kubernetes needs to evict pods (node upgrades, scaling down nodes, maintenance), a PDB ensures minimum availability.

### The Problem Without PDB

```
Node maintenance starts:
  Kubernetes drains node-1
  ├── Kills todo-backend-pod-1
  ├── Kills todo-backend-pod-2    ← All on the same node
  └── Kills todo-backend-pod-3

  0 pods running. App is down until new pods start elsewhere.
```

### With PDB

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: todo-backend-pdb
  namespace: todo-app
spec:
  minAvailable: 1               # At least 1 pod must always be running
  selector:
    matchLabels:
      app: todo-backend
```

Now:

```
Node maintenance starts:
  Kubernetes drains node-1
  ├── Kills todo-backend-pod-1
  │   └── Waits for replacement to be running
  ├── Kills todo-backend-pod-2
  │   └── Waits for replacement to be running
  └── Kills todo-backend-pod-3
      └── Waits for replacement to be running

  At least 1 pod running at all times. App stays up.
```

### minAvailable vs. maxUnavailable

Two ways to express the same constraint:

```yaml
# "Always keep at least 2 pods running"
spec:
  minAvailable: 2

# "Allow at most 1 pod to be unavailable"
spec:
  maxUnavailable: 1
```

For 3 replicas, `minAvailable: 2` and `maxUnavailable: 1` are equivalent.

You can also use percentages:

```yaml
spec:
  minAvailable: "50%"    # At least half the pods must be running
```

---

## Concept 7: Graceful Shutdown

### What It Is

When Kubernetes terminates a pod (during scaling down, rolling updates, or node drain), it doesn't kill the process immediately. It follows a shutdown sequence:

```
1. Pod is marked for termination
2. Pod is removed from Service endpoints (no new traffic)
3. Kubernetes sends SIGTERM to the container
4. App has "terminationGracePeriodSeconds" to finish current work (default: 30s)
5. If still running after grace period, Kubernetes sends SIGKILL (force kill)
```

### Why It Matters

Without graceful shutdown, a pod processing a request gets killed mid-response. The user gets an error.

With graceful shutdown:

```
Pod receives SIGTERM
  ├── Stops accepting new requests
  ├── Finishes processing in-flight requests
  ├── Closes database connections
  └── Exits cleanly
```

### Configuration

```yaml
spec:
  terminationGracePeriodSeconds: 60     # Give the app 60 seconds to shut down
  containers:
    - name: todo-backend
      lifecycle:
        preStop:
          exec:
            command: ["/bin/sh", "-c", "sleep 5"]    # Wait for Service to remove the pod
```

The `preStop` hook with `sleep 5` is a common pattern. It ensures the Service has removed the pod from its endpoints before the app starts shutting down. Without it, there's a race condition where new requests arrive at a pod that's already shutting down.

---

## Putting It All Together

A production-ready deployment uses all these concepts:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  namespace: todo-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0               # Zero-downtime updates
  template:
    spec:
      terminationGracePeriodSeconds: 60
      containers:
        - name: todo-backend
          image: todo-backend:v4
          ports:
            - containerPort: 8000
          resources:
            requests:                  # Scheduling guarantee
              memory: "128Mi"
              cpu: "100m"
            limits:                    # Safety ceiling
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:               # Restart if unhealthy
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:              # Only serve traffic when ready
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 5"]
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: todo-backend-hpa
  namespace: todo-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todo-backend
  minReplicas: 2                       # High availability
  maxReplicas: 10                      # Cost control
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70       # Scale at 70% CPU
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: todo-backend-pdb
  namespace: todo-app
spec:
  minAvailable: 1                      # Always keep at least 1 running
  selector:
    matchLabels:
      app: todo-backend
```

### The Reliability Chain

Each concept handles a different failure mode:

```
Failure                          Protection                    Concept
───────                          ──────────                    ───────
Pod crashes                      Auto-restart                  Liveness probe
Pod not ready                    Stop sending traffic          Readiness probe
Single pod failure               Other pods serve traffic      Replicas (3+)
Traffic spike                    Add more pods automatically   HPA
Resource starvation              Reserved CPU/memory           Resource requests
Noisy neighbor                   Hard ceilings                 Resource limits
Bad deployment                   Revert to previous version    Rolling update + rollback
Node maintenance                 Gradual eviction              PDB
Mid-request termination          Finish in-flight work         Graceful shutdown
```

No single concept covers everything. Together they create defense in depth.

---

## Key Commands Reference

```bash
# Scaling
kubectl scale deployment todo-backend --replicas=5 -n todo-app  # Manual scale
kubectl autoscale deployment todo-backend \
  --min=2 --max=10 --cpu-percent=70 -n todo-app                 # Create HPA

# Monitoring
kubectl top pods -n todo-app                                     # Resource usage
kubectl get hpa -n todo-app --watch                              # Watch autoscaler

# Updates
kubectl set image deployment/todo-backend \
  todo-backend=todo-backend:v5 -n todo-app                       # Update image
kubectl rollout status deployment/todo-backend -n todo-app       # Watch rollout

# Rollbacks
kubectl rollout history deployment/todo-backend -n todo-app      # See history
kubectl rollout undo deployment/todo-backend -n todo-app         # Undo last change
helm rollback todo-chatbot 1                                     # Helm rollback

# Disruption budgets
kubectl get pdb -n todo-app                                      # List PDBs
kubectl describe pdb todo-backend-pdb -n todo-app                # PDB details
```

---

## Summary

| Concept | What it does | Key setting |
|---------|-------------|-------------|
| **Horizontal scaling** | Run multiple pod copies | `replicas: 3` |
| **Resource requests** | Reserve CPU/memory for scheduling | `requests: {cpu: "100m", memory: "128Mi"}` |
| **Resource limits** | Cap maximum resource usage | `limits: {cpu: "500m", memory: "512Mi"}` |
| **HPA** | Auto-scale replicas based on metrics | `averageUtilization: 70` |
| **Rolling updates** | Replace pods gradually, zero downtime | `maxSurge: 1, maxUnavailable: 0` |
| **Rollbacks** | Revert to a previous version | `kubectl rollout undo` / `helm rollback` |
| **PDB** | Maintain minimum pods during disruptions | `minAvailable: 1` |
| **Graceful shutdown** | Finish in-flight work before terminating | `terminationGracePeriodSeconds: 60` |

The goal is an app that scales automatically, updates without downtime, recovers from failures without human intervention, and survives infrastructure maintenance. These eight concepts make that possible.
