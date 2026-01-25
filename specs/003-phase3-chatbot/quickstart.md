# Quickstart: Phase III - AI-Powered Todo Chatbot

**Created**: 2026-01-18
**Feature**: [specs/003-phase3-chatbot/spec.md](./spec.md)

## Prerequisites

Before starting Phase III implementation, ensure:

- [ ] Phase II web application is fully functional
- [ ] Neon PostgreSQL database is running with users and tasks tables
- [ ] Better Auth is configured and working
- [ ] Python 3.11+ and Node.js 18+ installed
- [ ] Google AI Studio account with API key

## Environment Setup

### 1. Obtain Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create or sign in to your Google account
3. Navigate to "Get API Key"
4. Create a new API key
5. Copy the key for use in environment variables

### 2. Backend Environment Variables

Add to `backend/.env`:

```bash
# Existing Phase II variables
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
CORS_ORIGINS=http://localhost:3000

# NEW: Phase III AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Install Backend Dependencies

```bash
cd backend

# Add new dependencies to requirements.txt:
# openai-agents[litellm]>=0.2.0
# sse-starlette>=2.0.0

pip install -r requirements.txt
```

### 4. Frontend Dependencies

```bash
cd frontend

# Install ChatKit
npm install @openai/chatkit-js
```

## Database Migration

Run the Phase III migration to add conversation and message tables:

```bash
cd backend

# Using psql directly
psql $DATABASE_URL -f migrations/003_phase3_chat_schema.sql
```

Or create the migration file:

```sql
-- migrations/003_phase3_chat_schema.sql

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_conversation_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_updated_at ON conversations(updated_at DESC);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_message_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_message_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_message_created_at ON messages(created_at);
```

## Project Structure After Phase III

```
backend/
├── src/
│   ├── api/
│   │   └── routes/
│   │       ├── tasks.py        # Existing
│   │       └── chat.py         # NEW: Chat endpoint
│   ├── models/
│   │   ├── task.py             # Existing
│   │   ├── conversation.py     # NEW: Conversation model
│   │   └── message.py          # NEW: Message model
│   ├── services/
│   │   ├── task_service.py     # Existing
│   │   ├── chat_service.py     # NEW: Chat orchestration
│   │   └── conversation_service.py  # NEW: Conversation CRUD
│   └── agent/
│       ├── __init__.py         # NEW
│       ├── agent.py            # NEW: Agent configuration
│       └── tools.py            # NEW: MCP tool definitions
└── migrations/
    └── 003_phase3_chat_schema.sql  # NEW

frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/
│   │   │   └── page.tsx        # Existing
│   │   └── chat/
│   │       └── page.tsx        # NEW: Chat page
│   ├── components/
│   │   ├── tasks/              # Existing
│   │   └── chat/
│   │       ├── chat-interface.tsx   # NEW
│   │       ├── message-list.tsx     # NEW
│   │       └── chat-input.tsx       # NEW
│   └── lib/
│       ├── api.ts              # Existing
│       └── chat-api.ts         # NEW: Chat API client
└── package.json
```

## Quick Verification

### 1. Test Gemini API Connection

```python
# test_gemini.py
import asyncio
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
import os

async def test():
    agent = Agent(
        name="Test",
        instructions="Say hello",
        model=LitellmModel(
            model="gemini/gemini-2.0-flash",
            api_key=os.getenv("GEMINI_API_KEY")
        )
    )
    result = await Runner.run(agent, "Hello!")
    print(result.final_output)

asyncio.run(test())
```

### 2. Test Chat Endpoint (after implementation)

```bash
# Get JWT token from frontend login, then:
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my tasks"}'
```

### 3. Access Chat UI

After frontend implementation, navigate to:
- Local: http://localhost:3000/chat

## Development Workflow

1. **Backend First**: Implement models, services, and API endpoints
2. **Test with curl**: Verify chat endpoint works correctly
3. **Frontend Integration**: Build ChatKit interface
4. **End-to-End Testing**: Test complete user flows

## Key Implementation Notes

### Agent Configuration

```python
# backend/src/agent/agent.py
from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel
from .tools import add_task, list_tasks, complete_task, delete_task, update_task

def create_todo_agent() -> Agent:
    return Agent(
        name="TodoAssistant",
        instructions="""You are a helpful todo assistant. Help users manage their tasks through conversation.

When users want to:
- Add a task: Use the add_task tool
- See their tasks: Use the list_tasks tool
- Complete a task: Use the complete_task tool
- Delete a task: Use the delete_task tool
- Update a task: Use the update_task tool

Always confirm actions with friendly, conversational responses.
If you're unsure what the user wants, ask for clarification.""",
        model=LitellmModel(
            model="gemini/gemini-2.0-flash",
            api_key=os.getenv("GEMINI_API_KEY")
        ),
        tools=[add_task, list_tasks, complete_task, delete_task, update_task]
    )
```

### Stateless Request Handling

Every chat request follows this pattern:

1. Receive message with optional conversation_id
2. Authenticate and verify user
3. Load conversation history from database (if exists)
4. Store user message immediately
5. Run agent with history + new message
6. Store assistant response
7. Return response (server holds no state)

## Common Issues

### Gemini API Rate Limits
- Free tier: 15 requests/minute
- Solution: Implement retry with exponential backoff

### Database Connection Pooling
- Use SQLModel's session management properly
- Don't hold connections during AI processing

### JWT Token Expiry
- Frontend should handle 401 responses
- Refresh token or redirect to login

## Next Steps

After quickstart setup, proceed to implement:

1. Database models (Conversation, Message)
2. MCP tool functions
3. Agent service
4. Chat API endpoint
5. Conversation management endpoints
6. Frontend chat interface
7. Integration tests

Refer to `tasks.md` (after running `/sp.tasks`) for detailed implementation tasks.
