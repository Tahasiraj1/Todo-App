# Skill Creation Workflow

## Overview

**Sequence**: Metadata → Discovery → Requirements → Analyze → Embed → Structure → Implement → Validate

**Foundational Principle**: Users want domain expertise IN the skill. They may not BE domain experts.

## Step 1: Get Skill Metadata

Ask only two initial questions:
- **Skill type**: Routes to appropriate patterns
- **Domain/technology**: Focuses discovery

Do NOT ask about domain knowledge yet.

## Step 2: Domain Discovery (Automatic)

Research the domain thoroughly before user engagement.

### Discover

- Core concepts
- Standards/compliance requirements
- Best practices
- Anti-patterns
- Security considerations
- Ecosystem tools
- Official sources

### Source Priority

1. Official documentation
2. Library docs (Context7)
3. GitHub repositories
4. Community resources
5. Web search

### Knowledge Sufficiency Check

Verify internally before proceeding:
- [ ] Core concepts understood?
- [ ] Best practices identified?
- [ ] Anti-patterns known?
- [ ] Security covered?
- [ ] Official sources found?

If gaps exist → research more.

## Step 3: Get User Requirements

Ask about THEIR context, not domain knowledge:

| Ask | Don't Ask |
|-----|-----------|
| "What's YOUR use case?" | "What is [technology]?" |
| "What's YOUR tech stack?" | "What options exist?" |
| "Any existing resources?" | "How does it work?" |
| "Specific constraints?" | "What are best practices?" |

## Step 4: Analyze Domain

Combine discovered knowledge with user requirements.

### Procedural Knowledge (HOW)
- Workflows
- Decision trees
- Error handling
- Step sequences

### Domain Expertise (WHAT)
- Concepts
- Best practices
- Anti-patterns
- Standards

### Variability Analysis
- What varies across use cases
- What stays constant
- Common variations
- Boundaries

## Step 5: Embed Domain Knowledge

### references/ folder

Contains knowledge for context:
- Library/API documentation
- Best practices
- Code examples
- Anti-patterns
- Domain-specific details

### scripts/ folder

For deterministic procedures:
- Setup/installation
- Processing
- Validation
- Deployment
- Automation

### assets/ folder

For templates:
- HTML boilerplate
- Configuration files
- Code boilerplate
- Starter files

**Critical**: Generated skills are zero-shot domain experts. The expertise gathered in Step 2 must be embedded so the skill can implement without runtime discovery.

## Step 6: Initialize Structure

Create folder hierarchy:

```
skill-name/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

Or run: `python scripts/init_skill.py <skill-name> --path <path>`

## Step 7: Implement by Type

### Builder Skills
- Required Clarifications
- Output Specification
- Domain Standards
- Output Checklist

### Guide Skills
- Workflow Steps
- Good/Bad Examples
- Official Documentation table
- When to Use/NOT Use

### Automation Skills
- Available Scripts table
- Dependencies
- Error Handling
- Input/Output Specification

### Analyzer Skills
- Analysis Scope
- Evaluation Criteria
- Output Format
- Validation Rules

### Validator Skills
- Quality Criteria
- Scoring Rubric
- Thresholds
- Remediation Patterns

## Step 8: Write SKILL.md

Structure includes:
1. Frontmatter (name, description, allowed-tools)
2. What This Skill Does / Does NOT Do
3. **Before Implementation** section
4. Type-specific sections
5. Reference Files table
6. Output Checklist

### Before Implementation Section (Critical)

```markdown
## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing structure, patterns, conventions |
| **Conversation** | User's specific requirements, constraints |
| **Skill References** | Domain patterns from `references/` |
| **User Guidelines** | Project-specific conventions, standards |

Ensure all required context gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).
```

## Step 9: Validate

Run validation:
```bash
python scripts/package_skill.py <path/to/skill-folder>
```

### Checklist

- [ ] Frontmatter accurate
- [ ] Structure compliant
- [ ] Reusability verified
- [ ] Zero-Shot Implementation supported
- [ ] Knowledge documented

## Step 10: Iterate

1. Use skill on real tasks
2. Identify gaps
3. Update skill
4. Revalidate
5. Repeat until production-ready

## Quick Reference

| Step | Action | Output |
|------|--------|--------|
| 1 | Get metadata | Type + Domain |
| 2 | Discover | Domain knowledge |
| 3 | Requirements | User context |
| 4 | Analyze | HOW + WHAT |
| 5 | Embed | references/, scripts/, assets/ |
| 6 | Structure | Directory created |
| 7 | Implement | Type-specific content |
| 8 | Write | SKILL.md complete |
| 9 | Validate | Pass checks |
| 10 | Iterate | Production-ready |
