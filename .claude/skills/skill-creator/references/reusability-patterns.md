# Reusability Patterns

This document outlines patterns for creating adaptable skills that handle variations across requirements.

## Core Framework

Every production-grade skill encodes two knowledge types:

1. **Procedural Knowledge (HOW)** - Step-by-step processes, decision trees, workflows
2. **Domain Expertise (WHAT)** - Concepts, best practices, patterns, anti-patterns

These work together to transform user requests into quality output.

## Key Principle: Varies vs Constant

The fundamental concept distinguishes between:
- **Varies**: Elements that change across use cases
- **Constant**: Elements that remain consistent

Effective skills:
- Encode constant patterns
- Ask clarifying questions about variable elements

## Domain Analysis Pattern

Before creating a skill, systematically analyze:

| Question | Informs |
|----------|---------|
| What changes between use cases? | Clarification questions |
| What stays the same? | Patterns to encode |
| What are common variations? | Options to present |
| What are the boundaries? | Scope definition |

## Examples by Domain

### Visualization Skills

| Varies | Constant |
|--------|----------|
| Data shape | Rendering lifecycle |
| Chart type | Accessibility requirements |
| Library choice | Error handling |
| Styling | Responsive patterns |

### Web Framework Skills

| Varies | Constant |
|--------|----------|
| Database | Project structure |
| CSS framework | Error handling patterns |
| Auth provider | Security patterns |
| API routes | Testing patterns |

### Deployment Skills

| Varies | Constant |
|--------|----------|
| Platform | CI/CD principles |
| Orchestration | Health check patterns |
| Environment | Logging patterns |
| Scale requirements | Rollback procedures |

### API Integration Skills

| Varies | Constant |
|--------|----------|
| Endpoints | Error handling |
| Authentication | Retry logic |
| Data formats | Rate limiting |
| Business logic | Timeout handling |

### Data Processing Skills

| Varies | Constant |
|--------|----------|
| Input/output formats | Validation patterns |
| Transformation rules | Streaming patterns |
| Scale | Error recovery |
| Business rules | Logging |

## Abstraction Levels

Skills exist at four levels (highest to lowest reuse potential):

### 1. Domain-Agnostic

- Error handling
- Logging
- Testing
- Documentation

**Highest reuse** - works across all domains.

### 2. Domain-Specific, Tool-Agnostic

- Visualization (tool-neutral)
- Deployment
- API integration

**High reuse** - works within domain, any tool.

### 3. Tool-Specific

- Next.js applications
- PostgreSQL databases
- React components

**Medium reuse** - works with specific tool.

### 4. Requirement-Specific

- "Create bar chart with sales data"
- "Deploy this specific app"

**Avoid creating skills at this level.**

## Clarification Questions Structure

Effective questions:
1. Identify variable elements
2. Provide reasonable options for common choices
3. Allow "other" for uncommon variations

### Good Example

```markdown
### What visualization type?
- [ ] Chart (line, bar, pie)
- [ ] Table (sortable, filterable)
- [ ] Dashboard (multiple widgets)
- [ ] Other: ___
```

### Bad Example

```markdown
The widget displays:
- product.name
- product.price
- product.quantity
```

*Hardcoding field names limits reusability.*

## Reusability Checklist

### Scope Requirements

- [ ] No hardcoded data fields/schemas
- [ ] No hardcoded tools/libraries (unless tool-specific)
- [ ] No hardcoded configurations
- [ ] Handles variations via clarifications

### Clarifications Should

- [ ] Request variable elements
- [ ] Provide reasonable options
- [ ] Accommodate uncommon variations

### Patterns Must

- [ ] Encode constant domain patterns
- [ ] Separate variable from constant concerns
- [ ] Work across multiple use cases

## Anti-Patterns to Avoid

### 1. Hardcoded Specifics

**Bad**:
```markdown
The widget displays product.name, product.price, product.quantity
```

**Good**:
```markdown
### Data Shape
What fields should be displayed?
- Field 1: ___
- Field 2: ___
- Field 3: ___
```

### 2. Tool Lock-in

**Bad**:
Creating a "visualization skill" that only works with Chart.js.

**Good**:
Creating a "visualization skill" that asks which library to use, with patterns for multiple options.

### 3. Feature Enumeration

**Bad**:
```markdown
Features:
- Show product name
- Show product price
- Show add to cart button
```

**Good**:
```markdown
Features:
- Display entity fields (configurable)
- Action buttons (configurable)
```

## Variability Encoding

### Option 1: Clarification Questions

Ask at skill invocation time.

```markdown
### Database
- [ ] PostgreSQL
- [ ] MySQL
- [ ] SQLite
- [ ] Other: ___
```

### Option 2: Pattern Library

Encode multiple patterns in references/.

```markdown
## PostgreSQL Pattern
[Pattern here]

## MySQL Pattern
[Pattern here]
```

### Option 3: Abstraction

Abstract away the variable.

```markdown
## Database Connection
Use the configured database driver.
```

## Summary

| Do | Don't |
|----|-------|
| Identify what varies | Hardcode specific values |
| Ask about variables | Assume requirements |
| Encode constants | Enumerate features |
| Support variations | Lock to one tool |
| Build abstractions | Create requirement-specific skills |
