# Cloudflare Tunnel Setup for OKE

## Goal
Expose `todo.tahasiraj.com` publicly via Cloudflare Tunnel (free) to satisfy FR-024 and SC-007.

## Prerequisites
- App deployed and working on OKE (port-forward verified)
- Domain `tahasiraj.com` on Namecheap
- Free Cloudflare account

## Steps

### 1. Create Cloudflare Account
- Sign up at https://dash.cloudflare.com
- No need to move domain — just need the account for tunnels

### 2. Create a Tunnel
- Go to Cloudflare Dashboard → Zero Trust → Networks → Tunnels
- Create a tunnel, name: `todo-app-oke`
- Copy the tunnel token

### 3. Deploy cloudflared in OKE
```bash
kubectl create secret generic cloudflared-token \
  --from-literal=token=<tunnel-token> \
  --namespace todo-app

# Deploy cloudflared pod (manifest to be created)
# Routes traffic: todo.tahasiraj.com → todo-frontend:3000
# Routes traffic: api.tahasiraj.com or todo.tahasiraj.com/api → todo-backend:8000
```

### 4. Add CNAME on Namecheap
- Go to Namecheap → Domain → Advanced DNS
- Add record:
  - Type: `CNAME`
  - Host: `todo`
  - Value: `<tunnel-id>.cfargotunnel.com`
  - TTL: Automatic

### 5. Verify
- Open `https://todo.tahasiraj.com` in browser
- Should load the app with HTTPS (Cloudflare provides free SSL)

## Notes
- Portfolio at `tahasiraj.com` is unaffected — only `todo` subdomain is routed
- Zero cost — Cloudflare Tunnels are free
- Works with private OKE nodes — no Load Balancer needed
- Estimated setup time: ~10-15 minutes
