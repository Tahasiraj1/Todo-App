# Todo App - Full-Stack Web Application

A modern full-stack todo application built with Next.js, FastAPI, PostgreSQL, and an event-driven microservices architecture powered by Dapr and Kafka.

## Features

### Core (Phase I-II)
- User registration and authentication with Better Auth
- Create, read, update, and delete tasks
- Mark tasks as complete/incomplete
- Responsive terminal-themed design for desktop, tablet, and mobile

### AI Chatbot (Phase III)
- AI-powered task management via natural language chat
- OpenAI Agents SDK integration with MCP tools

### Kubernetes (Phase IV)
- Helm chart deployment to Minikube and cloud clusters
- Health checks, readiness/liveness probes

### Event-Driven Cloud (Phase V)
- **Priorities & Tags**: Assign high/medium/low priorities and custom tags to tasks
- **Search, Filter & Sort**: Filter by priority, tag, status; search by keyword; sort by multiple fields
- **Due Dates & Reminders**: Set due dates, receive browser notifications or in-app reminders 30 min before
- **Recurring Tasks**: Daily/weekly/monthly recurrence with auto-creation of next occurrence on completion
- **Activity Log**: Event-driven audit trail of all task mutations with 90-day retention
- **Real-Time Sync**: WebSocket-based live updates across all open browser tabs
- **Dapr + Kafka Event Pipeline**: CloudEvents pub/sub via Dapr sidecars over Strimzi Kafka
- **Oracle OKE Deployment**: ARM64-compatible cloud deployment on Oracle Cloud free tier
- **CI/CD Pipeline**: GitHub Actions for automated build, test, push, and deploy
- **Structured JSON Logging**: Production-grade observability for all services

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│   Frontend   │◄──►│   Backend    │◄──►│   PostgreSQL     │
│   (Next.js)  │    │   (FastAPI)  │    │   (Neon)         │
│              │    │  + Dapr      │    └──────────────────┘
│  WebSocket ◄─┼────┤  Sidecar    │
└──────────────┘    └──────┬───────┘
                           │ CloudEvents
                    ┌──────▼───────┐
                    │    Kafka     │
                    │  (Strimzi)   │
                    └──┬───────┬───┘
              ┌────────▼──┐ ┌──▼────────────┐
              │Notification│ │Recurring Task │
              │  Service   │ │   Service     │
              │  + Dapr    │ │   + Dapr      │
              └────────────┘ └───────────────┘
```

## Tech Stack

### Frontend
- Next.js 16+ with App Router
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Better Auth (JWT authentication)
- WebSocket client with auto-reconnect

### Backend
- FastAPI (Python 3.13+)
- SQLModel ORM
- PostgreSQL (Neon Serverless)
- OpenAI Agents SDK (AI chatbot)
- Dapr HTTP API (event publishing, service invocation, Jobs scheduling)

### Infrastructure
- Kubernetes (Minikube / Oracle OKE)
- Helm 3 for deployment
- Dapr sidecars for service mesh
- Strimzi Kafka operator for messaging
- GitHub Actions for CI/CD

## Prerequisites

- Node.js 18+
- Python 3.13+
- PostgreSQL (Neon account)
- UV package manager (recommended) or pip
- **For K8s deployment**: Docker, Helm 3, Minikube or OKE
- **For event features**: Dapr CLI, Strimzi Kafka operator

## Project Structure

```
Todo-App/
├── backend/
│   ├── src/
│   │   ├── models/       # SQLModel database models + event schemas
│   │   ├── services/     # Business logic, event/reminder/activity services
│   │   ├── api/routes/   # FastAPI routes (tasks, chat, events, jobs, ws)
│   │   ├── agent/        # OpenAI Agents SDK + MCP tools
│   │   └── middleware/   # JWT verification, error handling
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js App Router pages
│   │   ├── components/   # React components (tasks, activity, notifications)
│   │   └── lib/          # API client, WebSocket, notifications
│   └── package.json
├── services/
│   ├── notification/     # WebSocket relay microservice
│   └── recurring-task/   # Recurring task creation microservice
├── k8s/
│   ├── helm/todo-chatbot/  # Helm chart (values, templates)
│   ├── kafka/              # Strimzi Kafka manifests
│   └── dapr/               # Dapr component definitions
├── .github/workflows/    # CI/CD pipeline
├── specs/                # Spec-Driven Development artifacts
└── docs/                 # Deployment and operations guides
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Todo-App
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

### 5. Kubernetes Deployment (Optional)

See [Phase IV Kubernetes Guide](docs/phase4-kubernetes-guide.md) for Minikube deployment, or [OKE Deployment Guide](docs/oke-deployment-guide.md) for Oracle Cloud deployment.

For the full event-driven stack (Dapr + Kafka), see [quickstart.md](specs/005-cloud-event-deployment/quickstart.md).

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@host/database
BETTER_AUTH_SECRET=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
OPENAI_API_KEY=sk-your-key
DAPR_ENABLED=false          # Set to true when running with Dapr sidecar
LOG_FORMAT=json              # json or text
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
| GET | /api/{user_id}/tasks | List tasks (with filter/sort/search) |
| POST | /api/{user_id}/tasks | Create a new task |
| GET | /api/{user_id}/tasks/{id} | Get task by ID |
| PUT | /api/{user_id}/tasks/{id} | Update task |
| DELETE | /api/{user_id}/tasks/{id} | Delete task |
| PATCH | /api/{user_id}/tasks/{id}/complete | Toggle completion |
| POST | /api/{user_id}/chat | Send chat message to AI agent |
| GET | /api/{user_id}/activity | Get activity log |
| WS | /api/ws/{user_id} | WebSocket for real-time updates |
| GET | /health | Health check |

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

## Phase Evolution

This is **Phase V** of the Todo App Evolution hackathon project:

- **Phase I**: Console app with in-memory storage (completed)
- **Phase II**: Full-stack web app with database (completed)
- **Phase III**: AI-powered chatbot interface (completed)
- **Phase IV**: Kubernetes deployment (completed)
- **Phase V**: Event-driven cloud microservices (current)

## Development Principles

This project follows Spec-Driven Development (SDD):
- Specifications: `specs/` (one directory per phase)
- All code is generated using Claude Code
- Prompt history tracked in `history/prompts/`

## License

MIT
