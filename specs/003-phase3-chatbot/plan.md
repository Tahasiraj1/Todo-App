# Implementation Plan: Phase III - AI-Powered Todo Chatbot

**Branch**: `003-phase3-chatbot` | **Date**: 2026-01-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-phase3-chatbot/spec.md`

## Summary

Phase III adds an AI-powered chat interface for managing todos through natural language. Users can create, view, update, complete, and delete tasks by conversing with an AI assistant. The implementation uses OpenAI Agents SDK with Google Gemini model for AI logic, MCP-style tools for task operations, and OpenAI ChatKit for the frontend UI. All conversation state is persisted to Neon PostgreSQL, maintaining the stateless server architecture from Phase II.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js 16+ (frontend)
**Primary Dependencies**: OpenAI Agents SDK (with LiteLLM), FastAPI, SQLModel, OpenAI ChatKit
**Storage**: Neon Serverless PostgreSQL (existing from Phase II)
**Testing**: pytest (backend), manual E2E testing
**Target Platform**: Web application (existing Phase II infrastructure)
**Project Type**: Web (monorepo with frontend/ and backend/)
**Performance Goals**: Chat response < 3s, tool execution < 2s
**Constraints**: Stateless server architecture, user data isolation
**Scale/Scope**: Same user base as Phase II, conversation history up to 100 messages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Spec exists at spec.md, plan follows workflow |
| II. AI-Native Implementation | ✅ PASS | All code to be generated via Claude Code |
| III. Progressive Architecture | ✅ PASS | Phase III builds on Phase II, not skipping |
| IV. Stateless Service Architecture | ✅ PASS | Conversations stored in DB, no in-memory state |
| V. Technology Stack Compliance | ✅ PASS | Using specified stack: OpenAI ChatKit, Agents SDK, MCP, FastAPI, SQLModel, Neon |
| VII. Independent Feature Testability | ✅ PASS | Chat features independently testable |
| VIII. Clean Code & Project Structure | ✅ PASS | Monorepo structure maintained |

**Gate Result**: ✅ ALL GATES PASS - Proceed to implementation

## Project Structure

### Documentation (this feature)

```text
specs/003-phase3-chatbot/
├── plan.md              # This file
├── spec.md              # Feature requirements
├── research.md          # Technology research findings
├── data-model.md        # Database entities
├── quickstart.md        # Developer setup guide
├── contracts/
│   ├── chat-api.md      # Chat API contract
│   ├── mcp-tools.md     # MCP tool definitions
│   └── openapi.yaml     # OpenAPI specification
├── checklists/
│   └── requirements.md  # Requirements checklist
└── tasks.md             # Implementation tasks (from /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py      # Update: include chat router
│   │       ├── tasks.py         # Existing
│   │       └── chat.py          # NEW: Chat endpoints
│   ├── models/
│   │   ├── __init__.py          # Update: export new models
│   │   ├── task.py              # Existing
│   │   ├── conversation.py      # NEW: Conversation SQLModel
│   │   ├── message.py           # NEW: Message SQLModel
│   │   └── schemas.py           # Update: add chat schemas
│   ├── services/
│   │   ├── __init__.py          # Update: export new services
│   │   ├── task_service.py      # Existing (reused by tools)
│   │   ├── chat_service.py      # NEW: Chat orchestration
│   │   └── conversation_service.py  # NEW: Conversation CRUD
│   ├── agent/
│   │   ├── __init__.py          # NEW
│   │   ├── agent.py             # NEW: Agent configuration
│   │   └── tools.py             # NEW: MCP tool functions
│   ├── middleware/              # Existing (auth reused)
│   └── main.py                  # Update: include chat routes
├── migrations/
│   └── 003_phase3_chat_schema.sql  # NEW: Schema migration
├── requirements.txt             # Update: add new dependencies
└── tests/
    └── test_chat.py             # NEW: Chat endpoint tests

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Update: add chat navigation
│   │   ├── dashboard/
│   │   │   └── page.tsx         # Existing
│   │   └── chat/
│   │       ├── page.tsx         # NEW: Chat page
│   │       └── layout.tsx       # NEW: Chat layout (optional)
│   ├── components/
│   │   ├── tasks/               # Existing
│   │   └── chat/
│   │       ├── chat-interface.tsx   # NEW: Main chat component
│   │       ├── message-list.tsx     # NEW: Message display
│   │       ├── chat-input.tsx       # NEW: Input with send
│   │       └── typing-indicator.tsx # NEW: Processing indicator
│   └── lib/
│       ├── api.ts               # Existing
│       └── chat-api.ts          # NEW: Chat API client
├── package.json                 # Update: add @openai/chatkit-js
└── next.config.ts               # Existing
```

**Structure Decision**: Extending the existing Phase II monorepo structure with new chat-related modules in both frontend and backend.

## Architecture Overview

### System Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                          Frontend (Next.js)                          │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    ChatKit Interface                            │ │
│  │  [Message List] ←──────────────────────────────────────────┐    │ │
│  │  [Input Box] ──→ POST /api/{user_id}/chat ──────────────┐ │    │ │
│  └──────────────────────────────────────────────────────────│─│────┘ │
└──────────────────────────────────────────────────────────────│─│──────┘
                                                               │ │
┌──────────────────────────────────────────────────────────────│─│──────┐
│                       Backend (FastAPI)                      │ │      │
│  ┌───────────────────────────────────────────────────────────│─│────┐ │
│  │  Chat Endpoint                                            │ │    │ │
│  │  1. Verify JWT ←── Authorization Header                   │ │    │ │
│  │  2. Load conversation history from DB                     │ │    │ │
│  │  3. Store user message                                    ▼ │    │ │
│  │  4. Run Agent ──────────────────────────────────────────────┤    │ │
│  │  5. Store assistant response                                │    │ │
│  │  6. Return response ────────────────────────────────────────┘    │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────────┐│
│  │  Agent (OpenAI Agents SDK + Gemini)                               ││
│  │  ┌─────────────────────────────────────────────────────────────┐  ││
│  │  │  Tools (MCP-style)                                          │  ││
│  │  │  • add_task(user_id, title, description?)                   │  ││
│  │  │  • list_tasks(user_id, status?)                             │  ││
│  │  │  • complete_task(user_id, task_id)                          │  ││
│  │  │  • delete_task(user_id, task_id)                            │  ││
│  │  │  • update_task(user_id, task_id, title?, description?)      │  ││
│  │  └──────────────────────────────────────────│──────────────────┘  ││
│  └──────────────────────────────────────────────│─────────────────────┘│
│                                                 │                      │
│  ┌──────────────────────────────────────────────│─────────────────────┐│
│  │  Services                                    ▼                     ││
│  │  TaskService (existing) ←── Tools call this                       ││
│  │  ConversationService (new) ←── Manages conversations              ││
│  └───────────────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────────────┘
                                      │
┌───────────────────────────────────────────────────────────────────────┐
│                    Neon PostgreSQL Database                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │    users     │  │    tasks     │  │conversations │                │
│  │  (existing)  │  │  (existing)  │  │    (new)     │                │
│  └──────────────┘  └──────────────┘  └──────────────┘                │
│                                      ┌──────────────┐                │
│                                      │   messages   │                │
│                                      │    (new)     │                │
│                                      └──────────────┘                │
└───────────────────────────────────────────────────────────────────────┘
```

### Request Flow (Stateless)

1. **User sends message** via ChatKit UI
2. **Frontend** POSTs to `/api/{user_id}/chat` with JWT token
3. **Backend** verifies JWT, matches user_id
4. **Chat Service** loads conversation history from DB
5. **Chat Service** stores user message immediately
6. **Agent** processes message with context, invokes tools as needed
7. **Tools** call TaskService (existing) for CRUD operations
8. **Chat Service** stores assistant response
9. **Response** returned to frontend (server state cleared)

## Implementation Phases

### Phase 1: Backend Infrastructure

**Objective**: Set up database models, services, and agent configuration

1. **Database Models**
   - Conversation model with SQLModel
   - Message model with SQLModel
   - Migration script for new tables

2. **Services**
   - ConversationService for CRUD operations
   - ChatService for orchestrating the flow

3. **Agent Setup**
   - Install openai-agents[litellm]
   - Configure agent with Gemini model
   - Define MCP tool functions

### Phase 2: Chat API Endpoints

**Objective**: Expose chat functionality via REST API

1. **Chat Endpoint** (`POST /api/{user_id}/chat`)
   - Request validation
   - JWT verification
   - Agent invocation
   - Response formatting

2. **Conversation Endpoints**
   - `GET /api/{user_id}/conversations` - List conversations
   - `GET /api/{user_id}/conversations/{id}` - Get conversation details
   - `DELETE /api/{user_id}/conversations/{id}` - Delete conversation

### Phase 3: Frontend Chat Interface

**Objective**: Build chat UI with OpenAI ChatKit

1. **Chat Page**
   - Protected route (requires auth)
   - ChatKit integration
   - Streaming response handling

2. **Chat Components**
   - Message list with user/assistant distinction
   - Input field with send functionality
   - Typing/processing indicator
   - Error state handling

3. **Navigation**
   - Add chat link to dashboard/layout
   - Conversation history sidebar (optional)

### Phase 4: Integration & Testing

**Objective**: End-to-end testing and refinement

1. **Backend Tests**
   - Tool function tests
   - Chat endpoint tests
   - Conversation persistence tests

2. **E2E Testing**
   - Full user flow testing
   - Error handling verification
   - Performance validation

## Key Design Decisions

### 1. Tool Implementation Approach

**Decision**: Use `@function_tool` decorator from OpenAI Agents SDK directly rather than a separate MCP server process.

**Rationale**:
- Simpler architecture (single process)
- No inter-process communication overhead
- Tools still follow MCP patterns for potential future extraction

### 2. Conversation Context Building

**Decision**: Load full conversation history (up to 100 messages) for each request.

**Rationale**:
- Enables coherent multi-turn conversations
- 100 message limit prevents excessive token usage
- Stateless server requires full context reload each request

### 3. Streaming vs. Non-Streaming

**Decision**: Start with non-streaming responses, add streaming as enhancement.

**Rationale**:
- Simpler initial implementation
- Streaming can be added later without API changes
- 3-second response time target achievable without streaming

## Dependencies

### Backend New Dependencies

```text
# requirements.txt additions
openai-agents[litellm]>=0.2.0
sse-starlette>=2.0.0
```

### Frontend New Dependencies

```json
{
  "@openai/chatkit-js": "^0.1.0"
}
```

## Environment Variables

### New Variables Required

```bash
# Backend
GEMINI_API_KEY=<google_ai_studio_api_key>
```

## Security Considerations

1. **Authentication**: All endpoints require valid JWT
2. **Authorization**: user_id in URL must match JWT claims
3. **Data Isolation**: All DB queries filter by user_id
4. **Input Validation**: Message length capped at 2000 chars
5. **Rate Limiting**: 60 requests/minute/user (implementation in future)

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Chat response time | < 3s | Time from send to full response |
| Tool execution | < 2s | Time for single tool call |
| Page load | < 3s | Time to interactive chat interface |
| Conversation restore | < 3s | Time to load 100 messages |

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gemini API rate limits | Medium | High | Implement retry logic, use paid tier if needed |
| ChatKit compatibility issues | Low | Medium | Fallback to custom chat UI if needed |
| Agent misinterpretation | Medium | Low | Improve prompts, add clarification handling |
| Database connection exhaustion | Low | High | Use connection pooling, async operations |

## Success Metrics

From spec.md Success Criteria:

- [ ] SC-001: Task creation via chat < 10s
- [ ] SC-002: Task listing via chat < 5s
- [ ] SC-003: 90% intent recognition accuracy
- [ ] SC-004: Conversation restore < 3s
- [ ] SC-005: UI responsive with 100 messages
- [ ] SC-006: Tool calls complete < 2s
- [ ] SC-007: Full context persistence across refreshes
- [ ] SC-008: No data loss on server restart
- [ ] SC-009: Clarification prompts for ambiguous input
- [ ] SC-010: 95% task operations succeed
- [ ] SC-011: ChatKit loads < 3s
- [ ] SC-012: Zero unauthorized data access

## Next Steps

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Implement in order: Backend Infrastructure → API → Frontend → Testing
3. Create ADRs for significant decisions if needed
4. Update spec.md Clarifications section as questions arise

---

**Generated by**: `/sp.plan`
**Constitution Version**: 1.0.0
