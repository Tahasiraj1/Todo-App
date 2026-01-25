# Output Patterns

This document provides template patterns and example-driven guidance for consistent output formatting.

## Template Patterns

### Strict Templates

Use exact format requirements when precision is critical.

**Report Structure Template**:
```markdown
# [Title]

## Executive Summary
[3-5 sentences summarizing key points]

## Key Findings
1. **Finding 1**: [Description]
2. **Finding 2**: [Description]
3. **Finding 3**: [Description]

## Recommendations
1. [Specific, actionable recommendation]
2. [Specific, actionable recommendation]

## Appendix
[Supporting data]
```

### Flexible Templates

For less rigid scenarios, use adaptable structures:

```markdown
# [Title]

## Overview
[Adapt length to audience: brief for executives, detailed for technical]

## [Main Content]
[Structure varies by purpose]

## Next Steps
[Adapt to context]
```

## Good/Bad Examples Pattern

Always provide both patterns with explanations.

### Error Handling

**Good**:
```python
def fetch_data(url: str) -> Result[Data, Error]:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Ok(parse_response(response.json()))
    except requests.Timeout:
        logger.error(f"Timeout fetching {url}")
        return Err(TimeoutError("Request timed out"))
    except requests.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        return Err(HTTPError(str(e)))
```

**Why**: Explicit error handling, logging, typed returns, user-friendly messages.

**Bad**:
```python
def fetch_data(url):
    return requests.get(url).json()
```

**Why**: No error handling, no logging, crashes on failure.

### Input Validation

**Good**:
```typescript
const schema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().positive()
});

function createUser(input: unknown) {
  const result = schema.safeParse(input);
  if (!result.success) {
    return { error: formatZodError(result.error) };
  }
  return { data: result.data };
}
```

**Why**: Schema validation, safe parsing, detailed errors.

**Bad**:
```typescript
function createUser(input: any) {
  db.insert(input);
}
```

**Why**: No validation, type safety, security vulnerability.

## Output Specifications

### API Responses

**Success Response**:
```json
{
  "success": true,
  "data": {
    "id": "123",
    "name": "Example"
  },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req_abc123"
  }
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req_abc123"
  }
}
```

**Pagination**:
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalCount": 150,
    "hasMore": true
  }
}
```

### Widget Requirements

Generated widgets must include:
- Theme-aware styling
- Data binding to system output
- Loading, error, and empty states
- Proper window object references

```typescript
interface WidgetProps {
  data: unknown;
  theme: 'light' | 'dark';
  onError?: (error: Error) => void;
}

interface WidgetState {
  status: 'loading' | 'ready' | 'error' | 'empty';
  data?: ProcessedData;
  error?: Error;
}
```

## Consistency Patterns

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | kebab-case | `user-service.ts` |
| Functions | camelCase | `getUserById()` |
| Classes/Types | PascalCase | `UserService` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| CSS classes | kebab-case | `user-card` |

### File Structure

```
src/
├── components/
│   ├── UserCard/
│   │   ├── index.ts
│   │   ├── UserCard.tsx
│   │   └── UserCard.test.tsx
├── hooks/
│   └── useUser.ts
├── services/
│   └── userService.ts
├── utils/
│   └── validation.ts
└── types/
    └── user.ts
```

## Format Selection Guide

| Scenario | Format |
|----------|--------|
| API data | JSON |
| Configuration | YAML or JSON |
| Documentation | Markdown |
| Logs | Structured JSON |
| Reports | Markdown with tables |
| Code output | Language-specific conventions |

## Output Checklist

Before delivering output:

- [ ] Format matches specification
- [ ] Naming conventions followed
- [ ] Error cases handled
- [ ] Examples provided where helpful
- [ ] Consistent with codebase patterns
