# Technical Patterns

This document provides comprehensive technical guidance for error handling, security, and performance in skill development.

## Error Handling Framework

### Error Handling Table

| Scenario | Error Type | Action |
|----------|------------|--------|
| Invalid input | Validation fails | Return specific error with details |
| File not found | FileNotFoundError | Clear message with fix suggestion |
| Network failure | Timeout/connection | Retry 3x with exponential backoff |
| Auth failure | 401/403 | Prompt re-authentication |
| Rate limit | 429 | Backoff and retry |
| Server error | 5xx | Retry with backoff, fail gracefully |

### Retry Pattern

Exponential backoff with jitter:

```python
import random
import time

def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0
):
    for attempt in range(max_retries):
        try:
            return func()
        except RetryableError as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

### Error Response Structure

```typescript
interface ErrorResponse {
  isError: true;
  content: string;  // User-friendly message
  metadata: {
    code: string;        // Machine-readable code
    details?: unknown;   // Debug info (hidden from user)
    retryable: boolean;
  };
}
```

### Graceful Degradation Strategy

1. Execute primary logic
2. On transient failure → retry
3. On persistent failure → serve cached result if available
4. No cache → return safe default/partial result
5. Cannot continue → fail with clear guidance

## Security Considerations

### Secrets Management

**Never**:
- Hardcode credentials
- Commit `.env` files
- Log sensitive data

**Always**:
- Use environment variables
- Maintain `.env` in `.gitignore`
- Provide `.env.example` templates
- Rotate compromised credentials immediately

```python
# Good
import os
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ConfigError("API_KEY environment variable required")

# Bad
API_KEY = "sk-abc123..."  # Never do this
```

### Input Validation

Validate ALL external input.

**File Paths**:
```python
from pathlib import Path

def safe_path(user_input: str, base_dir: Path) -> Path:
    # Resolve to prevent traversal
    path = (base_dir / user_input).resolve()
    # Ensure within base directory
    if not path.is_relative_to(base_dir):
        raise SecurityError("Path traversal detected")
    return path
```

**User Input**:
```typescript
import { z } from 'zod';

const userSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().min(0).max(150)
});

function validateUser(input: unknown) {
  return userSchema.safeParse(input);
}
```

### SQL Injection Prevention

**Never concatenate user input**:

```python
# Bad - SQL injection vulnerable
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# Good - parameterized query
query = "SELECT * FROM users WHERE name = ?"
cursor.execute(query, (user_input,))
```

### Output Escaping

Prevent XSS:

```typescript
function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
```

## Dependencies & Setup

### Version Requirements

| Dependency | Minimum | Recommended |
|------------|---------|-------------|
| Python | 3.10+ | 3.11+ |
| Node.js | 18+ | 20+ |
| TypeScript | 5.0+ | Latest |

### Installation Process

```bash
# 1. Verify prerequisites
python --version  # 3.10+
node --version    # 18+

# 2. Install dependencies
pip install -r requirements.txt
npm install

# 3. Configure environment
cp .env.example .env
# Edit .env with actual values

# 4. Verify setup
python -m pytest tests/
npm test
```

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| Memory | 512MB | 2GB |
| Disk | 100MB | 500MB |
| Network | HTTPS outbound | - |

## Performance Optimization

### Timeout Protection

```typescript
async function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number = 25000  // Platform limit
): Promise<T> {
  return Promise.race([
    promise,
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new TimeoutError()), timeoutMs)
    )
  ]);
}
```

### Resource Limits

| Resource | Limit | Reason |
|----------|-------|--------|
| Request timeout | 25s | Platform limit |
| File size | 10MB | Memory constraint |
| Batch size | 100 items | Performance |
| Concurrent requests | 5 | Rate limiting |

### Caching Pattern

```python
from functools import lru_cache
from datetime import datetime, timedelta

class TimedCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return value
            del self.cache[key]
        return None

    def set(self, key: str, value):
        self.cache[key] = (value, datetime.now())
```

## Logging Best Practices

### Structured Logging

```python
import logging
import json

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, message: str, **context):
        self.logger.info(json.dumps({
            "message": message,
            "level": "INFO",
            **context
        }))

    def error(self, message: str, error: Exception, **context):
        self.logger.error(json.dumps({
            "message": message,
            "level": "ERROR",
            "error_type": type(error).__name__,
            "error_message": str(error),
            **context
        }))
```

### Log Levels

| Level | Use For |
|-------|---------|
| DEBUG | Development details |
| INFO | Normal operations |
| WARNING | Recoverable issues |
| ERROR | Failures requiring attention |
| CRITICAL | System failures |

## Testing Patterns

### Unit Test Structure

```python
def test_function_name_scenario_expected():
    # Arrange
    input_data = create_test_input()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_output
```

### Error Case Testing

```python
def test_function_invalid_input_raises_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        function_under_test(invalid_input)

    assert "expected message" in str(exc_info.value)
```
