# AI-Assisted Kubernetes Operations Guide

**Purpose**: Document optional AI-assisted operations for Kubernetes management

> **Note**: AI-assisted operations are optional enhancements. All core deployment functionality works without these tools.

---

## Verification Report (2026-01-31)

All three AI tools were installed and verified on this project's Minikube cluster.

| Tool | Version | Installed Via | Status | Notes |
|------|---------|--------------|--------|-------|
| **kubectl-ai** | v0.0.29 | krew (kubectl plugin manager) | **Functional** | Connected to Gemini API; hit free-tier daily quota (429). Proves authentication and connectivity work. |
| **Docker AI (Gordon)** | v1.17.1 | Docker Desktop plugin | **Partial** | `docker ai version` works. Queries fail in WSL2 with "Docker Desktop is not running" — Gordon requires the Desktop GUI's AI backend service, not just the Docker engine. Works from Windows-native terminals. |
| **kagent** | v0.7.12 (Helm chart) | Helm OCI (`ghcr.io/kagent-dev/kagent`) | **Deployed** | CRDs + main chart installed. Controller, tools, and UI pods ran successfully. Full agent fleet (30+ pods) exceeds Minikube's 3GB memory budget, causing pod evictions. |

### Verification Commands Run

```bash
# kubectl-ai — version confirmed
$ kubectl-ai version
version: 0.0.29
commit: 38382d1add89a0c0825bed997d2257733c08b330
date: 2026-01-21T16:57:34Z

# kubectl-ai — query test (proves Gemini API connectivity)
$ export GEMINI_API_KEY=<key>
$ kubectl-ai --quiet --model gemini-2.0-flash "list all namespaces"
# Result: 429 RESOURCE_EXHAUSTED (free-tier daily quota hit)
# This confirms: binary works, API key accepted, Gemini endpoint reachable

# Docker AI (Gordon) — version confirmed
$ docker ai version
v1.17.1

# Docker AI — query test
$ docker ai "analyze the backend Dockerfile"
# Result: "Docker Desktop is not running" (WSL2 limitation)

# kagent — Helm releases confirmed
$ helm list -n kagent
NAME         NAMESPACE  REVISION  STATUS    CHART
kagent       kagent     1         deployed  kagent-0.7.12
kagent-crds  kagent     1         deployed  kagent-crds-0.7.12

# kagent — core pods verified
$ kubectl get pods -n kagent --field-selector=status.phase=Running
# kagent-controller, kagent-tools (1/1), kagent-ui, k8s-agent all reached Running
```

### Known Limitations

1. **Gemini free-tier quota**: kubectl-ai defaults to `gemini-2.5-pro`. Free-tier limits are low. Use `--model gemini-2.0-flash` for lower cost or provide a paid API key.
2. **Docker AI in WSL2**: Gordon requires the Docker Desktop GUI's AI backend service running on the Windows host. Use from PowerShell/CMD or Docker Desktop's integrated terminal instead.
3. **kagent memory footprint**: The full kagent deployment (controller + UI + 10+ specialized agents) spawns ~30 pods. Requires at least 8GB allocated to Minikube. On constrained environments, scale down non-essential agents.

---

## 1. kubectl-ai

**What it does**: Natural language interface for kubectl commands. Translates plain English into kubectl operations using LLMs.

### Installation (verified)

```bash
# Step 1: Install krew (kubectl plugin manager)
cd "$(mktemp -d)" && \
OS="$(uname | tr '[:upper:]' '[:lower:]')" && \
ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/aarch64/arm64/')" && \
KREW="krew-${OS}_${ARCH}" && \
curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" && \
tar zxvf "${KREW}.tar.gz" && \
./"${KREW}" install krew

# Step 2: Add krew to PATH (add to ~/.bashrc for persistence)
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

# Step 3: Install kubectl-ai
kubectl krew install ai

# Step 4: Verify
kubectl-ai version
```

### Configuration

```bash
# Set Gemini API key (default LLM provider)
export GEMINI_API_KEY="your-key-here"

# Or use OpenAI
export OPENAI_API_KEY="sk-..."
kubectl-ai --llm-provider openai "list pods"

# Change model (default is gemini-2.5-pro)
kubectl-ai --model gemini-2.0-flash "list deployments"
```

### Usage Examples

```bash
# List all pods in the todo-app namespace
kubectl ai "show me all pods in todo-app namespace"

# Scale the backend deployment
kubectl ai "scale todo-backend to 3 replicas in todo-app"

# Get logs from the frontend
kubectl ai "show me logs from todo-frontend"

# Debug a failing pod
kubectl ai "why is pod todo-backend-xxx failing?"

# Non-interactive mode (for scripts)
kubectl ai --quiet "list all services in todo-app namespace"
```

---

## 2. Docker AI (Gordon)

**What it does**: AI-powered Docker debugging and assistance built into Docker Desktop.

### Enabling Gordon

1. Update Docker Desktop to v4.30+
2. Gordon is enabled by default in recent versions
3. Verify: `docker ai version`

> **WSL2 note**: Gordon queries require the Docker Desktop GUI's AI backend running on Windows. The `docker ai` CLI from WSL2 can check version but cannot run queries. Use Docker Desktop's integrated terminal or PowerShell instead.

### Usage Examples

```bash
# Debug a container
docker ai "why did container todo-backend exit?"

# Build assistance
docker ai "optimize my Dockerfile for smaller image size"

# Security scanning explanation
docker ai "explain the vulnerabilities found in todo-frontend image"

# Performance suggestions
docker ai "how can I improve container startup time?"
```

### Interactive Mode

Gordon also provides interactive assistance in Docker Desktop:
- Click the "AI" icon in the bottom toolbar
- Ask questions about your containers, images, or Docker Compose files
- Get real-time suggestions for improvements

---

## 3. kagent (Kubernetes Agent)

**What it does**: Autonomous Kubernetes AI agent platform. Deploys specialized agents (k8s-agent, helm-agent, observability-agent, etc.) that use LLMs to manage clusters.

### Installation (verified)

```bash
# Step 1: Install CRDs
helm install kagent-crds \
  oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds \
  --namespace kagent --create-namespace

# Step 2: Install kagent with Gemini provider
helm install kagent \
  oci://ghcr.io/kagent-dev/kagent/helm/kagent \
  --namespace kagent \
  --set modelProvider.gemini.apiKey="YOUR_GEMINI_API_KEY"

# Step 3: Verify core pods
kubectl get pods -n kagent
```

### Key Components

| Pod | Role |
|-----|------|
| `kagent-controller` | Main orchestration controller |
| `kagent-tools` | Tool execution runtime |
| `kagent-ui` | Web dashboard (port 8080) |
| `k8s-agent` | Kubernetes operations agent |
| `helm-agent` | Helm chart management agent |
| `observability-agent` | Monitoring and diagnostics |

### Web UI

```bash
# Port-forward to access the dashboard
kubectl port-forward svc/kagent-ui -n kagent 8080:80

# Open http://localhost:8080 in browser
```

### Resource Requirements

kagent's full deployment spawns 30+ pods. Recommended minimums:
- **Development**: 8GB RAM, 4 CPUs allocated to Minikube
- **Minimal**: Scale down non-essential agents if running on <4GB

---

## Common AI-Assisted Operation Examples

### Example 1: Debug a CrashLoopBackOff Pod

```bash
# Using kubectl-ai
kubectl ai "why is todo-backend in CrashLoopBackOff?"

# Expected response includes:
# - Pod events analysis
# - Recent logs
# - Resource constraints check
# - Suggested fixes
```

### Example 2: Optimize Resource Allocation

```bash
# Using kubectl-ai
kubectl ai "analyze resource usage in todo-app and suggest improvements"
```

### Example 3: Troubleshoot Networking

```bash
# Using kubectl-ai
kubectl ai "can todo-frontend reach todo-backend service?"

# Or debug DNS
kubectl ai "debug DNS resolution for todo-backend.todo-app.svc.cluster.local"
```

### Example 4: Image Optimization

```bash
# Using Docker AI (Gordon)
docker ai "analyze todo-frontend:latest and suggest size optimizations"

# Response typically includes:
# - Multi-stage build suggestions
# - Unnecessary dependencies
# - Layer optimization tips
```

---

## Tool Availability Matrix

| Tool | Version | Installation | API Key Required | Default LLM | Offline Support |
|------|---------|-------------|------------------|-------------|-----------------|
| kubectl-ai | v0.0.29 | krew | Yes (Gemini or OpenAI) | gemini-2.5-pro | With Ollama |
| Docker AI (Gordon) | v1.17.1 | Docker Desktop (built-in) | No (Docker-provided) | Docker-managed | No |
| kagent | v0.7.12 | Helm OCI chart | Yes (Gemini or OpenAI) | Configurable | No |

---

## Best Practices

1. **Start Simple**: Use AI tools for debugging and learning, not production automation
2. **Verify Commands**: Always review AI-generated kubectl commands before executing
3. **Security**: Don't share sensitive information (secrets, credentials) with AI tools
4. **Fallback**: Know the manual commands for when AI tools are unavailable
5. **Local Options**: Consider Ollama for offline kubectl-ai usage
6. **Resource Awareness**: kagent is resource-heavy; only deploy on clusters with sufficient memory

---

## Troubleshooting

### kubectl-ai not responding
```bash
# Check API key is set
echo $GEMINI_API_KEY

# Ensure krew PATH is set
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

# Try with a smaller model
kubectl ai --model gemini-2.0-flash "list pods"

# Check for quota errors (free tier limits)
# Error 429 means daily quota exceeded — wait or upgrade API plan
```

### Docker AI not available
- Ensure Docker Desktop v4.30+ is installed
- In WSL2: Gordon queries require the Desktop GUI running on Windows
- Run from PowerShell/CMD or Docker Desktop's terminal for full functionality
- `docker ai version` works from WSL2 (confirms installation)

### kagent pods failing
```bash
# Check pod status
kubectl get pods -n kagent

# View controller logs
kubectl logs -n kagent -l app.kubernetes.io/name=kagent

# Restart stuck pods
kubectl rollout restart deployment -n kagent --all

# If memory-constrained, scale down non-essential agents
kubectl scale deployment -n kagent cilium-debug-agent --replicas=0
kubectl scale deployment -n kagent istio-agent --replicas=0
```
