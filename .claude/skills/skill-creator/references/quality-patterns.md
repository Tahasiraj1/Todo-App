# Quality Patterns

This document provides guidelines for ensuring high-quality skill outputs through clarifications, enforcement checklists, and quality gates.

## User Interaction Patterns

### Clarification Questions Structure

Organize clarifications into Required vs Optional:

**Required**:
- Data shape: What structure will input have?
- Action type: Read-only or write operations?
- Output format: Expected result format?

**Optional** (ask when relevant):
- Styling preferences
- Performance requirements
- Compatibility constraints

### Context Awareness

Before asking questions:
1. Examine conversation history
2. Infer from filenames/content
3. Check available data structures
4. Only ask what cannot be determined

### Graceful Handling

**User skips required clarification**:
- Explain the need briefly
- Ask again simply
- Provide sensible default if possible

**User gives ambiguous answer**:
- Confirm understanding before proceeding
- Present interpretation for validation

**User skips optional clarification**:
- Proceed with sensible defaults
- Note assumptions made

## Official Documentation Links

### Documentation Table Pattern

```markdown
| Resource | Purpose |
|----------|---------|
| [Getting Started](url) | Initial setup |
| [API Reference](url) | Complete API docs |
| [Best Practices](url) | Recommended patterns |
| [Examples](url) | Code samples |
```

### Version Awareness

- Include verification dates
- Monitor changelogs
- Flag potential deprecations

## Domain Standards Enforcement

### Must Follow / Must Avoid Pattern

**Web Accessibility (WCAG)**:

| Must Follow | Must Avoid |
|-------------|------------|
| 4.5:1 contrast for text | Color-only indicators |
| 3:1 contrast for UI | Auto-playing audio |
| Keyboard accessibility | Missing alt text |
| Visible focus states | Inaccessible forms |

**API Security (OWASP)**:

| Must Follow | Must Avoid |
|-------------|------------|
| Input validation | Hardcoded secrets |
| Parameterized queries | SQL concatenation |
| Authentication | Verbose error messages |
| Rate limiting | Unvalidated redirects |
| HTTPS | Sensitive data in URLs |

**Code Quality**:

| Must Follow | Must Avoid |
|-------------|------------|
| TypeScript strict mode | `any` types |
| Explicit return types | Deep nesting (>3 levels) |
| Error handling | Silent failures |
| Meaningful names | Abbreviations |
| Single responsibility | God functions |

## Quality Gates

### Output Checklist Pattern

Verify before delivery:

**Functional**:
- [ ] Core features work
- [ ] Error states handled
- [ ] Loading states present
- [ ] Edge cases covered

**Quality**:
- [ ] Follows naming conventions
- [ ] No hardcoded values
- [ ] Appropriate comments
- [ ] Consistent formatting

**Standards**:
- [ ] Passes domain requirements
- [ ] Tested against acceptance criteria
- [ ] No security vulnerabilities

### Skill-Specific Checklists

**Widget Outputs**:
- [ ] window.openai data access
- [ ] Event listeners registered
- [ ] Loading state
- [ ] Error state
- [ ] Empty state
- [ ] Theme support
- [ ] WCAG compliance
- [ ] Responsive layout

**Script Outputs**:
- [ ] Error handling on sample input
- [ ] Graceful failure modes
- [ ] Expected output format
- [ ] Cleanup procedures
- [ ] Clear usage instructions

## Good/Bad Examples Pattern

Always provide both correct and incorrect patterns.

### Bad Example

```python
def process(data):
    try:
        result = transform(data)
    except:
        pass  # Silent failure - masks problems
    return result
```

**Why bad**: Silent `except` blocks hide errors, making debugging impossible.

### Good Example

```python
def process(data: Input) -> Result[Output, Error]:
    try:
        result = transform(data)
        return Ok(result)
    except ValidationError as e:
        logger.warning(f"Validation failed: {e}")
        return Err(ValidationError(str(e)))
    except TransformError as e:
        logger.error(f"Transform failed: {e}")
        return Err(TransformError(str(e)))
```

**Why good**: Explicit exception handling, appropriate logging, typed returns.

## Quality Verification Flow

```
1. Gather requirements
   ↓
2. Check clarifications complete
   ↓
3. Implement with standards
   ↓
4. Run output checklist
   ↓
5. Verify examples work
   ↓
6. Deliver
```

## Quality Metrics

| Metric | Target |
|--------|--------|
| Clarification completeness | 100% required answered |
| Standards compliance | All must-follow met |
| Error handling coverage | All error paths handled |
| Documentation completeness | All public APIs documented |

## Remediation Patterns

### Issue: Missing Error Handling

**Before**:
```typescript
async function fetchUser(id: string) {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}
```

**After**:
```typescript
async function fetchUser(id: string): Promise<Result<User, Error>> {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      return Err(new HTTPError(response.status, response.statusText));
    }
    const data = await response.json();
    return Ok(data as User);
  } catch (error) {
    return Err(new NetworkError('Failed to fetch user'));
  }
}
```

### Issue: Hardcoded Values

**Before**:
```typescript
const API_URL = 'https://api.example.com';
```

**After**:
```typescript
const API_URL = process.env.API_URL || 'https://api.example.com';
```
