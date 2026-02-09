# Research: Phase 5 Testing Plan

**Feature**: 006-phase5-testing-plan
**Date**: 2026-02-09

---

## R1: Testing Tool Selection

**Decision**: Playwright MCP (Model Context Protocol integration)

**Rationale**: Playwright MCP is already configured in the project (`.playwright-mcp/` directory exists, `@playwright/test` is a frontend dev dependency). It provides browser automation via Claude Code tool calls — no separate test script needed. This matches the hackathon's AI-native development approach.

**Alternatives Considered**:

| Tool | Pros | Cons | Verdict |
|------|------|------|---------|
| Playwright MCP | Already available, interactive, AI-native | Not scriptable for CI/CD | Selected |
| Playwright test scripts | Repeatable, CI-friendly | Requires writing test files, not AI-native | Rejected for this iteration |
| Cypress | Good DX, visual testing | Not installed, separate ecosystem | Rejected |
| Manual browser testing | No setup needed | Not repeatable, no evidence | Rejected |

---

## R2: Infrastructure Verification Approach

**Decision**: kubectl CLI commands via Bash tool

**Rationale**: kubectl is already configured with OKE cluster credentials. Direct CLI commands provide authoritative pod/service status without additional tooling.

**Commands needed**:
- `kubectl get pods -n todo-app` — app pod status
- `kubectl get pods -n dapr-system` — Dapr system status
- `kubectl get kafka -n kafka` — Kafka cluster status
- `kubectl get kafkatopics -n kafka` — topic verification
- `kubectl get subscriptions -n todo-app` — Dapr subscription verification

---

## R3: Prior Test Results Analysis

**Decision**: Build on two previous testing sessions, not start from scratch.

**Session 1** (2026-02-02, localhost/Minikube):
- 31/37 PASS, 6 SKIP (activity log 404)
- Activity log 404 since fixed (commit `d708eac`)
- Tested: priorities, tags, search, filter, sort, due dates, recurring, edit, delete

**Session 2** (2026-02-08, cloud `todo.tahasiraj.com`):
- 20+ features tested, 1 needs fix (recurrence frequency validation)
- Fix exists in `task-form.tsx` but may not be in deployed Docker image
- Tested: auth, CRUD, priorities, tags, search, filter, sort, complete, edit, delete, chatbot, activity log, WebSocket

**Gap Analysis** (features needing re-test on cloud):
- Recurring task auto-creation (event-driven — needs Kafka/Dapr pipeline)
- Browser notifications (requires notification permission)
- Multi-tab real-time sync (needs two-tab validation)

---

## R4: Cloud Deployment Architecture

**Decision**: Test against existing OKE deployment via Cloudflare Tunnel.

**Architecture confirmed**:
- 2 ARM64 nodes (VM.Standard.A1.Flex, 2 OCPU + 12GB each)
- Cloudflare Tunnel routes: `/api/auth` → frontend, `/api` → backend, `*` → frontend
- JWKS fetched internally (`JWKS_INTERNAL_URL=http://todo-frontend:3000`)
- Neon PostgreSQL (external database)

**No changes needed** — test the existing deployment as-is.

---

## R5: Demo Video Structure

**Decision**: 90-second structured demo covering all Phase 5 features.

**Research**: Hackathon spec states "Judges will only watch the first 90 seconds" and requires:
1. Public GitHub Repo Link
2. Published App Link
3. Demo video link (under 90 seconds)
4. WhatsApp number

**Structure** (from previous session analysis):

| Time | Segment | Duration |
|------|---------|----------|
| 0:00 | Cloud infrastructure (OKE cluster, pods, Dapr, Kafka) | 15s |
| 0:15 | Sign in + Dashboard overview | 10s |
| 0:25 | Create task with priority + tags + due date | 15s |
| 0:40 | Search, filter, sort | 10s |
| 0:50 | Recurring task creation | 10s |
| 1:00 | AI Chatbot (natural language task creation) | 15s |
| 1:15 | Activity log + real-time sync | 10s |
| 1:25 | Closing (repo link, architecture diagram) | 5s |

---

## R6: Known Issues & Workarounds

| Issue | Status | Workaround |
|-------|--------|------------|
| Frontend recurrence validation not deployed | Fix in code, not in Docker image | Manually select frequency before submitting |
| CI/CD pipeline not set up | Out of scope for testing | Document as known gap |
| Notification service E2E | Requires waiting for reminder timing | Verify pod running, skip timing test |
| WSL DNS resolution | Fixed via /etc/hosts | Verify entry before testing |
