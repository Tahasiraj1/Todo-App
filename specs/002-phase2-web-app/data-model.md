# Data Model: Phase II - Todo Full-Stack Web Application

**Date**: 2025-01-27  
**Feature**: Phase II - Todo Full-Stack Web Application  
**Branch**: `002-phase2-web-app`

## Overview

This document defines the database schema and data models for Phase II of the Todo App Evolution. The data model supports user authentication, task management, and user data isolation.

## Database: Neon Serverless PostgreSQL

**Database Type**: PostgreSQL (serverless via Neon)  
**ORM**: SQLModel  
**Connection**: Managed via environment variable `DATABASE_URL`

## Entities

### User

Represents an authenticated user account in the system.

**Table Name**: `users`

**Attributes**:
- `id` (string, primary key): Unique user identifier. Format: UUID or string ID from Better Auth
- `email` (string, unique, required): User's email address. Must be unique across all users.
- `name` (string, required): User's display name.
- `password_hash` (string, required): Hashed password. Managed by Better Auth, not directly stored in our database.
- `created_at` (timestamp, required): Account creation timestamp. Auto-generated.

**Relationships**:
- One-to-many with Task: A user can have multiple tasks.

**Constraints**:
- Email must be unique (enforced at database level)
- Email must be valid format (validated at application level)
- Password must meet zxcvbn score of 3 (validated at application level)

**Indexes**:
- Primary key on `id`
- Unique index on `email`

**Notes**:
- User authentication is managed by Better Auth on the frontend
- Backend receives user_id from JWT token, does not directly manage user creation
- User data may be stored in Better Auth's database, backend may only reference user_id

### Task

Represents a todo item belonging to a user.

**Table Name**: `tasks`

**Attributes**:
- `id` (integer, primary key): Unique task identifier. Auto-incrementing.
- `user_id` (string, foreign key → users.id, required): Owner of the task. References User.id.
- `title` (string, required, 1-200 characters): Task title. Required, must be between 1 and 200 characters.
- `description` (text, optional, max 1000 characters): Task description. Optional, maximum 1000 characters if provided.
- `completed` (boolean, default false): Task completion status. Defaults to false (pending).
- `created_at` (timestamp, required): Task creation timestamp. Auto-generated.
- `updated_at` (timestamp, required): Last update timestamp. Auto-updated on modification.

**Relationships**:
- Many-to-one with User: Each task belongs to exactly one user.

**Constraints**:
- `user_id` must reference existing user (foreign key constraint)
- `title` must be between 1 and 200 characters (validated at application and database level)
- `description` must be maximum 1000 characters if provided (validated at application and database level)
- `completed` defaults to false

**Indexes**:
- Primary key on `id`
- Index on `user_id` (for efficient user filtering - critical for performance)
- Index on `completed` (optional, for potential status filtering in future)

**State Transitions**:
- **Pending → Completed**: User marks task as complete
- **Completed → Pending**: User toggles task back to incomplete
- **Any → Deleted**: User deletes task (soft delete not implemented, hard delete)

**Notes**:
- All queries must filter by `user_id` to enforce user isolation
- `updated_at` is automatically updated on any modification (title, description, or completed status)

## SQLModel Models

### User Model (Backend Reference)

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship (if needed for queries)
    tasks: list["Task"] = Relationship(back_populates="user")
```

**Note**: User model may be minimal since Better Auth manages user creation. Backend primarily receives user_id from JWT token.

### Task Model

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    user: Optional[User] = Relationship(back_populates="tasks")
```

### Task Create/Update Schemas (Pydantic)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

## Database Schema (SQL)

```sql
-- Users table (may be managed by Better Auth)
-- This schema is for reference if backend needs to query user data

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Tasks table

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT title_length CHECK (LENGTH(title) >= 1 AND LENGTH(title) <= 200),
    CONSTRAINT description_length CHECK (description IS NULL OR LENGTH(description) <= 1000)
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);

-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Data Validation Rules

### User Validation
- **Email**: Must be valid email format (RFC 5322 compliant)
- **Email**: Must be unique across all users
- **Name**: Required, no specific length constraint (reasonable limit: 100 characters)
- **Password**: Validated by Better Auth using zxcvbn (minimum score 3)

### Task Validation
- **Title**: Required, 1-200 characters
- **Description**: Optional, maximum 1000 characters if provided
- **Completed**: Boolean, defaults to false
- **User ID**: Must reference existing user (enforced by foreign key)

## Data Isolation

**Critical Requirement**: All task queries MUST filter by authenticated user_id.

**Implementation**:
- Backend extracts user_id from JWT token (never from URL or request body)
- All queries include `WHERE user_id = :authenticated_user_id`
- Database foreign key ensures user_id references valid user
- Application-level authorization checks prevent cross-user access

**Example Query Pattern**:
```python
# CORRECT: Filter by authenticated user
tasks = session.exec(
    select(Task).where(Task.user_id == authenticated_user_id)
).all()

# INCORRECT: No user filter (security violation)
tasks = session.exec(select(Task)).all()
```

## Migration Strategy

**Initial Migration**:
1. Create `users` table (if not managed by Better Auth)
2. Create `tasks` table with foreign key to users
3. Create indexes on `user_id` and `completed`
4. Create trigger for `updated_at` auto-update

**Future Migrations** (Phase V):
- May add indexes for search/filter functionality
- May add audit log table for task operations
- May add fields for due dates, priorities, tags

## Performance Considerations

- **Index on `user_id`**: Critical for fast user filtering (most common query pattern)
- **Index on `completed`**: Optional, useful for status filtering
- **Connection Pooling**: Use SQLModel/SQLAlchemy connection pooling for Neon serverless
- **Query Optimization**: Use SQLModel's select() for efficient queries
- **Pagination**: Not required for Phase II (up to 100 tasks per user), but consider for Phase V

## References

- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Neon Documentation: https://neon.tech/docs

