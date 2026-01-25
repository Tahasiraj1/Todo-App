# Skill Validation Checklist

This checklist ensures every skill meets delivery standards before release.

## Key Validation Areas

### 1. Deployment Tested

- [ ] Installation procedures succeed
- [ ] Testing procedures pass
- [ ] Cleanup procedures work
- [ ] Tool versions are current (not >6 months old)
- [ ] No deprecated APIs present

### 2. Real Scenario Tested

Confirms the skill addresses domain questions, not just tool mechanics.

**Test Approach**:
- Use skill on a realistic scenario
- Verify it provides domain expertise, not just syntax
- Check edge cases are handled

**Example**: A Kafka skill should identify coupling issues in a scenario where "Service A calls B, C, D directly at 500ms each."

### 3. No Over-Engineering

- [ ] Relies on native tools rather than custom wrappers
- [ ] Avoids Python scripts that shell out to CLI tools
- [ ] SKILL.md documentation under 500 lines
- [ ] No unnecessary abstractions

### 4. Battle-Tested Assets

The assets/ directory should contain only:
- Code that has been executed successfully
- Manifests applied to real environments
- Templates with verified versions

**Not**: Untested generated code.

### 5. Domain Knowledge Included

Addresses the "when" and "why" alongside the "how":
- [ ] Architecture patterns documented
- [ ] Anti-patterns documented
- [ ] Trade-offs explained

### 6. Failure Mode Handling

- [ ] Debugging runbooks included
- [ ] Common mistakes documented
- [ ] Prevention strategies provided

## Pre-Delivery Certification

### Validation Report Template

```markdown
## Validation Report

**Skill**: [skill-name]
**Date**: [YYYY-MM-DD]
**Validator**: [name]

### Test Scenarios
1. [Scenario 1] - PASS/FAIL
2. [Scenario 2] - PASS/FAIL

### Tool Versions Verified
- [Tool 1]: [version]
- [Tool 2]: [version]

### Asset Execution Status
- [Asset 1]: Executed successfully
- [Asset 2]: Executed successfully

### Domain Knowledge Coverage
- [ ] Architecture patterns
- [ ] Anti-patterns
- [ ] Trade-offs
- [ ] Security considerations

### Certification
[ ] Skill is production-ready
```

## Quick Validation Script

Run before delivery:

```bash
python scripts/quick_validate.py <skill-folder>
```

Checks:
- SKILL.md exists
- Frontmatter is valid
- Name follows conventions
- Description is complete

## Full Validation Script

Run for packaging:

```bash
python scripts/package_skill.py <skill-folder>
```

Checks everything above plus:
- Structure compliance
- No placeholder content
- All references accessible

## Validation Categories

### Structural Validation

| Check | Requirement |
|-------|-------------|
| SKILL.md | Exists, valid frontmatter |
| name | Lowercase, hyphens, ≤64 chars |
| description | ≤1024 chars, [What]+[When] format |
| Line count | <500 lines |

### Content Validation

| Check | Requirement |
|-------|-------------|
| Scope | What it does AND does not do |
| Clarifications | User requirements, not domain knowledge |
| References | Domain expertise embedded |
| Examples | Good/bad patterns shown |

### Quality Validation

| Check | Requirement |
|-------|-------------|
| Reusability | Not tied to specific requirement |
| Zero-shot | Works without iteration |
| Battle-tested | Verified on real scenarios |
| No placeholders | All TODO items resolved |

## Common Validation Failures

### 1. Missing Frontmatter

```yaml
# Bad - no frontmatter
# Skill Title

# Good
---
name: skill-name
description: Description here
---
```

### 2. Invalid Name

```yaml
# Bad
name: My Skill Name  # spaces, capitals

# Good
name: my-skill-name  # lowercase, hyphens
```

### 3. Incomplete Description

```yaml
# Bad
description: Creates things

# Good
description: |
  Creates production-grade API documentation.
  Use when users ask to generate OpenAPI specs or API docs.
```

### 4. Placeholder Content

```markdown
# Bad
## [TODO: Add section]

# Good
## Error Handling
[Actual content]
```

### 5. Over-length SKILL.md

Move content to references/ if SKILL.md exceeds 500 lines.

## Post-Validation Actions

After validation passes:

1. **Package**: `python scripts/package_skill.py <skill-folder>`
2. **Test**: Use skill on a new scenario
3. **Document**: Update any missing documentation
4. **Deliver**: Skill is ready for use
