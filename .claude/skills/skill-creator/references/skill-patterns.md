# Skill Patterns Reference

This document establishes standards for creating Claude Code skills with consistent structure and metadata.

## Frontmatter Requirements

Skills must include YAML frontmatter with required and optional fields.

### Required Fields

| Field | Requirements |
|-------|--------------|
| `name` | Lowercase, hyphenated, ≤64 chars, must match directory name |
| `description` | ≤1024 chars, "[What] [When]" format |

### Optional Fields

| Field | Purpose |
|-------|---------|
| `allowed-tools` | Restrict tool access (e.g., `Read, Grep, Glob`) |
| `model` | Override default model for capability needs |

### Description Format

```yaml
description: |
  [What] Creates production-grade visualizations from data.
  [When] Use when users ask to create charts, graphs, or dashboards.
```

**Strong descriptions** specify trigger conditions clearly:
- "Use when users ask to [action]"
- "This skill should be used when [scenario]"

## SKILL.md Structure Template

```markdown
---
name: skill-name
description: |
  [What] Capability statement.
  [When] Use when users ask to <triggers>.
---

# Skill Title

## What This Skill Does
- Capability 1
- Capability 2

## What It Does NOT Do
- Exclusion 1
- Exclusion 2

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing structure, patterns, conventions |
| **Conversation** | User's specific requirements, constraints |
| **Skill References** | Domain patterns from `references/` |
| **User Guidelines** | Project-specific conventions, standards |

## Required Clarifications
[Type-specific questions]

## Workflow
[Type-specific workflow]

## [Domain-Specific Content]
[Varies by skill type]

## Output Checklist
- [ ] Item 1
- [ ] Item 2

## Reference Files
| File | Purpose |
|------|---------|
| `references/file.md` | Description |
```

## Five Skill Types

### 1. Builder Skills

**Purpose**: Create artifacts (code, documents, widgets, configs)

**Key Sections**:
- Required Clarifications (what to build)
- Output Specification (exact format)
- Domain Standards (quality requirements)
- Output Checklist (verification)

**Template Pattern**:
```markdown
## Required Clarifications

### Output Type
- Widget / Component / Document / Configuration

### Data Shape
- What structure will input data have?

### Styling Requirements
- Theme support needed?
- Responsive requirements?

## Output Specification

### File Structure
[Exact output structure]

### Code Standards
[Language/framework requirements]

## Output Checklist
- [ ] Meets output specification
- [ ] Follows code standards
- [ ] Error states handled
- [ ] Accessible (if applicable)
```

### 2. Guide Skills

**Purpose**: Provide step-by-step instructions and tutorials

**Key Sections**:
- Workflow Steps (numbered sequence)
- Good/Bad Examples (concrete patterns)
- Official Documentation (authoritative sources)
- When to Use/NOT Use (boundaries)

**Template Pattern**:
```markdown
## Workflow

### Step 1: [Action]
[Clear instructions]

### Step 2: [Action]
[Clear instructions]

## Examples

### Good Example
[Correct pattern with explanation]

### Bad Example
[Incorrect pattern with explanation why]

## Official Documentation

| Resource | URL |
|----------|-----|
| Getting Started | [link] |
| API Reference | [link] |

## When to Use This Skill
- Scenario 1
- Scenario 2

## When NOT to Use
- Scenario 1
- Scenario 2
```

### 3. Automation Skills

**Purpose**: Execute workflows and process files

**Key Sections**:
- Available Scripts (executable procedures)
- Dependencies (requirements)
- Error Handling (failure modes)
- Input/Output Specification

**Template Pattern**:
```markdown
## Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/process.py` | Process files | `python scripts/process.py <input>` |

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| FileNotFound | Input missing | Check path |

## Input/Output

### Input Format
[Specification]

### Output Format
[Specification]
```

### 4. Analyzer Skills

**Purpose**: Extract insights, summarize, review content

**Key Sections**:
- Analysis Scope (what to examine)
- Evaluation Criteria (how to judge)
- Output Format (results structure)
- Validation Rules (quality checks)

**Template Pattern**:
```markdown
## Analysis Scope

### Include
- Item 1
- Item 2

### Exclude
- Item 1

## Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Correctness | High | Accurate results |
| Completeness | Medium | All items covered |

## Output Format

```json
{
  "summary": "string",
  "findings": ["array"],
  "score": "number"
}
```

## Validation Rules
- Rule 1
- Rule 2
```

### 5. Validator Skills

**Purpose**: Enforce quality standards and compliance

**Key Sections**:
- Quality Criteria (what to check)
- Scoring Rubric (how to score)
- Thresholds (pass/fail levels)
- Remediation Patterns (how to fix)

**Template Pattern**:
```markdown
## Quality Criteria

| Criterion | Required | Description |
|-----------|----------|-------------|
| Item 1 | Yes | Must pass |
| Item 2 | No | Optional |

## Scoring Rubric

| Score | Meaning |
|-------|---------|
| 100 | Perfect |
| 80-99 | Good |
| 60-79 | Acceptable |
| <60 | Failing |

## Thresholds

| Level | Minimum Score |
|-------|---------------|
| Production | 80 |
| Development | 60 |

## Remediation Patterns

### Issue: [Problem]
**Fix**: [Solution]
**Example**: [Code]
```

## Type Selection Guide

| Primary Output | Skill Type |
|---------------|------------|
| New artifacts (code, docs, widgets) | Builder |
| Teaching/instructions | Guide |
| Multi-step execution | Automation |
| Information extraction | Analyzer |
| Standards enforcement | Validator |

## Asset Management

### When to Include assets/

- Skill provides templates users can customize
- Multiple reference documents support implementation
- Boilerplate code or starter files needed

### When NOT to Include assets/

- Purely instructional content
- Guiding users through existing tools
- No reusable templates needed

## Reference Organization

**Single-domain skills**: Organize by complexity level
**Multi-domain skills**: Organize by domain
**Feature-rich skills**: Organize by feature
