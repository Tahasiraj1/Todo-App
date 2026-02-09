# Implementation Plan: Phase 5 Testing Plan

**Branch**: `006-phase5-testing-plan` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-phase5-testing-plan/spec.md`

## Summary

Comprehensive testing of the Phase 5 cloud-deployed Todo application against the hackathon requirements. The plan uses Playwright MCP for automated browser testing against the live deployment at `https://todo.tahasiraj.com` (OKE via Cloudflare Tunnel) and kubectl for infrastructure verification. Produces a pass/fail test report and a 90-second demo video structure.

## Technical Context

**Language/Version**: TypeScript (Playwright MCP), Bash (kubectl commands)
**Primary Dependencies**: Playwright MCP (browser automation), kubectl (infrastructure), Helm (deployment)
**Storage**: N/A (testing only — reads from live deployment)
**Testing**: Playwright MCP for E2E browser tests, kubectl for infrastructure checks
**Target Platform**: WSL2 Linux (test runner) → OKE ARM64 cluster (test target)
**Project Type**: Testing/validation — no source code changes
**Performance Goals**: All tests complete within 15 minutes
**Constraints**: WSL DNS requires /etc/hosts entry; Cloudflare Tunnel may have latency; 90-second demo video limit
**Scale/Scope**: 33 test cases across 8 phases, covering all Phase 5 hackathon requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | Testing plan follows Specify → Plan → Tasks workflow |
| II. AI-Native Implementation | PASS | Tests executed via Claude Code + Playwright MCP |
| III. Progressive Architecture | PASS | Tests validate Phase 5 (builds on all prior phases) |
| IV. Stateless Architecture | N/A | Testing only — no service changes |
| V. Technology Stack Compliance | PASS | Uses Playwright, kubectl, Helm — appropriate for testing |
| VI. Event-Driven Architecture | PASS | Tests verify Kafka, Dapr, activity log, WebSocket |
| VII. Independent Feature Testability | PASS | Each test case is independently executable |
| VIII. Clean Code & Structure | PASS | Test artifacts organized in specs/006-phase5-testing-plan/ |

**Gate Result**: PASS — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/006-phase5-testing-plan/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Testing tool research & prior results
├── data-model.md        # Test case data model
├── quickstart.md        # How to execute the test plan
├── contracts/
│   └── test-report-schema.yaml   # Test report output format
├── checklists/
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Task breakdown (created by /sp.tasks)
```

### Source Code (repository root)

```text
# No source code changes — this is a testing/validation feature.
# Test execution happens via:

.playwright-mcp/          # Playwright MCP session artifacts (screenshots, logs)

# Infrastructure verification via kubectl commands against:
k8s/helm/todo-chatbot/    # Helm chart (read-only — verify deployed state)
```

**Structure Decision**: No new source code directories. All test artifacts are documentation in `specs/006-phase5-testing-plan/`. Test execution uses Playwright MCP (browser automation tool) and kubectl (CLI) — both are interactive tools, not test scripts.

## Architecture

### Test Execution Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                    WSL2 Test Runner                            │
│                                                               │
│  ┌─────────────────┐    ┌──────────────────────────────────┐ │
│  │  Claude Code     │    │  Playwright MCP                  │ │
│  │  (Orchestrator)  │───▶│  (Browser Automation)            │ │
│  │                  │    │  - Navigate, click, type          │ │
│  │                  │    │  - Snapshot DOM state              │ │
│  │                  │    │  - Take screenshots               │ │
│  │                  │    │  - Evaluate JavaScript             │ │
│  └────────┬─────────┘    └──────────────┬───────────────────┘ │
│           │                             │                     │
│           ▼                             ▼                     │
│  ┌─────────────────┐    ┌──────────────────────────────────┐ │
│  │  kubectl         │    │  Chromium Browser                 │ │
│  │  (Infra Checks)  │    │  → https://todo.tahasiraj.com    │ │
│  └─────────────────┘    └──────────────────────────────────┘ │
│           │                             │                     │
└───────────┼─────────────────────────────┼─────────────────────┘
            │                             │
            ▼                             ▼ (via Cloudflare Tunnel)
┌───────────────────────────────────────────────────────────────┐
│                    OKE Cluster (ARM64)                         │
│                                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐│
│  │ Frontend │ │ Backend  │ │ Notif.   │ │ Recurring Task   ││
│  │ + Dapr   │ │ + Dapr   │ │ + Dapr   │ │ + Dapr           ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘│
│  ┌──────────┐ ┌──────────┐                                   │
│  │ Kafka    │ │ Dapr     │                                   │
│  │ Cluster  │ │ System   │                                   │
│  └──────────┘ └──────────┘                                   │
└───────────────────────────────────────────────────────────────┘
```

### Test Phases Flow

```
Phase 1: Infrastructure ──► Phase 2: Auth ──► Phase 3: CRUD ──►
Phase 4: Intermediate ──► Phase 5: Advanced ──► Phase 6: Chatbot ──►
Phase 7: Event-Driven ──► Phase 8: Report & Demo
```

Each phase depends on the previous (sequential execution). If Phase 1 (infrastructure) fails, subsequent phases cannot run reliably.

## Test Strategy

### Previous Testing Baseline

A previous Playwright E2E validation (2026-02-02, documented in PHR `005-cloud-event-deployment/001`) achieved:
- 31/37 tests PASS, 6 SKIP (activity log backend 404), 0 FAIL
- Tested against localhost (Minikube), not cloud deployment
- Activity log 404 has since been fixed (commit `d708eac`)

A subsequent cloud testing session (2026-02-08, from conversation summary) achieved:
- 20 PASS, 1 NEEDS FIX (recurring task frequency validation)
- Tested against live `https://todo.tahasiraj.com`
- Frequency validation fix added to `task-form.tsx` but may not be deployed

### Current Testing Approach

1. **Tool**: Playwright MCP — interactive browser automation via Claude Code tool calls
2. **Target**: Live cloud deployment at `https://todo.tahasiraj.com`
3. **Authentication**: Sign in with existing credentials (email/password)
4. **Coverage**: All 33 test cases from spec, plus infrastructure checks
5. **Output**: Pass/fail table, screenshots, demo video structure
6. **Known Issues**: Frontend image may need rebuild for recurrence validation fix

### Test Data Strategy

- Use existing user account (avoid sign-up during testing)
- Create fresh test tasks during testing (prefix with "Test:" for easy cleanup)
- Clean up test data after testing (delete test tasks)

### Failure Handling

- If a test fails, record the failure, take a screenshot, and continue
- Do not retry failed tests automatically (manual investigation needed)
- If infrastructure check fails (Phase 1), abort and report

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cloudflare Tunnel down | All browser tests fail | Check tunnel status first; have port-forward fallback |
| Frontend image not rebuilt | Recurrence validation test fails | Note as known issue; test with workaround |
| WSL DNS failure | Cannot reach todo.tahasiraj.com | Verify /etc/hosts entry exists |
| Session expires mid-test | Tests fail with 401 | Re-authenticate if session drops |
| OKE pods restarting | Intermittent failures | Check pod stability in Phase 1 |

## Complexity Tracking

No complexity violations. This is a testing feature with no architecture changes.
