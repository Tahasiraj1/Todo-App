<!--
Sync Impact Report:
Version: 1.0.0 (initial creation)
Modified Principles: None (initial creation)
Added Sections: All core principles, technology stack constraints, development workflow, governance
Removed Sections: None
Templates Requiring Updates:
  ✅ plan-template.md - Constitution Check section aligns with principles
  ✅ spec-template.md - Aligns with spec-driven workflow
  ✅ tasks-template.md - Aligns with task-based implementation
  ⚠️ Follow-up: Review command templates in .specify/templates/commands/ for agent-specific references
Deferred Items: None
-->

# Todo App Evolution Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

**MUST**: All features MUST follow the Spec-Kit Plus workflow: Specify → Plan → Tasks → Implement. No code generation is permitted without a complete specification.

**Rationale**: This prevents "vibe coding" and ensures every implementation maps to explicit requirements. The hackathon requires spec-driven development as a core deliverable.

**Enforcement**: 
- Agents MUST NOT write code without a referenced Task ID
- Agents MUST NOT modify architecture without updating `speckit.plan`
- Agents MUST NOT propose features without updating `speckit.specify`
- Every code file MUST contain a comment linking to Task and Spec sections

### II. AI-Native Implementation (NON-NEGOTIABLE)

**MUST**: All code MUST be generated using Claude Code. Manual code writing is strictly prohibited.

**Rationale**: The hackathon evaluates the process of refining specifications until Claude Code generates correct output. This demonstrates mastery of AI-driven development.

**Enforcement**:
- If Claude Code output is incorrect, refine the specification, not the code
- Document all specification iterations and prompts used
- Code must be traceable to specification artifacts

### III. Progressive Architecture Evolution

**MUST**: The application MUST evolve through 5 phases: Console App → Web App → AI Chatbot → Local K8s → Cloud K8s.

**Rationale**: This simulates real-world software evolution and teaches cloud-native architecture progression.

**Enforcement**:
- Each phase builds on the previous phase
- Phases cannot be skipped
- Architecture decisions must consider future phase requirements

### IV. Stateless Service Architecture

**MUST**: All services MUST be stateless. State MUST be persisted in the database (Neon PostgreSQL).

**Rationale**: Stateless services enable horizontal scaling, resilience, and cloud-native deployment patterns.

**Enforcement**:
- No in-memory state between requests
- Conversation history stored in database
- Server restarts must not lose state
- All services must be independently deployable

### V. Technology Stack Compliance

**MUST**: Each phase MUST use the specified technology stack. No substitutions without justification.

**Phase I**: Python 3.13+, UV, Claude Code, Spec-Kit Plus
**Phase II**: Next.js 16+ (App Router), FastAPI, SQLModel, Neon PostgreSQL, Better Auth
**Phase III**: OpenAI ChatKit, OpenAI Agents SDK, Official MCP SDK, FastAPI, SQLModel, Neon PostgreSQL
**Phase IV**: Docker, Minikube, Helm Charts, kubectl-ai, kagent, Docker AI Agent (Gordon)
**Phase V**: Kafka (Redpanda/Strimzi), Dapr, DigitalOcean DOKS (or AKS/GKE), CI/CD (GitHub Actions)

**Rationale**: Consistent technology stack enables evaluation and demonstrates proficiency with specified tools.

**Enforcement**:
- Stack changes require constitution amendment
- All dependencies must be justified in plan.md

### VI. Event-Driven Architecture (Phase V)

**MUST**: Phase V MUST implement event-driven architecture using Kafka and Dapr.

**Rationale**: Event-driven architecture enables decoupled microservices, scalable notification systems, and audit trails.

**Enforcement**:
- Task operations publish to Kafka topics
- Dapr Pub/Sub abstracts Kafka implementation
- Services communicate via events, not direct API calls
- Event schemas must be documented

### VII. Independent Feature Testability

**MUST**: All features MUST be independently testable and deliverable as MVP increments.

**Rationale**: Enables incremental delivery, parallel development, and independent validation of each feature.

**Enforcement**:
- User stories must be prioritized (P1, P2, P3...)
- Each story must be independently testable
- Features must not break when implemented independently
- Tests must be written before implementation (TDD)

### VIII. Clean Code & Project Structure

**MUST**: Code MUST follow clean code principles and proper project structure per phase requirements.

**Rationale**: Maintainable code structure enables collaboration and future evolution.

**Enforcement**:
- Phase I: `/src` folder with Python source code
- Phase II+: Monorepo structure with `/frontend` and `/backend`
- All phases: README.md, CLAUDE.md, specs folder
- Code must be readable, documented, and follow language conventions

## Technology Stack Constraints

### Required Technologies by Phase

**Phase I - Console App**:
- Python 3.13+ with UV package manager
- In-memory storage (no database)
- Command-line interface

**Phase II - Web Application**:
- Frontend: Next.js 16+ with App Router, TypeScript, Tailwind CSS
- Backend: FastAPI with Python
- Database: Neon Serverless PostgreSQL
- ORM: SQLModel
- Authentication: Better Auth with JWT tokens
- Deployment: Vercel (frontend)

**Phase III - AI Chatbot**:
- Frontend: OpenAI ChatKit
- Backend: FastAPI with OpenAI Agents SDK
- MCP Server: Official MCP SDK
- Database: Neon PostgreSQL (conversations, messages, tasks)
- Stateless chat endpoint with database persistence

**Phase IV - Local Kubernetes**:
- Containerization: Docker (Docker Desktop)
- Docker AI: Docker AI Agent (Gordon) for AI-assisted operations
- Orchestration: Minikube
- Package Manager: Helm Charts
- AI DevOps: kubectl-ai, kagent

**Phase V - Cloud Deployment**:
- Cloud Platform: DigitalOcean DOKS (or Azure AKS, Google GKE)
- Event Streaming: Kafka (Redpanda Cloud or Strimzi)
- Runtime: Dapr (Pub/Sub, State, Bindings, Secrets, Service Invocation)
- CI/CD: GitHub Actions
- Monitoring: Configured logging and monitoring

### Stack Modification Policy

Technology stack changes require:
1. Constitution amendment with rationale
2. Update to affected phase specifications
3. Migration plan if changing existing implementation

## Development Workflow

### Spec-Kit Plus Workflow (MANDATORY)

All development MUST follow this sequence:

1. **Specify** (`speckit.specify`): Capture requirements, user journeys, acceptance criteria
2. **Plan** (`speckit.plan`): Generate technical approach, architecture, component breakdown
3. **Tasks** (`speckit.tasks`): Break plan into atomic, testable work units with Task IDs
4. **Implement**: Generate code via Claude Code, referencing Task IDs

### Agent Behavior Rules

Agents MUST:
- Reference Task IDs in all code: `[Task]: T-001 [From]: speckit.specify §2.1, speckit.plan §3.4`
- Check constitution before proposing solutions
- Request clarification if specifications are incomplete
- Update relevant spec files when proposing changes

Agents MUST NOT:
- Generate code without Task ID reference
- Modify architecture without updating `speckit.plan`
- Propose features without updating `speckit.specify`
- Alter stack choices without justification
- Add endpoints/fields/flows not in specification
- Ignore acceptance criteria

### Specification Hierarchy

In case of conflicts, priority order:
1. **Constitution** (this document) - Principles and constraints
2. **Specify** (`speckit.specify`) - Requirements and acceptance criteria
3. **Plan** (`speckit.plan`) - Architecture and technical approach
4. **Tasks** (`speckit.tasks`) - Implementation work units

## Security & Authentication

### Authentication Requirements (Phase II+)

**MUST**: Implement user authentication using Better Auth with JWT tokens.

**Enforcement**:
- Frontend uses Better Auth for login/signup
- Backend verifies JWT tokens from Authorization header
- All API endpoints require valid JWT token
- User data isolation enforced (users only see their own tasks)
- Shared secret (`BETTER_AUTH_SECRET`) used by both frontend and backend

### Security Standards

- API endpoints require authentication (Phase II+)
- User data isolation enforced at database level
- Secrets stored in environment variables or Kubernetes secrets
- No hardcoded credentials in code
- JWT tokens expire automatically

## Performance & Scalability

### Performance Goals

- Phase I: Console responsiveness (< 100ms command execution)
- Phase II: Web app page load < 2s, API response < 200ms p95
- Phase III: Chat response < 3s, stateless request handling
- Phase IV: Pod startup < 30s, horizontal scaling support
- Phase V: Event processing < 500ms, supports 1000+ concurrent users

### Scalability Requirements

- Stateless services enable horizontal scaling
- Database connection pooling
- Event-driven architecture for async processing
- Kubernetes auto-scaling support (Phase IV+)

## Observability & Monitoring

### Logging Requirements

**MUST**: Structured logging for all operations.

**Enforcement**:
- Log all task operations (create, update, delete, complete)
- Log authentication events
- Log MCP tool invocations (Phase III+)
- Log Kafka event publishing (Phase V)
- Use structured JSON logging format

### Monitoring (Phase IV+)

- Kubernetes pod health checks
- Application metrics (request rate, error rate, latency)
- Database connection monitoring
- Kafka topic lag monitoring (Phase V)

## Governance

### Constitution Authority

This constitution supersedes all other development practices and documentation. All code, architecture decisions, and development workflows MUST comply with these principles.

### Amendment Process

Constitution amendments require:
1. Document rationale for change
2. Update version number (semantic versioning: MAJOR.MINOR.PATCH)
3. Update affected specifications and templates
4. Document migration impact if changing existing implementations
5. Update this governance section with amendment date

### Compliance Review

All PRs and code reviews MUST verify:
- Code references Task IDs
- Specifications are complete before implementation
- Technology stack compliance
- Stateless architecture (where applicable)
- Testability of features

### Version Control

- Constitution version follows semantic versioning
- All amendments tracked with dates
- Version history maintained in this document

### Development Guidance

- Use `CLAUDE.md` (referencing `AGENTS.md`) for Claude Code instructions
- Use `README.md` for setup and deployment instructions
- Use `specs/` folder for all specification artifacts
- Reference constitution in all specification files

**Version**: 1.0.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-01-27
