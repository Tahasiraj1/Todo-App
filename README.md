# Todo App - Full-Stack Web Application

A modern full-stack todo application built with Next.js, FastAPI, and PostgreSQL.

## Features

- User registration and authentication with Better Auth
- Create, read, update, and delete tasks
- Mark tasks as complete/incomplete
- Responsive design for desktop, tablet, and mobile
- Secure user data isolation

## Tech Stack

### Frontend
- Next.js 16+ with App Router
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Better Auth (JWT authentication)
- zxcvbn (password validation)

### Backend
- FastAPI (Python 3.13+)
- SQLModel ORM
- PostgreSQL (Neon Serverless)
- JWT token verification

## Prerequisites

- Node.js 18+
- Python 3.13+
- PostgreSQL (Neon account)
- UV package manager (recommended) or pip

## Project Structure

```
Todo-App/
├── backend/
│   ├── src/
│   │   ├── models/       # SQLModel database models
│   │   ├── services/     # Business logic
│   │   ├── api/          # FastAPI routes
│   │   └── middleware/   # JWT verification
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js App Router pages
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities and API client
│   └── package.json
└── specs/                # Specification documents
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Todo-App
git checkout 002-phase2-web-app
```

### 2. Database Setup

1. Create account at [Neon](https://neon.tech)
2. Create a new project
3. Copy the connection string

### 3. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
# Edit .env with your DATABASE_URL and BETTER_AUTH_SECRET

# Start backend server
uvicorn src.main:app --reload --port 8000
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file from example
cp .env.local.example .env.local
# Edit .env.local with your settings

# Start development server
npm run dev
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@host/database
BETTER_AUTH_SECRET=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

**Important**: `BETTER_AUTH_SECRET` must be the same in both frontend and backend.

## Development

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

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/tasks | List all tasks |
| POST | /api/tasks | Create a new task |
| GET | /api/tasks/{id} | Get task by ID |
| PUT | /api/tasks/{id} | Update task |
| DELETE | /api/tasks/{id} | Delete task |
| PATCH | /api/tasks/{id}/complete | Toggle completion |

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

## Phase Evolution

This is **Phase II** of the Todo App Evolution hackathon project:

- **Phase I**: Console app with in-memory storage (completed)
- **Phase II**: Full-stack web app with database (current)
- **Phase III**: AI-powered chatbot interface
- **Phase IV**: Kubernetes deployment
- **Phase V**: Event-driven microservices

## Development Principles

This project follows Spec-Driven Development (SDD):
- Specifications: `specs/002-phase2-web-app/`
- All code is generated using Claude Code

## License

MIT
