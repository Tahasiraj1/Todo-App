# Data Model: Phase 5 Testing Plan

**Feature**: 006-phase5-testing-plan
**Date**: 2026-02-09

---

## Entities

### Test Case

Represents a single verifiable check in the test plan.

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier (e.g., "TC-01") |
| phase | integer | Test execution phase (1-8) |
| category | string | Feature area (e.g., "CRUD", "Search/Filter", "Chatbot") |
| description | string | What is being tested |
| steps | list[string] | Ordered steps to execute |
| expected_result | string | What should happen |
| actual_result | string | What actually happened (filled during execution) |
| status | enum | PASS, FAIL, SKIP, BLOCKED |
| hackathon_ref | string | Hackathon spec requirement reference (e.g., "Phase V Part A: Priorities") |
| screenshot | string | Path to screenshot file (if captured) |
| notes | string | Additional observations |

### Test Phase

Groups test cases into sequential execution phases.

| Field | Type | Description |
|-------|------|-------------|
| number | integer | Phase number (1-8) |
| name | string | Phase name (e.g., "Infrastructure Verification") |
| tool | string | Primary tool used (e.g., "kubectl", "Playwright MCP") |
| prerequisite | string | What must be true before this phase runs |
| test_cases | list[TestCase] | Test cases in this phase |

### Test Report

The final output summarizing all test results.

| Field | Type | Description |
|-------|------|-------------|
| date | datetime | When tests were executed |
| target_url | string | Application URL tested (e.g., "https://todo.tahasiraj.com") |
| total_tests | integer | Total number of test cases |
| passed | integer | Count of PASS results |
| failed | integer | Count of FAIL results |
| skipped | integer | Count of SKIP results |
| blocked | integer | Count of BLOCKED results |
| phases | list[TestPhase] | All test phases with results |
| screenshots | list[string] | Paths to captured screenshots |
| demo_structure | DemoStructure | 90-second demo video plan |

### Demo Structure

Plan for the 90-second hackathon demo video.

| Field | Type | Description |
|-------|------|-------------|
| total_duration | integer | Total seconds (max 90) |
| segments | list[DemoSegment] | Ordered segments |

### Demo Segment

A timed section of the demo video.

| Field | Type | Description |
|-------|------|-------------|
| start_time | integer | Start time in seconds |
| duration | integer | Duration in seconds |
| title | string | Segment title |
| features_shown | list[string] | Features demonstrated |
| script | string | What to show/say |

---

## Relationships

```
TestReport 1──* TestPhase 1──* TestCase
TestReport 1──1 DemoStructure 1──* DemoSegment
```

---

## Test Case Catalog

### Phase 1: Infrastructure Verification (kubectl)

| ID | Description | Hackathon Ref |
|----|-------------|---------------|
| TC-01 | All app pods in Running state | Phase V Part C: Cloud Deployment |
| TC-02 | Dapr system pods running | Phase V Part B: Dapr |
| TC-03 | Kafka cluster Ready | Phase V Part A: Kafka |
| TC-04 | Kafka topics exist (task-events, reminders) | Phase V: Kafka Topics |

### Phase 2: Authentication (Playwright)

| ID | Description | Hackathon Ref |
|----|-------------|---------------|
| TC-05 | Navigate to app URL | Phase II: Web App |
| TC-06 | Sign in with valid credentials | Phase II: Authentication |
| TC-07 | Dashboard loads with tasks | Phase II: View Tasks |
| TC-08 | Session persists after refresh | Phase II: Authentication |

### Phase 3: Core CRUD (Playwright)

| ID | Description | Hackathon Ref |
|----|-------------|---------------|
| TC-09 | Create task with title + description | Phase II: Add Task |
| TC-10 | Task appears in list | Phase II: View Tasks |
| TC-11 | Edit task title | Phase II: Update Task |
| TC-12 | Mark task complete | Phase II: Mark Complete |
| TC-13 | Delete task with confirmation | Phase II: Delete Task |

### Phase 4: Intermediate Features (Playwright)

| ID | Description | Hackathon Ref |
|----|-------------|---------------|
| TC-14 | Create task with HIGH priority | Phase V Part A: Priorities |
| TC-15 | Create task with tags | Phase V Part A: Tags |
| TC-16 | Search by keyword | Phase V Part A: Search |
| TC-17 | Filter by HIGH priority | Phase V Part A: Filter |
| TC-18 | Filter by tag | Phase V Part A: Filter |
| TC-19 | Clear filters | Phase V Part A: Filter |
| TC-20 | Sort by priority | Phase V Part A: Sort |

### Phase 5: Advanced Features (Playwright)

| ID | Description | Hackathon Ref |
|----|-------------|---------------|
| TC-21 | Create task with due date | Phase V Part A: Due Dates |
| TC-22 | Verify overdue display | Phase V Part A: Due Dates |
| TC-23 | Create recurring task with frequency | Phase V Part A: Recurring Tasks |
| TC-24 | Recurring without frequency shows error | Phase V Part A: Recurring Tasks |

### Phase 6: AI Chatbot (Playwright)

| ID | Description | Hackathon Ref |
|----|-------------|---------------|
| TC-25 | Navigate to chat tab | Phase III: AI Chatbot |
| TC-26 | Create task via natural language | Phase III: Natural Language Commands |
| TC-27 | Chatbot confirms creation | Phase III: Agent Behavior |
| TC-28 | Chatbot task visible on dashboard | Phase III: Deliverables |

### Phase 7: Event-Driven Features (Playwright)

| ID | Description | Hackathon Ref |
|----|-------------|---------------|
| TC-29 | Activity log shows entries | Phase V Part A: Activity Log |
| TC-30 | WebSocket connection established | Phase V Part A: Real-Time Sync |

### Phase 8: Report & Demo

| ID | Description | Hackathon Ref |
|----|-------------|---------------|
| TC-31 | Final dashboard screenshot | Submission: Demo Video |
| TC-32 | Test report table compiled | Submission: Deliverables |
| TC-33 | Demo video structure created | Submission: Demo Video (90s) |
