# Workflow Patterns

This document provides comprehensive guidance on documenting workflows within skills.

## Sequential Workflows

Break complex tasks into clear steps.

### Basic Sequential Pattern

```markdown
## Workflow

### Step 1: Validate Input
- Check required fields present
- Validate data types
- Return early on validation failure

### Step 2: Process Data
- Transform input format
- Apply business rules
- Handle edge cases

### Step 3: Verify Output
- Check output matches specification
- Validate against schema
- Log results

### Step 4: Deliver
- Format for target system
- Send/save output
- Confirm delivery
```

### Phase-Based Pattern

```markdown
## Phases

### Phase 1: Setup
| Step | Action | Checkpoint |
|------|--------|------------|
| 1.1 | Install dependencies | All installed |
| 1.2 | Configure environment | .env populated |
| 1.3 | Verify connections | All services reachable |

### Phase 2: Execution
| Step | Action | Checkpoint |
|------|--------|------------|
| 2.1 | Load data | Data in memory |
| 2.2 | Transform | Transformation complete |
| 2.3 | Validate | All validations pass |

### Phase 3: Delivery
| Step | Action | Checkpoint |
|------|--------|------------|
| 3.1 | Format output | Output formatted |
| 3.2 | Deliver | Delivery confirmed |
| 3.3 | Cleanup | Resources released |
```

## Conditional Workflows

Guide users through decision points.

### Simple Branch Pattern

```markdown
## Decision: Content Action

### If Creating New Content
1. Gather requirements
2. Generate draft
3. Review and refine
4. Deliver

### If Editing Existing Content
1. Load current content
2. Identify changes needed
3. Apply changes
4. Verify modifications
5. Deliver
```

### Decision Tree Pattern

```markdown
## Authentication Method Selection

```
Start
  ↓
Need OAuth?
  ├─ Yes → Use OAuth 2.0 flow
  │         ├─ Web app → Authorization Code
  │         ├─ Mobile → PKCE
  │         └─ Server → Client Credentials
  └─ No → Need API key?
            ├─ Yes → Use API key auth
            └─ No → Use session auth
```
```

### Fallback Strategy Pattern

```markdown
## Data Retrieval Strategy

1. **Primary**: Fetch from API
   - If success → return data
   - If failure → continue to fallback

2. **Fallback 1**: Check cache
   - If cache hit → return cached data
   - If cache miss → continue

3. **Fallback 2**: Use default
   - Return safe default value
   - Log fallback usage
```

## Complex Workflows

### Parallel Execution Pattern

```markdown
## Deployment Workflow

### Parallel Preparation
Execute simultaneously:
- [ ] Build application
- [ ] Run tests
- [ ] Generate documentation
- [ ] Prepare infrastructure

Wait for all to complete.

### Sequential Deployment
Execute in order:
1. Deploy to staging
2. Run smoke tests
3. Deploy to production
4. Verify production
```

### State Machine Pattern

```markdown
## Order Processing States

```
[Created] → [Validated] → [Processing] → [Shipped] → [Delivered]
    ↓           ↓              ↓             ↓
[Cancelled] [Rejected]    [Failed]      [Returned]
```

### Transitions

| From | To | Trigger |
|------|-----|---------|
| Created | Validated | Validation passes |
| Created | Cancelled | User cancels |
| Validated | Processing | Payment confirmed |
| Validated | Rejected | Validation fails |
| Processing | Shipped | Package sent |
| Processing | Failed | Processing error |
| Shipped | Delivered | Delivery confirmed |
| Shipped | Returned | Return requested |
```

### Iterative Pattern

```markdown
## Refinement Loop

```
Draft → Review → Refine → Review → ...
                   ↓
              [Approved] → Deliver
```

### Rules
- Maximum 5 iterations
- Exit on approval
- Escalate if max iterations reached
```

## Best Practices

### Clear Entry/Exit Criteria

```markdown
## Workflow: Data Migration

### Entry Criteria (Prerequisites)
- [ ] Source database accessible
- [ ] Target database provisioned
- [ ] Backup completed
- [ ] Migration scripts tested

### Exit Criteria (Completion)
- [ ] All data migrated
- [ ] Data integrity verified
- [ ] Performance acceptable
- [ ] Rollback plan documented
```

### Error Recovery Documentation

```markdown
## Error Recovery

| Failure Mode | Detection | Recovery Action |
|--------------|-----------|-----------------|
| Connection lost | Timeout | Retry 3x with backoff |
| Validation error | Exception | Log and skip record |
| Rate limit | 429 response | Wait and retry |
| Auth expired | 401 response | Refresh token |
| Data corruption | Checksum fail | Restore from backup |
```

### Specificity Requirements

**Avoid**:
```markdown
## Step 3
Do the thing with the data.
```

**Prefer**:
```markdown
## Step 3: Transform Data
Execute `scripts/transform.py` with the validated input:
```bash
python scripts/transform.py --input data/validated.json --output data/transformed.json
```

Expected output:
- File: `data/transformed.json`
- Records: Same count as input
- Format: JSON array
```

## Workflow Documentation Checklist

- [ ] Clear step numbering
- [ ] Specific actions (not vague)
- [ ] Expected outputs stated
- [ ] Error handling documented
- [ ] Entry/exit criteria defined
- [ ] Decision points explicit
- [ ] Commands/scripts exact
- [ ] Checkpoints included
