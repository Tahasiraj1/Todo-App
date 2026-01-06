# API Contract: Phase II - Todo Full-Stack Web Application

**Date**: 2025-01-27  
**Feature**: Phase II - Todo Full-Stack Web Application  
**Branch**: `002-phase2-web-app`

## Overview

This document defines the RESTful API contract for the Todo application backend. All endpoints require JWT authentication via the `Authorization: Bearer <token>` header.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: TBD (backend deployment URL)

## Authentication

All API endpoints require JWT authentication.

**Header**: `Authorization: Bearer <jwt_token>`

**Token Source**: JWT token issued by Better Auth on frontend after user sign-in.

**Token Verification**: Backend verifies token signature using shared secret (`BETTER_AUTH_SECRET`).

**User Identification**: Backend extracts `user_id` from decoded JWT token. User_id is NOT included in URL path.

**Error Response (401 Unauthorized)**:
```json
{
  "detail": "Invalid or expired token"
}
```

## Common Response Codes

- `200 OK`: Successful GET, PUT, PATCH request
- `201 Created`: Successful POST request (resource created)
- `400 Bad Request`: Invalid request data or validation error
- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Resource not found or user does not have access
- `500 Internal Server Error`: Server error

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Validation Errors (400)**:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Title is required",
      "type": "value_error.missing"
    }
  ]
}
```

## Endpoints

### 1. List All Tasks

**GET** `/api/tasks`

**Description**: Retrieve all tasks belonging to the authenticated user.

**Authentication**: Required (JWT token)

**Query Parameters**: None

**Request Example**:
```http
GET /api/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK)**:
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "user-123",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2025-01-27T10:00:00Z",
      "updated_at": "2025-01-27T10:00:00Z"
    },
    {
      "id": 2,
      "user_id": "user-123",
      "title": "Call mom",
      "description": null,
      "completed": true,
      "created_at": "2025-01-26T15:30:00Z",
      "updated_at": "2025-01-27T09:00:00Z"
    }
  ]
}
```

**Empty Response (200 OK)**:
```json
{
  "tasks": []
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Database error

---

### 2. Create Task

**POST** `/api/tasks`

**Description**: Create a new task for the authenticated user.

**Authentication**: Required (JWT token)

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Request Schema**:
- `title` (string, required): Task title, 1-200 characters
- `description` (string, optional): Task description, maximum 1000 characters

**Request Example**:
```http
POST /api/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Response (201 Created)**:
```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-01-27T10:00:00Z",
  "updated_at": "2025-01-27T10:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Validation error (missing title, title too long, description too long)
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Database error

**Validation Error Example (400)**:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Title is required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### 3. Get Task by ID

**GET** `/api/tasks/{id}`

**Description**: Retrieve a specific task by ID. Only returns task if it belongs to the authenticated user.

**Authentication**: Required (JWT token)

**Path Parameters**:
- `id` (integer): Task ID

**Request Example**:
```http
GET /api/tasks/1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-01-27T10:00:00Z",
  "updated_at": "2025-01-27T10:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Task not found or does not belong to authenticated user
- `500 Internal Server Error`: Database error

---

### 4. Update Task

**PUT** `/api/tasks/{id}`

**Description**: Update an existing task. Only allows update if task belongs to the authenticated user.

**Authentication**: Required (JWT token)

**Path Parameters**:
- `id` (integer): Task ID

**Request Body**:
```json
{
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas"
}
```

**Request Schema**:
- `title` (string, optional): Task title, 1-200 characters
- `description` (string, optional): Task description, maximum 1000 characters

**Note**: At least one field (title or description) must be provided.

**Request Example**:
```http
PUT /api/tasks/1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas"
}
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas",
  "completed": false,
  "created_at": "2025-01-27T10:00:00Z",
  "updated_at": "2025-01-27T11:30:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Validation error (empty title, title too long, description too long)
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Task not found or does not belong to authenticated user
- `500 Internal Server Error`: Database error

---

### 5. Delete Task

**DELETE** `/api/tasks/{id}`

**Description**: Delete a task. Only allows deletion if task belongs to the authenticated user.

**Authentication**: Required (JWT token)

**Path Parameters**:
- `id` (integer): Task ID

**Request Example**:
```http
DELETE /api/tasks/1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK)**:
```json
{
  "message": "Task deleted successfully"
}
```

**Alternative Response (204 No Content)**:
No response body, just status code 204.

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Task not found or does not belong to authenticated user
- `500 Internal Server Error`: Database error

---

### 6. Toggle Task Completion

**PATCH** `/api/tasks/{id}/complete`

**Description**: Toggle the completion status of a task. Only allows toggle if task belongs to the authenticated user.

**Authentication**: Required (JWT token)

**Path Parameters**:
- `id` (integer): Task ID

**Request Example**:
```http
PATCH /api/tasks/1/complete HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body**: None (or empty JSON `{}`)

**Response (200 OK)**:
```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,
  "created_at": "2025-01-27T10:00:00Z",
  "updated_at": "2025-01-27T12:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Task not found or does not belong to authenticated user
- `500 Internal Server Error`: Database error

---

## Security Notes

1. **User Isolation**: All endpoints automatically filter by authenticated user_id from JWT token. Users cannot access or modify other users' tasks.

2. **Token Verification**: Backend verifies JWT token signature using shared secret. Invalid or expired tokens return 401.

3. **Input Validation**: All request bodies are validated for required fields, data types, and length constraints.

4. **Authorization**: Task operations (GET, PUT, DELETE, PATCH) verify that the task belongs to the authenticated user before proceeding.

## Rate Limiting

Not implemented in Phase II. Consider adding in Phase V for production deployment.

## CORS

Backend must allow CORS requests from frontend origin (Vercel deployment URL in production, localhost:3000 in development).

## References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- REST API Best Practices: https://restfulapi.net/

