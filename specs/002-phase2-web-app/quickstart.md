# Quick Start Guide: Phase II - Todo Full-Stack Web Application

**Date**: 2025-01-27  
**Feature**: Phase II - Todo Full-Stack Web Application  
**Branch**: `002-phase2-web-app`

## Overview

This guide provides step-by-step instructions for setting up and running the Phase II Todo application locally for development.

## Prerequisites

- **Node.js**: 18+ (for Next.js frontend)
- **Python**: 3.13+ (for FastAPI backend)
- **PostgreSQL**: Neon Serverless PostgreSQL account (free tier available)
- **Git**: For version control
- **UV**: Python package manager (recommended) or pip

## Initial Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd Todo-App
git checkout 002-phase2-web-app
```

### 2. Database Setup

1. Create account at [Neon](https://neon.tech)
2. Create a new project
3. Copy the connection string (format: `postgresql://user:password@host/database`)
4. Save as environment variable `DATABASE_URL`

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies (using UV)
uv sync

# Or using pip
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@host/database"
export BETTER_AUTH_SECRET="your-secret-key-here"  # Generate a secure random string

# Run database migrations (if using Alembic)
# alembic upgrade head

# Start backend server
uvicorn src.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

### 4. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Set environment variables
export NEXT_PUBLIC_API_URL="http://localhost:8000"
export BETTER_AUTH_SECRET="your-secret-key-here"  # Same as backend
export BETTER_AUTH_URL="http://localhost:3000"

# Initialize shadcn/ui (if not already done)
npx shadcn-ui@latest init

# Add required shadcn components
npx shadcn-ui@latest add button input label dialog

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Development Workflow

### Running Both Services

**Terminal 1 - Backend**:
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### Testing

**Backend Tests**:
```bash
cd backend
pytest
```

**Frontend Tests**:
```bash
cd frontend
npm test
```

**E2E Tests**:
```bash
cd frontend
npm run test:e2e
```

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@host/database
BETTER_AUTH_SECRET=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

**Important**: `BETTER_AUTH_SECRET` must be the same in both frontend and backend.

## Project Structure

```
Todo-App/
├── backend/
│   ├── src/
│   │   ├── models/       # SQLModel models
│   │   ├── services/     # Business logic
│   │   ├── api/          # FastAPI routes
│   │   └── middleware/   # JWT verification
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js App Router
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities and API client
│   └── tests/
└── specs/
    └── 002-phase2-web-app/
```

## Common Tasks

### Create a New Task

1. Sign up or sign in at `http://localhost:3000`
2. Navigate to dashboard
3. Click "Add Task" button
4. Enter title and optional description
5. Submit form

### Update a Task

1. Click "Edit" on any task
2. Modify title or description
3. Save changes

### Mark Task Complete

1. Click checkbox or "Complete" button on a task
2. Task status toggles between complete/incomplete

### Delete a Task

1. Click "Delete" on a task
2. Confirm deletion in dialog
3. Task is removed

## Troubleshooting

### Backend Issues

**Database Connection Error**:
- Verify `DATABASE_URL` is correct
- Check Neon project is active
- Ensure connection string includes SSL parameters if required

**JWT Verification Fails**:
- Verify `BETTER_AUTH_SECRET` matches frontend
- Check token is being sent in `Authorization` header
- Verify token hasn't expired

### Frontend Issues

**API Calls Fail**:
- Verify `NEXT_PUBLIC_API_URL` points to backend
- Check backend is running on port 8000
- Verify CORS is configured in backend

**Authentication Issues**:
- Verify `BETTER_AUTH_SECRET` matches backend
- Check Better Auth configuration
- Clear browser cookies/localStorage

**shadcn Components Not Found**:
- Run `npx shadcn-ui@latest init` if not done
- Add missing components: `npx shadcn-ui@latest add <component-name>`

## Next Steps

1. Review [API Contract](./contracts/api-endpoints.md) for endpoint details
2. Review [Data Model](./data-model.md) for database schema
3. Review [Research](./research.md) for technical decisions
4. Proceed to `/sp.tasks` to break down implementation into tasks

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Better Auth Documentation](https://www.better-auth.com/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [Neon Documentation](https://neon.tech/docs)

