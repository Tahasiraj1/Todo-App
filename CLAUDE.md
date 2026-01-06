# Claude Code Instructions

This project uses **Spec-Driven Development** with Claude Code. All code must be generated following the specification artifacts.

## Project Context

**Active Feature**: Phase II - Todo Full-Stack Web Application  
**Branch**: `002-phase2-web-app`  
**Technology Stack**: Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL, Better Auth, shadcn/ui

## Active Technologies

- Next.js 16+ with App Router, TypeScript, Tailwind CSS (002-phase2-web-app)
- FastAPI, Python 3.13+, SQLModel (002-phase2-web-app)
- Neon Serverless PostgreSQL (002-phase2-web-app)
- Better Auth with JWT tokens (002-phase2-web-app)
- shadcn/ui components (002-phase2-web-app)
- zxcvbn password validation (002-phase2-web-app)
- Python 3.13+, UV, argparse, pytest (001-phase1-console - completed)

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLModel database models (User, Task)
│   ├── services/        # Business logic (task operations, auth verification)
│   ├── api/             # FastAPI routes (tasks, auth endpoints)
│   ├── middleware/      # JWT verification middleware
│   └── db.py            # Database connection and session management
└── tests/
    ├── unit/            # Unit tests for services and models
    └── integration/     # API integration tests

frontend/
├── src/
│   ├── app/             # Next.js App Router pages
│   │   ├── (auth)/      # Authentication routes (sign-in, sign-up)
│   │   ├── dashboard/   # Dashboard page
│   │   └── layout.tsx   # Root layout
│   ├── components/      # React components
│   │   ├── ui/          # shadcn/ui components
│   │   ├── tasks/       # Task-related components
│   │   └── auth/        # Authentication components
│   ├── lib/             # Utilities and services
│   │   ├── api.ts       # API client with JWT token handling
│   │   ├── auth.ts      # Better Auth configuration
│   │   └── utils.ts     # Helper functions
│   └── types/           # TypeScript type definitions
└── tests/
    ├── unit/            # Component unit tests
    └── e2e/             # Playwright E2E tests
```

## Development Workflow

1. **Read Specifications**: Always check `specs/002-phase2-web-app/` before implementing
2. **Follow Tasks**: Reference `specs/002-phase2-web-app/tasks.md` for task IDs
3. **Reference Plan**: Check `specs/002-phase2-web-app/plan.md` for architecture
4. **Code Generation**: All code must reference Task IDs in comments
5. **Use shadcn MCP**: Use shadcn MCP server to discover and implement UI components

## Code Requirements

- **Task References**: Every code file must contain comments linking to Task IDs
- **Format**: `[Task]: T-XXX [From]: spec.md §X.X, plan.md §Y.Y`
- **File Paths**: Follow exact paths specified in tasks.md
- **Error Handling**: Use Python exceptions with user-friendly messages to stderr
- **CLI Framework**: Use argparse (standard library)

## Key Files

- **Constitution**: `.specify/memory/constitution.md` - Project principles
- **Specification**: `specs/002-phase2-web-app/spec.md` - Requirements
- **Plan**: `specs/002-phase2-web-app/plan.md` - Technical design
- **Tasks**: `specs/002-phase2-web-app/tasks.md` - Implementation tasks
- **Data Model**: `specs/002-phase2-web-app/data-model.md` - Database schema
- **API Contracts**: `specs/002-phase2-web-app/contracts/api-endpoints.md` - REST API specification
- **OpenAPI**: `specs/002-phase2-web-app/contracts/openapi.yaml` - OpenAPI specification
- **Research**: `specs/002-phase2-web-app/research.md` - Technical decisions
- **Quickstart**: `specs/002-phase2-web-app/quickstart.md` - Setup guide

## Recent Changes

- 002-phase2-web-app: Added Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL, Better Auth, shadcn/ui, zxcvbn
- 001-phase1-console: Added Python 3.13+ + UV (package manager), Python standard library (argparse or click for CLI) - completed

## Commands

**Backend**:
- `cd backend; uvicorn src.main:app --reload --port 8000`
- `cd backend; pytest`

**Frontend**:
- `cd frontend; npm run dev`
- `cd frontend; npm test`
- `cd frontend; npm run test:e2e`

## Language Conventions

**Python (Backend)**:
- Use type hints where appropriate
- Follow PEP 8 style guide
- Use docstrings for functions and classes
- Use SQLModel for database models
- Use Pydantic for request/response validation

**TypeScript (Frontend)**:
- Use strict TypeScript configuration
- Follow Next.js App Router conventions
- Use server components by default, client components only when needed
- Use shadcn/ui components for UI consistency
- All API calls go through `lib/api.ts` with JWT token handling

**Last updated**: 2025-01-27

