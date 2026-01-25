# Chat API Contract: Phase III - AI-Powered Todo Chatbot

**Created**: 2026-01-17
**Feature**: [specs/003-phase3-chatbot/spec.md](../spec.md)

## Overview

This document specifies the Chat API endpoint that serves as the interface between the OpenAI ChatKit frontend and the backend FastAPI server with OpenAI Agents SDK.

## Endpoint Specification

### POST /api/{user_id}/chat

Send a message and receive an AI-generated response.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | The authenticated user's ID |

#### Headers

| Header | Required | Description |
|--------|----------|-------------|
| Authorization | Yes | Bearer token (JWT from Better Auth) |
| Content-Type | Yes | application/json |

#### Request Body

```json
{
  "conversation_id": 12345,
  "message": "Add a task to buy groceries"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | integer | No | Existing conversation ID. If not provided, creates a new conversation |
| message | string | Yes | User's natural language message |

#### Response Body

```json
{
  "conversation_id": 12345,
  "response": "I've created a new task 'Buy groceries' for you. Is there anything else you'd like me to add?",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {
        "user_id": "usr_abc123",
        "title": "Buy groceries"
      },
      "result": {
        "task_id": 5,
        "status": "created",
        "title": "Buy groceries"
      }
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| conversation_id | integer | The conversation ID (new or existing) |
| response | string | AI assistant's response message |
| tool_calls | array | List of MCP tools that were invoked during processing |

#### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success - message processed and response returned |
| 400 | Bad Request - invalid request body (e.g., missing message) |
| 401 | Unauthorized - missing or invalid JWT token |
| 403 | Forbidden - user_id in URL doesn't match JWT token |
| 404 | Not Found - conversation_id doesn't exist or doesn't belong to user |
| 500 | Internal Server Error - processing failed |

## Request/Response Examples

### Example 1: Create New Conversation

**Request**:
```http
POST /api/usr_abc123/chat HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "message": "Show me all my tasks"
}
```

**Response**:
```json
{
  "conversation_id": 1,
  "response": "Here are your current tasks:\n\n1. Buy groceries (pending)\n2. Call mom (completed)\n3. Pay bills (pending)\n\nWould you like to add a new task or mark any of these as complete?",
  "tool_calls": [
    {
      "tool": "list_tasks",
      "parameters": {
        "user_id": "usr_abc123",
        "status": "all"
      },
      "result": [
        {"id": 1, "title": "Buy groceries", "completed": false},
        {"id": 2, "title": "Call mom", "completed": true},
        {"id": 3, "title": "Pay bills", "completed": false}
      ]
    }
  ]
}
```

### Example 2: Continue Existing Conversation

**Request**:
```http
POST /api/usr_abc123/chat HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "conversation_id": 1,
  "message": "Mark the groceries task as complete"
}
```

**Response**:
```json
{
  "conversation_id": 1,
  "response": "Done! I've marked 'Buy groceries' as complete. You now have 1 pending task remaining.",
  "tool_calls": [
    {
      "tool": "complete_task",
      "parameters": {
        "user_id": "usr_abc123",
        "task_id": 1
      },
      "result": {
        "task_id": 1,
        "status": "completed",
        "title": "Buy groceries"
      }
    }
  ]
}
```

### Example 3: Error Response - Unauthorized

**Request**:
```http
POST /api/usr_abc123/chat HTTP/1.1
Content-Type: application/json

{
  "message": "Show my tasks"
}
```

**Response (401)**:
```json
{
  "detail": "Authentication required"
}
```

### Example 4: Error Response - Missing Message

**Request**:
```http
POST /api/usr_abc123/chat HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "conversation_id": 1
}
```

**Response (400)**:
```json
{
  "detail": "message is required"
}
```

## Conversation Flow (Stateless Request Cycle)

The server follows this stateless processing flow for each request:

1. **Receive** - Accept user message via POST request
2. **Authenticate** - Verify JWT token and match with URL user_id
3. **Fetch History** - Load conversation history from database (if conversation_id provided)
4. **Store User Message** - Persist user message to database immediately
5. **Build Context** - Construct message array for agent (history + new message)
6. **Process** - Run OpenAI Agent with MCP tools
7. **Execute Tools** - Agent invokes appropriate MCP tool(s) as needed
8. **Store Response** - Persist assistant response to database
9. **Return** - Send response to client
10. **Reset** - Server holds NO state (ready for next request)

## Security Requirements

1. JWT token must be present in Authorization header
2. URL path user_id must match the user_id decoded from JWT token
3. Conversation must belong to the authenticated user
4. All database queries must filter by user_id
5. Error messages must not expose sensitive information

## Rate Limiting Considerations

The endpoint should implement rate limiting to prevent abuse:
- Maximum 60 requests per minute per user
- Maximum message length: 2000 characters
- Maximum conversation history: 100 messages per conversation
