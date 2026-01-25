# Data Model: Phase III - AI-Powered Todo Chatbot

**Created**: 2026-01-17
**Feature**: [specs/003-phase3-chatbot/spec.md](../spec.md)

## Overview

This document defines the data model for Phase III, including new entities for conversation management while reusing existing entities from Phase II.

## Entity Relationship Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      User       │     │   Conversation  │     │     Message     │
│  (from Phase II)│     │                 │     │                 │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │────<│ id (PK)         │────<│ id (PK)         │
│ email           │     │ user_id (FK)    │     │ user_id (FK)    │
│ name            │     │ created_at      │     │ conversation_id │
│ ...             │     │ updated_at      │     │ role            │
└─────────────────┘     └─────────────────┘     │ content         │
        │                                        │ created_at      │
        │                                        └─────────────────┘
        │
        │           ┌─────────────────┐
        └──────────<│      Task       │
                    │  (from Phase II)│
                    ├─────────────────┤
                    │ id (PK)         │
                    │ user_id (FK)    │
                    │ title           │
                    │ description     │
                    │ completed       │
                    │ created_at      │
                    │ updated_at      │
                    └─────────────────┘
```

## Entities

### Conversation (NEW)

Represents a chat session between a user and the AI assistant.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique conversation identifier |
| user_id | String | Foreign Key (User.id), Not Null | Owner of the conversation |
| created_at | Timestamp | Not Null, Default: NOW() | When the conversation was started |
| updated_at | Timestamp | Not Null, Default: NOW() | When the conversation was last active |

**Relationships**:
- Belongs to one User
- Contains many Messages

**Indexes**:
- `idx_conversation_user_id` on (user_id) - for filtering by user
- `idx_conversation_updated_at` on (updated_at DESC) - for sorting by recent

---

### Message (NEW)

Represents a single message in a conversation (either from user or assistant).

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique message identifier |
| user_id | String | Foreign Key (User.id), Not Null | Owner of the message (for security filtering) |
| conversation_id | Integer | Foreign Key (Conversation.id), Not Null | Parent conversation |
| role | Enum | Not Null, Values: "user", "assistant" | Who sent the message |
| content | Text | Not Null | The message content |
| created_at | Timestamp | Not Null, Default: NOW() | When the message was sent |

**Relationships**:
- Belongs to one Conversation
- Belongs to one User (for security filtering)

**Indexes**:
- `idx_message_conversation_id` on (conversation_id) - for fetching conversation history
- `idx_message_user_id` on (user_id) - for security filtering
- `idx_message_created_at` on (created_at) - for ordering messages

---

### Task (Existing - Phase II)

No changes to the Task entity from Phase II. The MCP tools will interact with this entity through the existing task service.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique task identifier |
| user_id | String | Foreign Key (User.id), Not Null | Owner of the task |
| title | String(200) | Not Null | Task title (1-200 characters) |
| description | Text | Nullable | Optional task description (max 1000 characters) |
| completed | Boolean | Not Null, Default: false | Completion status |
| created_at | Timestamp | Not Null, Default: NOW() | When the task was created |
| updated_at | Timestamp | Not Null, Default: NOW() | When the task was last modified |

---

### User (Existing - Phase II / Better Auth)

No changes to the User entity. Managed by Better Auth.

## Database Migration

### New Tables Required

```sql
-- Conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_conversation_user_id ON conversations(user_id);
CREATE INDEX idx_conversation_updated_at ON conversations(updated_at DESC);

-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_message_conversation_id ON messages(conversation_id);
CREATE INDEX idx_message_user_id ON messages(user_id);
CREATE INDEX idx_message_created_at ON messages(created_at);
```

## Data Access Patterns

### Conversation Management

1. **Create Conversation**: Insert new conversation when user starts chatting without conversation_id
2. **Get Conversation History**: Select all messages for a conversation, ordered by created_at
3. **Update Conversation**: Touch updated_at when new message is added
4. **List User Conversations**: Select conversations by user_id, ordered by updated_at DESC

### Message Management

1. **Add User Message**: Insert message with role="user" before processing
2. **Add Assistant Response**: Insert message with role="assistant" after AI processing
3. **Build Agent Context**: Fetch conversation history to construct message array for OpenAI Agent

### Security Filtering

All queries must include user_id filter:
- `WHERE user_id = :authenticated_user_id`
- This ensures users cannot access other users' conversations or messages

## Data Retention

- Conversations and messages are retained indefinitely by default
- Consider implementing cleanup for conversations older than 90 days in future iterations
- Deletion of a user should cascade delete all conversations and messages (ON DELETE CASCADE)
