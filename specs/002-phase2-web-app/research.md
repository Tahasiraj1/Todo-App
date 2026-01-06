# Research: Phase II - Todo Full-Stack Web Application

**Date**: 2025-01-27  
**Feature**: Phase II - Todo Full-Stack Web Application  
**Branch**: `002-phase2-web-app`

## Research Summary

This document consolidates research findings for implementing Phase II of the Todo App Evolution hackathon. All technical decisions are documented with rationale and alternatives considered.

## Technology Stack Decisions

### Frontend Framework: Next.js 16+ with App Router

**Decision**: Use Next.js 16+ with App Router for frontend implementation.

**Rationale**:
- Required by hackathon specification (Phase II technology stack)
- App Router provides modern React patterns with server components
- Built-in routing, API routes, and optimization features
- Excellent TypeScript support
- Seamless deployment to Vercel

**Alternatives Considered**:
- Next.js Pages Router: Rejected - App Router is the modern standard and required by spec
- React with Vite: Rejected - Not specified in hackathon requirements
- Remix: Rejected - Not specified in hackathon requirements

### Authentication: Better Auth with JWT

**Decision**: Use Better Auth library for frontend authentication with JWT token issuance.

**Rationale**:
- Required by hackathon specification
- Provides JWT plugin for token-based authentication
- Integrates seamlessly with Next.js
- Handles session management and token refresh
- Supports email/password authentication out of the box

**Alternatives Considered**:
- NextAuth.js: Rejected - Hackathon specifically requires Better Auth
- Custom JWT implementation: Rejected - Better Auth provides tested, secure implementation
- OAuth-only: Rejected - Hackathon requires email/password signup/signin

### UI Component Library: shadcn/ui

**Decision**: Use shadcn/ui components for consistent UI design.

**Rationale**:
- Specified in clarifications (user requirement)
- Copy-paste component model provides flexibility
- Built on Radix UI primitives (accessible)
- Tailwind CSS integration
- shadcn MCP available for component discovery

**Alternatives Considered**:
- Material-UI: Rejected - Not specified, shadcn/ui is required
- Chakra UI: Rejected - Not specified, shadcn/ui is required
- Custom components: Rejected - shadcn/ui ensures consistency

### Backend Framework: FastAPI

**Decision**: Use FastAPI for backend API implementation.

**Rationale**:
- Required by hackathon specification
- Modern Python web framework with async support
- Automatic OpenAPI documentation
- Type hints and Pydantic validation
- Excellent performance

**Alternatives Considered**:
- Django: Rejected - Not specified, FastAPI is required
- Flask: Rejected - Not specified, FastAPI is required
- Express.js: Rejected - Backend must be Python (FastAPI)

### Database: Neon Serverless PostgreSQL

**Decision**: Use Neon Serverless PostgreSQL for data persistence.

**Rationale**:
- Required by hackathon specification
- Serverless architecture aligns with stateless service requirements
- PostgreSQL provides ACID compliance and relational data model
- Free tier available for development
- Connection pooling and auto-scaling

**Alternatives Considered**:
- Supabase: Rejected - Hackathon specifically requires Neon
- PlanetScale: Rejected - Hackathon specifically requires Neon
- Local PostgreSQL: Rejected - Serverless required for cloud-native architecture

### ORM: SQLModel

**Decision**: Use SQLModel for database operations.

**Rationale**:
- Required by hackathon specification
- Combines SQLAlchemy and Pydantic
- Type-safe models with validation
- Automatic schema generation
- Works seamlessly with FastAPI

**Alternatives Considered**:
- SQLAlchemy: Rejected - SQLModel is required and provides better FastAPI integration
- Django ORM: Rejected - Not compatible with FastAPI
- Raw SQL: Rejected - SQLModel provides type safety and validation

### Password Validation: zxcvbn

**Decision**: Use zxcvbn library with minimum pass score of 3.

**Rationale**:
- Specified in clarifications (user requirement)
- Provides realistic password strength estimation
- Score 3 indicates "strong" password
- Better UX than arbitrary complexity rules
- Available for both frontend and backend

**Alternatives Considered**:
- Custom regex validation: Rejected - zxcvbn provides better security and UX
- Simple length check: Rejected - Insufficient security
- OWASP guidelines: Rejected - zxcvbn is more user-friendly and specified

## Architecture Decisions

### API Endpoint Pattern: JWT-Based Authentication

**Decision**: Extract user_id from JWT token only, remove from URL path. Use `/api/tasks` pattern (not `/api/{user_id}/tasks`).

**Rationale**:
- More secure - prevents URL manipulation attacks
- Aligns with JWT-based authentication patterns
- Cleaner API design
- User identity comes from authenticated token, not URL

**Alternatives Considered**:
- URL path with user_id: Rejected - Security risk, allows URL manipulation
- Both URL and JWT: Rejected - Redundant, adds complexity

### Stateless Backend Architecture

**Decision**: All backend services are stateless. All state persisted in database.

**Rationale**:
- Required by constitution (Principle IV)
- Enables horizontal scaling
- Resilient to server restarts
- Aligns with cloud-native patterns

**Alternatives Considered**:
- In-memory state: Rejected - Violates constitution, not scalable
- Session storage: Rejected - Better Auth handles sessions, backend should be stateless

### Monorepo Structure

**Decision**: Use monorepo with `frontend/` and `backend/` directories.

**Rationale**:
- Aligns with hackathon monorepo organization guide
- Single repository for easier development
- Shared types and utilities possible
- Clear separation of concerns

**Alternatives Considered**:
- Separate repositories: Rejected - Hackathon guide specifies monorepo
- Single codebase: Rejected - Frontend and backend have different tech stacks

## Integration Patterns

### JWT Token Flow

**Decision**: Frontend (Better Auth) issues JWT tokens. Backend verifies tokens using shared secret.

**Rationale**:
- Standard JWT authentication pattern
- Stateless authentication
- Shared secret ensures both services can verify tokens
- Better Auth handles token issuance and refresh

**Implementation**:
1. User signs in via Better Auth (frontend)
2. Better Auth issues JWT token with user_id, email
3. Frontend includes token in `Authorization: Bearer <token>` header
4. Backend middleware verifies token signature using shared secret
5. Backend extracts user_id from decoded token
6. Backend filters all operations by authenticated user_id

### API Client Pattern

**Decision**: Centralized API client in `frontend/src/lib/api.ts` with automatic JWT token attachment.

**Rationale**:
- Single source of truth for API calls
- Automatic token handling
- Consistent error handling
- Token refresh logic centralized

**Implementation**:
- API client reads JWT token from Better Auth session
- Automatically attaches to all requests
- Handles 401 responses with token refresh
- Redirects to sign-in if refresh fails

### Database Schema Design

**Decision**: Separate User and Task tables with foreign key relationship.

**Rationale**:
- Relational database best practices
- Enforces data integrity
- Enables efficient queries with user filtering
- Supports future features (Phase V: audit logs, etc.)

**Schema**:
- `users` table: id, email, name, password_hash, created_at
- `tasks` table: id, user_id (FK), title, description, completed, created_at, updated_at
- Index on `tasks.user_id` for efficient filtering

## Security Decisions

### User Data Isolation

**Decision**: Enforce user isolation at database query level. All queries filter by authenticated user_id.

**Rationale**:
- Defense in depth - even if frontend is compromised, backend enforces isolation
- Prevents unauthorized access
- Required by specification (FR-013, SC-010)

**Implementation**:
- All task queries include `WHERE user_id = :authenticated_user_id`
- Backend never trusts user_id from request body or URL
- Authorization checks on every operation

### Password Security

**Decision**: Use zxcvbn with minimum pass score of 3. Hash passwords with bcrypt (via Better Auth).

**Rationale**:
- zxcvbn provides realistic password strength
- Better Auth handles secure password hashing
- Score 3 ensures strong passwords without arbitrary rules

### JWT Token Security

**Decision**: Use shared secret (BETTER_AUTH_SECRET) for JWT signing and verification. Tokens expire automatically.

**Rationale**:
- Standard JWT security practice
- Token expiration reduces risk of token theft
- Shared secret ensures both services can verify tokens
- Better Auth handles token lifecycle

## Performance Decisions

### Database Indexing

**Decision**: Create index on `tasks.user_id` for efficient user filtering.

**Rationale**:
- Most queries filter by user_id
- Index improves query performance
- Required for SC-005 (500ms API response time)

### API Response Optimization

**Decision**: Return only necessary fields in API responses. Use SQLModel for efficient queries.

**Rationale**:
- Reduces payload size
- Improves response time
- SQLModel provides efficient ORM queries

### Frontend Optimization

**Decision**: Use Next.js App Router with server components where possible. Client components only for interactivity.

**Rationale**:
- Server components reduce client bundle size
- Better performance and SEO
- Aligns with Next.js best practices

## Error Handling Decisions

### API Error Responses

**Decision**: Return appropriate HTTP status codes (200, 201, 400, 401, 404, 500) with user-friendly error messages.

**Rationale**:
- Standard REST API practice
- Required by specification (FR-017, FR-020, FR-021)
- Clear error messages improve UX

### Token Refresh Handling

**Decision**: Silently attempt token refresh on 401 responses. Redirect to sign-in only if refresh fails.

**Rationale**:
- Better UX - users don't lose work
- Aligns with modern SPA patterns
- Specified in clarifications

## UI/UX Decisions

### Empty State Design

**Decision**: Show empty state message with "Add your first task" call-to-action button.

**Rationale**:
- Guides new users
- Improves onboarding
- Specified in clarifications

### Delete Confirmation

**Decision**: Show confirmation dialog with "Are you sure you want to delete this task?" and Cancel/Delete buttons.

**Rationale**:
- Prevents accidental deletions
- Standard UX pattern
- Specified in clarifications

### Responsive Design

**Decision**: Support screen sizes from 320px (mobile) to 2560px (desktop) using Tailwind CSS responsive utilities.

**Rationale**:
- Required by specification (FR-018, SC-008)
- Modern web application expectation
- Tailwind CSS provides responsive utilities

## Testing Strategy

### Frontend Testing

**Decision**: Use Jest and React Testing Library for unit tests, Playwright for E2E tests.

**Rationale**:
- Standard Next.js testing stack
- React Testing Library focuses on user behavior
- Playwright provides reliable E2E testing

### Backend Testing

**Decision**: Use pytest with httpx for API testing.

**Rationale**:
- Standard Python testing stack
- httpx provides async HTTP client for FastAPI testing
- pytest fixtures for test setup

## Deployment Decisions

### Frontend Deployment: Vercel

**Decision**: Deploy frontend to Vercel.

**Rationale**:
- Required by hackathon specification
- Seamless Next.js integration
- Free tier available
- Automatic deployments from Git

### Backend Deployment

**Decision**: Deploy backend as API service (specific platform TBD based on hackathon requirements).

**Rationale**:
- Backend must be accessible for frontend API calls
- Stateless architecture enables flexible deployment
- Can deploy to any Python hosting service

## Open Questions Resolved

All technical decisions have been made. No outstanding research questions remain.

## References

- Hackathon Specification: `Hackathon II - Todo Spec-Driven Development.md`
- Constitution: `.specify/memory/constitution.md`
- Feature Specification: `specs/002-phase2-web-app/spec.md`
- Better Auth Documentation: https://www.better-auth.com/docs
- Next.js Documentation: https://nextjs.org/docs
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- shadcn/ui Documentation: https://ui.shadcn.com/
- zxcvbn Documentation: https://github.com/dropbox/zxcvbn

