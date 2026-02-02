# Ingress, DNS, and TLS — Making Your App Public

**Context**: This guide picks up where the cloud-native stack guide left off. You have a working Kubernetes deployment with Services of type `ClusterIP`/`NodePort`. The app is only accessible locally. This guide covers what it takes to make it publicly accessible with a domain name and HTTPS.

**Prerequisites**: Understanding of Pods, Deployments, and Services from `docs/cloud-native-stack-guide.md`.

---

## The Problem

Right now the app looks like this:

```
Internet  ──X──  Can't reach anything

Your Machine  ──→  minikube ip  ──→  NodePort 30080  ──→  todo-frontend pod
                                 ──→  NodePort 30081  ──→  todo-backend pod
```

Every service has its own port number. No domain names. No HTTPS. Only accessible from your machine.

What you want:

```
User types: https://todo.example.com        →  frontend
            https://todo.example.com/api    →  backend
```

One domain. HTTPS. Clean paths. Multiple services behind one entry point.

Three things need to happen: **Ingress** (routing), **DNS** (domain name), **TLS** (encryption).

---

## Part 1: Ingress

### What It Is

An Ingress is a Kubernetes resource that defines routing rules: "When traffic arrives at this domain and path, send it to this service."

### The Two Pieces

Ingress has two parts that are easy to confuse:

| Piece | What it is | Analogy |
|-------|-----------|---------|
| **Ingress resource** | A YAML file with routing rules | A menu (says what's available) |
| **Ingress Controller** | A pod that reads the rules and routes traffic | The waiter (actually serves the food) |

An Ingress resource without a controller does nothing. It's a declaration with nobody listening.

### Ingress Resource

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  namespace: todo-app
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: todo.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: todo-frontend
                port:
                  number: 3000
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: todo-backend
                port:
                  number: 8000
```

This says:
- `todo.example.com/` → forward to `todo-frontend` service on port 3000
- `todo.example.com/api` → forward to `todo-backend` service on port 8000

### Ingress Controller

The most common controller is **NGINX Ingress Controller** — a pod running NGINX that watches for Ingress resources and reconfigures itself automatically.

```bash
# On Minikube (simplest)
minikube addons enable ingress

# On a real cluster (via Helm)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

When installed, the controller creates a LoadBalancer service. On cloud providers (AWS, GCP, Azure), this automatically gets a public IP address. On Minikube, you use `minikube tunnel` to simulate a LoadBalancer.

### How Traffic Flows With Ingress

```
Internet
    │
    ▼
┌──────────────────────┐
│  Load Balancer       │   ← Cloud provider assigns a public IP (e.g., 34.56.78.90)
│  (external)          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Ingress Controller  │   ← NGINX pod inside your cluster
│  (reads Ingress      │   ← Matches host + path to service
│   resources)         │
└──────────┬───────────┘
           │
      ┌────┴─────┐
      ▼          ▼
  frontend    backend         ← ClusterIP services (no NodePort needed)
  service     service
      │          │
      ▼          ▼
  frontend    backend
  pods        pods
```

Key insight: With Ingress, your services can be `ClusterIP` (internal only). The Ingress Controller is the only thing that needs external access. Everything else stays private inside the cluster.

### Without Ingress vs. With Ingress

```
Without Ingress:
  http://34.56.78.90:30080   →  frontend
  http://34.56.78.90:30081   →  backend
  (ugly ports, no domain, no HTTPS)

With Ingress:
  https://todo.example.com       →  frontend
  https://todo.example.com/api   →  backend
  (clean URLs, one entry point)
```

### Path-Based vs. Host-Based Routing

Ingress supports two routing strategies:

**Path-based** (what we'd use): One domain, different paths.

```yaml
rules:
  - host: todo.example.com
    http:
      paths:
        - path: /         →  frontend
        - path: /api      →  backend
```

**Host-based**: Different subdomains for different services.

```yaml
rules:
  - host: todo.example.com
    http:
      paths:
        - path: /         →  frontend
  - host: api.todo.example.com
    http:
      paths:
        - path: /         →  backend
```

Both are valid. Path-based is simpler for small apps. Host-based is cleaner when services have completely separate concerns.

### Other Ingress Controllers

NGINX is the most common, but alternatives exist:

| Controller | When to use |
|-----------|-------------|
| **NGINX** | Default choice. Stable, well-documented, covers 90% of use cases. |
| **Traefik** | Auto-discovers services. Popular with smaller clusters and k3s. |
| **HAProxy** | High-performance TCP/HTTP load balancing. |
| **AWS ALB Controller** | On AWS, uses native Application Load Balancers instead of NGINX pods. |
| **Istio Gateway** | Part of the Istio service mesh. For advanced traffic management. |

For learning and most production use cases, NGINX is the standard.

---

## Part 2: DNS

### What It Is

DNS (Domain Name System) translates human-readable names into IP addresses.

```
todo.example.com  →  DNS lookup  →  34.56.78.90
```

Your browser doesn't know what `todo.example.com` means. It asks a DNS resolver, which looks up the IP address, and then connects to that IP.

### What You Need to Do

1. **Own a domain** — buy from a registrar (Namecheap, Cloudflare, Google Domains, etc.)
2. **Get your cluster's external IP** — from the Ingress Controller's LoadBalancer service
3. **Create a DNS record** — point the domain to the IP

```bash
# Get the external IP of your Ingress Controller
kubectl get service -n ingress-nginx ingress-nginx-controller

# Output:
# NAME                       TYPE           EXTERNAL-IP    PORT(S)
# ingress-nginx-controller   LoadBalancer   34.56.78.90    80:31080/TCP,443:31443/TCP
```

Then at your DNS provider, create a record:

```
Type    Name                  Value           TTL
A       todo.example.com      34.56.78.90     300
```

That's it. DNS itself is straightforward — one record mapping your domain to your cluster's IP.

### DNS Record Types

| Type | What it does | Example |
|------|-------------|---------|
| **A** | Maps domain to IPv4 address | `todo.example.com → 34.56.78.90` |
| **AAAA** | Maps domain to IPv6 address | `todo.example.com → 2001:db8::1` |
| **CNAME** | Maps domain to another domain | `www.todo.example.com → todo.example.com` |

For Kubernetes, you typically create an **A record** pointing to the LoadBalancer IP.

On AWS, the LoadBalancer gets a hostname (not an IP), so you'd use a **CNAME** instead:

```
Type     Name                  Value
CNAME    todo.example.com      abc123.elb.amazonaws.com
```

### DNS Propagation

After creating a DNS record, it takes time for the change to spread across the internet. This is called **propagation**. Typically 5 minutes to 48 hours depending on TTL (Time To Live) settings.

```
TTL: 300  = DNS resolvers cache the result for 5 minutes
TTL: 3600 = Cached for 1 hour
TTL: 86400 = Cached for 24 hours
```

Lower TTL = faster updates but more DNS lookups (slightly slower for users).

### ExternalDNS (Automation)

On real clusters, you can automate DNS record creation with **ExternalDNS** — a Kubernetes controller that watches Ingress resources and creates DNS records automatically.

```bash
helm install external-dns bitnami/external-dns \
  --set provider=cloudflare \
  --set cloudflare.apiToken=<token>
```

With ExternalDNS, creating an Ingress with `host: todo.example.com` automatically creates the DNS record. No manual step needed.

---

## Part 3: TLS (HTTPS)

### What It Is

TLS (Transport Layer Security) encrypts traffic between the user's browser and your server. Without it, anyone on the network can read the data in transit — passwords, API keys, personal data.

HTTPS = HTTP + TLS.

### How TLS Works (Simplified)

```
Browser                                    Server
   │                                          │
   ├── "I want to connect securely" ────────→ │
   │                                          │
   │ ←── Server sends its certificate ──────── │
   │     (proves identity, contains           │
   │      public key)                         │
   │                                          │
   ├── Browser verifies certificate ────────→ │
   │   (checks against trusted CAs)          │
   │                                          │
   │ ←── Both agree on encryption key ──────── │
   │                                          │
   ├══ Encrypted traffic flows both ways ════╡
```

The certificate is the critical piece. It proves that the server is really `todo.example.com` and not an impersonator.

### Certificates — Where They Come From

A certificate must be issued by a **Certificate Authority (CA)** — a trusted third party.

| Option | Cost | Automation |
|--------|------|-----------|
| **Let's Encrypt** | Free | Fully automated via cert-manager |
| **Commercial CAs** (DigiCert, Sectigo) | $10-500/year | Manual or semi-automated |
| **Self-signed** | Free | No trust (browsers show warnings) |

**Let's Encrypt** is the standard for Kubernetes. It's free, automated, and trusted by all browsers.

### cert-manager — Automated Certificates in Kubernetes

cert-manager is a Kubernetes controller that:
1. Watches for Ingress resources that request TLS
2. Contacts Let's Encrypt
3. Proves you own the domain (via a challenge)
4. Gets a certificate
5. Stores it as a Kubernetes Secret
6. Renews it automatically before expiry

```bash
# Install cert-manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true
```

### Step 1: Create a ClusterIssuer

A ClusterIssuer tells cert-manager how to get certificates. You create it once for the entire cluster.

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: you@example.com           # Let's Encrypt sends expiry warnings here
    privateKeySecretRef:
      name: letsencrypt-prod-key     # Stores the account private key
    solvers:
      - http01:
          ingress:
            class: nginx             # Uses the NGINX Ingress Controller for challenges
```

There are two types of challenge solvers:

| Solver | How it works | When to use |
|--------|-------------|-------------|
| **HTTP-01** | Let's Encrypt requests a file at `http://yourdomain/.well-known/acme-challenge/...`. cert-manager creates a temporary Ingress to serve it. | Default. Works when your cluster is publicly accessible on port 80. |
| **DNS-01** | cert-manager creates a TXT record in your DNS. Let's Encrypt verifies it. | When port 80 isn't available, or for wildcard certificates (`*.example.com`). |

### Step 2: Add TLS to Your Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  namespace: todo-app
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"    # ← Triggers cert-manager
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - todo.example.com
      secretName: todo-tls-cert      # ← cert-manager creates this Secret automatically
  rules:
    - host: todo.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: todo-frontend
                port:
                  number: 3000
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: todo-backend
                port:
                  number: 8000
```

### What Happens Automatically

```
1. You apply the Ingress with the cert-manager annotation
2. cert-manager sees it, creates a Certificate resource
3. cert-manager contacts Let's Encrypt: "I need a cert for todo.example.com"
4. Let's Encrypt says: "Prove you own the domain. Serve this token at this URL."
5. cert-manager creates a temporary pod/ingress to serve the challenge
6. Let's Encrypt verifies the challenge
7. Let's Encrypt issues the certificate
8. cert-manager stores it in the Secret "todo-tls-cert"
9. NGINX Ingress Controller picks up the Secret and configures TLS
10. HTTPS works.
11. 30 days before expiry, cert-manager renews automatically
```

You configure it once. Certificates are managed forever after.

### Verifying TLS

```bash
# Check certificate status
kubectl get certificate -n todo-app

# Output:
# NAME            READY   SECRET          AGE
# todo-tls-cert   True    todo-tls-cert   5m

# Describe for details
kubectl describe certificate todo-tls-cert -n todo-app

# Check the actual certificate
kubectl get secret todo-tls-cert -n todo-app -o jsonpath='{.data.tls\.crt}' | \
  base64 -d | openssl x509 -text -noout | head -20
```

### TLS Termination

An important concept: **where does decryption happen?**

```
Browser  ═══TLS═══→  Ingress Controller  ───plain HTTP──→  Service  ──→  Pod
                     (decrypts here)
```

This is called **TLS termination at the Ingress**. Traffic is encrypted between the user and the Ingress Controller. Inside the cluster, traffic is plain HTTP. This is the default and is fine for most applications because the internal cluster network is trusted.

For high-security environments, you can also do **end-to-end TLS** (encrypted all the way to the pod), but that adds complexity and is rarely needed for internal traffic.

---

## The Complete Flow

After setting up all three pieces:

```
User types: https://todo.example.com
                │
                ▼
DNS Resolver (Cloudflare, Google)
                │
                ▼
Looks up A record: todo.example.com → 34.56.78.90
                │
                ▼
Browser connects to 34.56.78.90:443 (HTTPS)
                │
                ▼
Load Balancer (cloud provider)
                │
                ▼
NGINX Ingress Controller
  ├── Terminates TLS (cert from cert-manager / Let's Encrypt)
  ├── Reads Ingress rules
  ├── path: /     → todo-frontend service → frontend pods
  └── path: /api  → todo-backend service  → backend pods
```

### Before and After

```
Before (our Phase 4):
  http://192.168.49.2:30080    ← ugly IP, port number, HTTP only, local only
  http://192.168.49.2:30081

After (Ingress + DNS + TLS):
  https://todo.example.com     ← clean domain, HTTPS, public, one entry point
  https://todo.example.com/api
```

---

## Trying It on Minikube

You can practice this locally without a real domain.

### Step 1: Enable Ingress Addon

```bash
minikube addons enable ingress
```

### Step 2: Create an Ingress Resource

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  namespace: todo-app
spec:
  ingressClassName: nginx
  rules:
    - host: todo.local            # Fake domain for local testing
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: todo-frontend
                port:
                  number: 3000
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: todo-backend
                port:
                  number: 8000
```

### Step 3: Map the Fake Domain to Minikube IP

```bash
# Get Minikube IP
minikube ip
# 192.168.49.2

# Add to /etc/hosts (Linux/macOS) or C:\Windows\System32\drivers\etc\hosts (Windows)
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
```

### Step 4: Access

```bash
curl http://todo.local
# Routes to frontend

curl http://todo.local/api/health
# Routes to backend
```

No TLS in this local setup (cert-manager needs a real domain for Let's Encrypt), but the routing works identically.

---

## Key Commands Reference

```bash
# Ingress
minikube addons enable ingress                    # Enable on Minikube
kubectl get ingress -n todo-app                   # List Ingress resources
kubectl describe ingress todo-ingress -n todo-app # Detailed routing info

# DNS
nslookup todo.example.com                        # Check DNS resolution
dig todo.example.com                             # Detailed DNS lookup

# TLS / cert-manager
kubectl get certificate -n todo-app              # Check certificate status
kubectl describe certificate <name> -n todo-app  # Certificate details
kubectl get clusterissuer                        # Check issuer status
kubectl logs -n cert-manager -l app=cert-manager # cert-manager logs
```

---

## Summary

| Component | What it does | Tool we'd use |
|-----------|-------------|--------------|
| **Ingress Controller** | Routes external HTTP traffic into the cluster by domain and path | NGINX Ingress Controller |
| **Ingress Resource** | Declares which domain/path maps to which service | Kubernetes YAML |
| **DNS** | Maps a domain name to the cluster's external IP | Domain registrar (Namecheap, Cloudflare) |
| **cert-manager** | Automates TLS certificate issuance and renewal | Helm chart + ClusterIssuer |
| **Let's Encrypt** | Free Certificate Authority | Used by cert-manager automatically |

Together these three layers turn a cluster-internal app into a publicly accessible, encrypted web application with clean URLs.
