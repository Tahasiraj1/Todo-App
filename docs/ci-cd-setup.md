# CI/CD Setup Guide

**Task**: T071 | **Feature**: Phase V — CI/CD Pipeline (US9)

## Overview

The CI/CD pipeline runs via GitHub Actions on push to the `main` branch. It executes:

1. **Backend tests** (pytest)
2. **Frontend tests** (npm test)
3. **Multi-arch Docker build** (amd64 + arm64)
4. **Push to OCIR** (Oracle Container Registry)
5. **Helm deploy to OKE** (Oracle Kubernetes Engine)

Failed tests in stages 1-2 will block the deployment.

## Required GitHub Secrets

Configure these in **Settings → Secrets and variables → Actions**:

| Secret | Description | Example |
|--------|-------------|---------|
| `OCI_CLI_USER` | OCI user OCID | `ocid1.user.oc1..aaa...` |
| `OCI_CLI_TENANCY` | OCI tenancy OCID | `ocid1.tenancy.oc1..aaa...` |
| `OCI_CLI_FINGERPRINT` | API key fingerprint | `ab:cd:ef:12:34:...` |
| `OCI_CLI_KEY_CONTENT` | Private API key (PEM content) | `-----BEGIN RSA PRIVATE KEY-----\n...` |
| `OCI_CLI_REGION` | OCI region identifier | `us-ashburn-1` |
| `OKE_CLUSTER_OCID` | OKE cluster OCID | `ocid1.cluster.oc1..aaa...` |
| `OCIR_NAMESPACE` | Tenancy namespace for OCIR | `mytenancy` |
| `OCIR_USERNAME` | OCIR login username | `user@example.com` |
| `OCIR_TOKEN` | OCIR auth token | (generate in OCI Console → User Settings → Auth Tokens) |

## Generating OCI Credentials

### 1. API Signing Key

```bash
# Generate key pair
oci setup keys

# Upload public key to OCI Console → User Settings → API Keys
# Note the fingerprint displayed after upload
```

### 2. Auth Token for OCIR

1. Go to OCI Console → Identity → Users → your user
2. Click "Auth Tokens" → "Generate Token"
3. Copy the token value (shown only once)

### 3. Find OKE Cluster OCID

```bash
oci ce cluster list --compartment-id <compartment-ocid> --query 'data[].id'
```

## Pipeline Behavior

| Event | Stages Run |
|-------|------------|
| Push to `main` | Test → Build → Push → Deploy |
| Pull request to `main` | Test only (no build/deploy) |

## Monitoring Deployments

```bash
# Check GitHub Actions status
gh run list --workflow=deploy.yaml

# View deployment logs
gh run view <run-id> --log

# Verify deployment on cluster
kubectl get pods -n todo-app
kubectl rollout status deployment/todo-backend -n todo-app
```
