# Tasks: Phase III - AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/003-phase3-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the spec. Manual E2E testing is sufficient per plan.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- This is a monorepo with separate frontend (Next.js) and backend (FastAPI)

## User Stories Summary

| ID | Story | Priority | Description |
|----|-------|----------|-------------|
| US1 | Natural Language Task Creation | P1 | Create tasks via chat |
| US2 | Natural Language Task Listing | P1 | View tasks via chat |
| US3 | Natural Language Task Completion | P2 | Complete tasks via chat |
| US4 | Natural Language Task Deletion | P2 | Delete tasks via chat |
| US5 | Natural Language Task Update | P2 | Update tasks via chat |
| US6 | Conversation Persistence | P1 | Save/restore chat history |
| US7 | ChatKit User Interface | P1 | Modern chat UI |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency configuration

- [x] T001 Update backend/pyproject.toml with new dependencies (openai-agents[litellm], sse-starlette)
- [x] T002 [P] Create database migration file backend/migrations/003_phase3_chat_schema.sql
- [ ] T003 [P] Run migration to create conversations and messages tables
- [x] T004 [P] Update frontend/package.json - ChatKit unavailable, using custom chat UI instead
- [x] T005 Install frontend dependencies with npm install

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models

- [x] T006 [P] Create Conversation model in backend/src/models/conversation.py (SQLModel with id, user_id, created_at, updated_at)
- [x] T007 [P] Create Message model in backend/src/models/message.py (SQLModel with id, user_id, conversation_id, role, content, created_at)
- [x] T008 Update backend/src/models/__init__.py to export Conversation and Message models
- [x] T009 Add chat-related Pydantic schemas in backend/src/models/schemas.py (ChatRequest, ChatResponse, ToolCall, ConversationSummary)

### Services

- [x] T010 Create ConversationService in backend/src/services/conversation_service.py (create, get, list, delete, add_message, get_messages)
- [x] T011 Update backend/src/services/__init__.py to export ConversationService

### Agent Infrastructure

- [x] T012 Create backend/src/agent/__init__.py (module initialization)
- [x] T013 [P] Create add_task tool function in backend/src/agent/tools.py using @function_tool decorator
- [x] T014 [P] Create list_tasks tool function in backend/src/agent/tools.py using @function_tool decorator
- [x] T015 [P] Create complete_task tool function in backend/src/agent/tools.py using @function_tool decorator
- [x] T016 [P] Create delete_task tool function in backend/src/agent/tools.py using @function_tool decorator
- [x] T017 [P] Create update_task tool function in backend/src/agent/tools.py using @function_tool decorator
- [x] T018 Create TodoAssistant agent configuration in backend/src/agent/agent.py with LitellmModel for Gemini

### Chat Service

- [x] T019 Create ChatService in backend/src/services/chat_service.py (process_message method that orchestrates agent and conversation)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 6 - Conversation Persistence (Priority: P1) 🎯 MVP Foundation

**Goal**: Store and retrieve conversation history from database

**Independent Test**: Have a conversation, refresh the page, verify history is restored

**Why First**: This is foundational for all chat functionality - messages must persist before any chat feature works

### Implementation for User Story 6

- [x] T020 [US6] Create chat API router in backend/src/api/routes/chat.py with initial structure
- [x] T021 [US6] Implement GET /api/{user_id}/conversations endpoint in backend/src/api/routes/chat.py
- [x] T022 [US6] Implement GET /api/{user_id}/conversations/{conversation_id} endpoint in backend/src/api/routes/chat.py
- [x] T023 [US6] Implement DELETE /api/{user_id}/conversations/{conversation_id} endpoint in backend/src/api/routes/chat.py
- [x] T024 [US6] Update backend/src/api/routes/__init__.py to include chat router
- [x] T025 [US6] Update backend/src/main.py to register chat routes at /api prefix (routes already included)
- [x] T026 [US6] Add JWT verification and user_id matching to all chat endpoints

**Checkpoint**: Conversation CRUD endpoints working, messages persist to database

---

## Phase 4: User Story 1 & 2 - Task Creation and Listing (Priority: P1) 🎯 MVP Core

**Goal**: Create and list tasks through natural language chat

**Independent Test**: Send "Add a task to buy groceries" → task created; Send "Show my tasks" → tasks displayed

**Why Combined**: These form the core chat-to-task loop and share the chat endpoint

### Implementation for User Stories 1 & 2

- [x] T027 [US1][US2] Implement POST /api/{user_id}/chat endpoint in backend/src/api/routes/chat.py
- [x] T028 [US1][US2] Wire ChatService.process_message to handle chat requests
- [x] T029 [US1][US2] Implement conversation history loading in ChatService (fetch last 100 messages)
- [x] T030 [US1][US2] Implement message persistence in ChatService (store user message before processing, store assistant response after)
- [x] T031 [US1][US2] Configure agent instructions for task intent recognition (add, list patterns)
- [x] T032 [US1][US2] Handle agent response formatting (include tool_calls in response)
- [x] T033 [US1][US2] Add error handling for agent failures (return user-friendly messages)

**Checkpoint**: Can create and list tasks via chat; conversations persist

---

## Phase 5: User Story 7 - ChatKit User Interface (Priority: P1) 🎯 MVP UI

**Goal**: Modern chat interface with ChatKit components

**Independent Test**: Access /chat page, send messages, see typing indicator, view message bubbles

### Implementation for User Story 7

- [x] T034 [P] [US7] Create frontend/src/lib/chat-api.ts with sendMessage, getConversations, getConversation, deleteConversation functions
- [x] T035 [P] [US7] Create frontend/src/components/chat/typing-indicator.tsx component
- [x] T036 [P] [US7] Create frontend/src/components/chat/message-list.tsx component with user/assistant message styling
- [x] T037 [P] [US7] Create frontend/src/components/chat/chat-input.tsx component with send button
- [x] T038 [US7] Create frontend/src/components/chat/chat-interface.tsx main chat component (combines all)
- [x] T039 [US7] Create frontend/src/app/chat/page.tsx protected page with custom chat UI (ChatKit unavailable)
- [x] T040 [US7] Add chat navigation link to frontend/src/app/dashboard/page.tsx
- [x] T041 [US7] Implement conversation loading on page mount (restore history)
- [x] T042 [US7] Implement new conversation creation flow
- [x] T043 [US7] Add loading and error states to chat interface

**Checkpoint**: Full chat UI working with task creation and listing

---

## Phase 6: User Story 3 - Task Completion (Priority: P2)

**Goal**: Mark tasks as complete through natural language

**Independent Test**: Have a task, say "Mark task 3 as complete", verify task status changes

### Implementation for User Story 3

- [x] T044 [US3] Ensure complete_task tool properly calls TaskService.toggle_task_completion
- [x] T045 [US3] Update agent instructions to recognize completion intent patterns ("done", "complete", "finished")
- [x] T046 [US3] Handle task-not-found errors gracefully in complete_task tool
- [ ] T047 [US3] Test completion by task ID and by task title matching

**Checkpoint**: Task completion via chat working

---

## Phase 7: User Story 4 - Task Deletion (Priority: P2)

**Goal**: Delete tasks through natural language

**Independent Test**: Have a task, say "Delete task 2", verify task is removed

### Implementation for User Story 4

- [x] T048 [US4] Ensure delete_task tool properly calls TaskService.delete_task
- [x] T049 [US4] Update agent instructions to recognize deletion intent patterns ("delete", "remove", "cancel")
- [x] T050 [US4] Handle task-not-found errors gracefully in delete_task tool
- [ ] T051 [US4] Test deletion by task ID and by task title matching

**Checkpoint**: Task deletion via chat working

---

## Phase 8: User Story 5 - Task Update (Priority: P2)

**Goal**: Update task details through natural language

**Independent Test**: Have a task, say "Change task 1 to 'Buy groceries and fruits'", verify update

### Implementation for User Story 5

- [x] T052 [US5] Ensure update_task tool properly calls TaskService.update_task
- [x] T053 [US5] Update agent instructions to recognize update intent patterns ("change", "update", "rename", "add description")
- [x] T054 [US5] Handle validation errors (empty title, no updates provided)
- [ ] T055 [US5] Test update by task ID and by task title matching

**Checkpoint**: Task update via chat working - Full CRUD complete

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T056 [P] Add structured logging for all chat operations in ChatService
- [x] T057 [P] Add structured logging for all MCP tool invocations in tools.py
- [x] T058 Add input validation for message length (max 2000 chars) in chat endpoint (via ChatRequest schema)
- [x] T059 Add conversation message limit (cap at 100 messages) in ChatService (MAX_CONTEXT_MESSAGES)
- [ ] T060 [P] Add error boundary component to chat interface in frontend
- [ ] T061 Test ambiguous input handling (agent asks for clarification)
- [ ] T062 Verify user data isolation (users cannot access other users' conversations/tasks)
- [ ] T063 Run quickstart.md validation end-to-end
- [x] T064 Update backend/.env.example with GEMINI_API_KEY placeholder

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **US6 Conversation Persistence (Phase 3)**: Depends on Foundational - Core for all chat
- **US1 & US2 Task Create/List (Phase 4)**: Depends on US6 - Core chat loop
- **US7 ChatKit UI (Phase 5)**: Depends on US1 & US2 - Needs working backend
- **US3, US4, US5 (Phases 6-8)**: Depend on Foundational - Can run in parallel with each other
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← CRITICAL GATE
    ↓
Phase 3 (US6: Persistence) ← Foundation for all chat
    ↓
Phase 4 (US1+US2: Create/List) ← Core functionality
    ↓
Phase 5 (US7: ChatKit UI) ← Full MVP
    ↓
Phases 6-8 (US3, US4, US5) ← Can be parallel with each other
    ↓
Phase 9 (Polish)
```

### Parallel Opportunities

**Within Phase 2 (Foundational)**:
```bash
# Models can be created in parallel:
Task: "T006 Create Conversation model"
Task: "T007 Create Message model"

# MCP tools can be created in parallel:
Task: "T013 add_task tool"
Task: "T014 list_tasks tool"
Task: "T015 complete_task tool"
Task: "T016 delete_task tool"
Task: "T017 update_task tool"
```

**Within Phase 5 (US7: ChatKit UI)**:
```bash
# Frontend components can be created in parallel:
Task: "T034 chat-api.ts"
Task: "T035 typing-indicator.tsx"
Task: "T036 message-list.tsx"
Task: "T037 chat-input.tsx"
```

**Phases 6, 7, 8 can run in parallel** (different tools, no dependencies):
- US3 (Task Completion)
- US4 (Task Deletion)
- US5 (Task Update)

---

## Parallel Example: Foundational Phase

```bash
# Launch all model creation tasks together:
Agent: "Create Conversation model in backend/src/models/conversation.py"
Agent: "Create Message model in backend/src/models/message.py"

# After models complete, launch all tool tasks together:
Agent: "Create add_task tool function in backend/src/agent/tools.py"
Agent: "Create list_tasks tool function in backend/src/agent/tools.py"
Agent: "Create complete_task tool function in backend/src/agent/tools.py"
Agent: "Create delete_task tool function in backend/src/agent/tools.py"
Agent: "Create update_task tool function in backend/src/agent/tools.py"
```

---

## Implementation Strategy

### MVP First (Phases 1-5)

1. Complete Phase 1: Setup (dependencies, migration)
2. Complete Phase 2: Foundational (models, tools, services)
3. Complete Phase 3: US6 - Conversation Persistence
4. Complete Phase 4: US1 & US2 - Task Create/List
5. Complete Phase 5: US7 - ChatKit UI
6. **STOP and VALIDATE**: Test full chat-to-task flow
7. Deploy/demo if ready

**MVP delivers**: Create tasks, list tasks, modern chat UI, persistent conversations

### Full Feature Delivery

8. Complete Phases 6-8: US3, US4, US5 (can be parallel)
9. Complete Phase 9: Polish
10. Final validation and deployment

---

## Task Summary

| Phase | Tasks | Parallel Tasks |
|-------|-------|----------------|
| Phase 1: Setup | 5 | 3 |
| Phase 2: Foundational | 14 | 7 |
| Phase 3: US6 Persistence | 7 | 0 |
| Phase 4: US1+US2 Create/List | 7 | 0 |
| Phase 5: US7 ChatKit UI | 10 | 4 |
| Phase 6: US3 Completion | 4 | 0 |
| Phase 7: US4 Deletion | 4 | 0 |
| Phase 8: US5 Update | 4 | 0 |
| Phase 9: Polish | 9 | 3 |
| **Total** | **64** | **17** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- The agent instructions in backend/src/agent/agent.py control intent recognition
- All MCP tools must include user_id parameter for data isolation
