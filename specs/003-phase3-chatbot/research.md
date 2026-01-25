# Research: Phase III - AI-Powered Todo Chatbot

**Created**: 2026-01-18
**Feature**: [specs/003-phase3-chatbot/spec.md](./spec.md)

## Overview

This document captures research findings for Phase III implementation, resolving all technical unknowns and documenting best practices for the chosen technology stack.

---

## 1. OpenAI Agents SDK with Google Gemini

### Decision
Use OpenAI Agents SDK with LiteLLM integration to support Google Gemini models.

### Rationale
- OpenAI Agents SDK provides a lightweight, well-documented framework for building AI agents
- LiteLLM integration allows using Gemini models with the same familiar API
- Built-in support for function/tool calling, which maps directly to MCP tools
- Supports streaming responses for better UX

### Implementation Pattern

```python
# Install: pip install "openai-agents[litellm]"
from agents import Agent, Runner, function_tool
from agents.extensions.models.litellm_model import LitellmModel

# Create agent with Gemini model
agent = Agent(
    name="TodoAssistant",
    instructions="You are a helpful todo assistant...",
    model=LitellmModel(
        model="gemini/gemini-2.0-flash",  # or gemini-2.5-flash-preview
        api_key=os.getenv("GEMINI_API_KEY")
    ),
    tools=[add_task, list_tasks, complete_task, delete_task, update_task]
)

# Run the agent
result = await Runner.run(agent, user_message)
```

### Environment Variables Required
- `GEMINI_API_KEY`: Google AI Studio API key for Gemini model access

### Alternatives Considered
1. **Direct Google AI SDK**: Less integration with tool calling patterns
2. **LangChain**: Heavier abstraction, unnecessary complexity for this use case
3. **OpenAI GPT-4**: Higher cost, spec requires Gemini

---

## 2. MCP (Model Context Protocol) Server Implementation

### Decision
Use FastMCP from the official MCP Python SDK to expose task operations as tools.

### Rationale
- FastMCP provides a decorator-based API similar to FastAPI
- Tools are automatically documented and type-validated
- Native async support for database operations
- Built-in transport options (HTTP, stdio)

### Implementation Pattern

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TodoMCP", json_response=True)

@mcp.tool()
async def add_task(user_id: str, title: str, description: str = None) -> dict:
    """Add a new task for the user."""
    # Implementation calls TaskService
    return {"task_id": task.id, "status": "created", "title": task.title}

@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> list:
    """List tasks for the user."""
    # Implementation calls TaskService
    return [{"id": t.id, "title": t.title, "completed": t.completed} for t in tasks]
```

### Integration Approach
Rather than running MCP as a separate server, the MCP tools will be:
1. Defined as Python functions with the `@function_tool` decorator from OpenAI Agents SDK
2. Directly callable by the agent within the FastAPI process
3. This avoids inter-process communication overhead

### Alternatives Considered
1. **Separate MCP Server Process**: Added complexity, latency from IPC
2. **Direct function calls without MCP**: Loses standardization benefits
3. **REST endpoints as tools**: More boilerplate, less type safety

---

## 3. OpenAI ChatKit Frontend Integration

### Decision
Use OpenAI ChatKit (`@openai/chatkit-js`) for the frontend chat UI with custom FastAPI backend.

### Rationale
- Production-ready chat UI components out of the box
- Built-in streaming support for AI responses
- Tool call visualization support
- Customizable theming to match existing app design
- Works with any backend that implements the ChatKit protocol

### Installation

```bash
npm install @openai/chatkit-js
```

### Frontend Implementation Pattern

```tsx
import { ChatKit, Thread, UserMessage, AssistantMessage } from '@openai/chatkit-js';

function ChatPage() {
  const handleSendMessage = async (message: string, conversationId?: number) => {
    const response = await fetch(`/api/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwt}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message, conversation_id: conversationId })
    });
    // Handle streaming response
  };

  return (
    <ChatKit>
      <Thread messages={messages} onSendMessage={handleSendMessage} />
    </ChatKit>
  );
}
```

### Backend Streaming Response Pattern

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

@app.post("/api/{user_id}/chat")
async def chat_endpoint(user_id: str, request: ChatRequest):
    async def generate():
        async for event in process_with_agent(user_id, request):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### Alternatives Considered
1. **Custom chat UI**: Significant development effort for similar result
2. **Vercel AI SDK Chat UI**: Less customization, different protocol
3. **React-chat-widget**: Less feature-rich, no tool support

---

## 4. Conversation Persistence Strategy

### Decision
Store conversations and messages in Neon PostgreSQL with SQLModel ORM.

### Rationale
- Reuses existing database infrastructure from Phase II
- SQLModel integrates seamlessly with FastAPI
- Supports the stateless server architecture requirement
- Enables conversation history retrieval on page refresh

### Database Schema

```sql
-- Already defined in data-model.md
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Access Pattern for Agent Context

```python
async def build_agent_context(conversation_id: int, user_id: str) -> list[dict]:
    """Build message history for agent from database."""
    messages = await get_conversation_messages(conversation_id, user_id)
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
```

---

## 5. Authentication Integration

### Decision
Reuse Better Auth JWT verification from Phase II for all chat endpoints.

### Rationale
- Maintains consistency with existing authentication flow
- JWT tokens already include user_id claims
- Existing middleware can be reused

### Implementation Pattern

```python
from ..middleware.auth import verify_jwt_token, get_current_user

@app.post("/api/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    # Verify URL user_id matches JWT user_id
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Process chat...
```

---

## 6. Dependencies to Add

### Backend (requirements.txt additions)

```text
# AI Agent
openai-agents[litellm]>=0.2.0
mcp>=1.0.0

# Streaming
sse-starlette>=2.0.0
```

### Frontend (package.json additions)

```json
{
  "dependencies": {
    "@openai/chatkit-js": "^0.1.0"
  }
}
```

---

## 7. Project Structure for Phase III

### Backend Additions

```
backend/src/
├── api/
│   └── routes/
│       └── chat.py          # NEW: Chat endpoint
├── models/
│   ├── conversation.py      # NEW: Conversation model
│   └── message.py           # NEW: Message model
├── services/
│   ├── chat_service.py      # NEW: Chat orchestration
│   └── agent_service.py     # NEW: Agent configuration
└── mcp/
    └── tools.py             # NEW: MCP tool definitions
```

### Frontend Additions

```
frontend/src/
├── app/
│   └── chat/
│       └── page.tsx         # NEW: Chat page
├── components/
│   └── chat/
│       ├── chat-interface.tsx   # NEW: ChatKit wrapper
│       ├── message-list.tsx     # NEW: Message display
│       └── chat-input.tsx       # NEW: Input component
└── lib/
    └── chat-api.ts          # NEW: Chat API client
```

---

## 8. Error Handling Strategy

### Agent Errors
- Wrap agent execution in try/catch
- Return user-friendly error messages
- Log detailed errors for debugging

### Tool Execution Errors
- MCP tools return error objects on failure
- Agent receives error context and can explain to user
- Example: "Task not found" → Agent: "I couldn't find a task with that ID. Would you like to see your task list?"

### Network/API Errors
- Frontend handles connection failures gracefully
- Retry logic for transient failures
- Clear error states in UI

---

## 9. Performance Considerations

### Response Time Targets
- Chat response < 3 seconds (per spec SC-001)
- Tool execution < 2 seconds (per spec SC-006)

### Optimization Strategies
1. **Streaming responses**: Show partial responses as they arrive
2. **Connection pooling**: Reuse database connections
3. **Async operations**: Non-blocking I/O throughout
4. **Message limit**: Cap conversation history at 100 messages

---

## 10. Security Considerations

### Input Validation
- Validate message length (max 2000 chars)
- Sanitize user input before storing
- Rate limit: 60 requests/minute/user

### Data Isolation
- All queries include user_id filter
- JWT verification on every request
- No cross-user data access possible

---

## Summary of Key Decisions

| Area | Decision | Key Package |
|------|----------|-------------|
| AI Agent | OpenAI Agents SDK + LiteLLM | `openai-agents[litellm]` |
| Model | Google Gemini 2.0 Flash | via LiteLLM |
| MCP Tools | Integrated function_tool pattern | `agents.function_tool` |
| Chat UI | OpenAI ChatKit | `@openai/chatkit-js` |
| Database | Neon PostgreSQL + SQLModel | `sqlmodel` |
| Auth | Better Auth JWT (reuse Phase II) | `PyJWT` |
| Streaming | SSE for responses | `sse-starlette` |
