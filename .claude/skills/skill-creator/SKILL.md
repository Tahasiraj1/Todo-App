---
name: skill-creator
description: |
  Creates production-grade, reusable skills that extend Claude's capabilities.
  This skill should be used when users want to create a new skill, improve an
  existing skill, or build domain-specific intelligence. Gathers context from
  codebase, conversation, and authentic sources before creating adaptable skills.
---

# Skill Creator

## Core Purpose

This meta-skill provides structured guidance for creating skills—reusable intelligence modules that extend Claude's capabilities with embedded domain expertise.

## How It Works

1. User requests skill creation
2. Claude uses this skill as guidance
3. Follow Domain Discovery → clarifying questions → skill generation
4. Output: skill with embedded domain knowledge

## What This Skill Does

- Guides creation of new skills from scratch
- Improves existing skills to production quality
- Provides patterns for 5 skill types (Builder, Guide, Automation, Analyzer, Validator)
- Ensures skills encode both procedural and domain expertise

## What It Does NOT Do

- Handle post-creation versioning/updates
- Create requirement-specific (non-reusable) skills
- Deploy to production independently
- Though it requires local testing before delivery

## Domain Discovery Framework

### Phase 1: Automatic Discovery (No User Input)

Research proactively before asking anything:
- Core concepts from official docs and Context7
- Standards/compliance via targeted searches
- Best practices (current year focus)
- Anti-patterns and common mistakes
- Security considerations
- Ecosystem tools and related technologies

**Source priority**: Official docs → library docs → GitHub → community → web search

### Phase 2: Knowledge Sufficiency Check

Verify internally before user contact:
- Core concepts understood?
- Best practices identified?
- Anti-patterns known?
- Security covered?
- Official sources found?

*If gaps exist → research more. Only ask user for proprietary/internal knowledge.*

### Phase 3: User Requirements (NOT Domain Knowledge)

| Ask | Don't Ask |
|-----|-----------|
| "What's YOUR use case?" | "What is [technology]?" |
| "What's YOUR tech stack?" | "What options exist?" |
| "Any existing resources?" | "How does it work?" |
| "Specific constraints?" | "What are best practices?" |

**Key principle**: The skill contains domain expertise. Users provide requirements.

## Required Clarifications

### Skill Metadata

**1. Skill Type** - Choose from:
- **Builder**: Create artifacts (widgets, code, documents)
- **Guide**: Provide instructions (how-to, tutorials)
- **Automation**: Execute workflows (file processing, deployments)
- **Analyzer**: Extract insights (code review, data analysis)
- **Validator**: Enforce quality (compliance checks, scoring)

**2. Domain** - What technology/domain?

### User Requirements (After Domain Discovery)

**3. Use Case** - User's specific needs
**4. Tech Stack** - Environment details
**5. Existing Resources** - Scripts, templates, configs to include
**6. Constraints** - Limitations specific to context

**Pacing**: Ask metadata immediately, conduct discovery after domain identification, then gather user requirements.

## Core Principles

### Reusable Intelligence, Not Requirement-Specific

Skills must handle variations, not single requirements:
- "Create bar chart with sales data using Recharts"
- "Create visualizations—adaptable to data shape, chart type, library"

Identify what varies vs. what's constant. See `references/reusability-patterns.md`.

### Concise is Key

Context window is shared (~1,500+ tokens per skill). Challenge every section:
- "Does Claude really need this?"
- "Does this justify its token cost?"

Prefer concise examples over verbose explanations.

### Appropriate Freedom

Match specificity to task fragility:

| Level | When | Example |
|-------|------|---------|
| High | Multiple valid approaches | "Choose your preferred style" |
| Medium | Preferred pattern exists | Pseudocode with parameters |
| Low | Operations are fragile | Exact scripts, few parameters |

### Progressive Disclosure

Three-level loading:
1. **Metadata** (~100 tokens)—Always in context (description ≤1024 chars)
2. **SKILL.md body** (<500 lines)—When skill triggers
3. **References** (unlimited)—Loaded as needed by Claude

## Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description, allowed-tools?, model?)
│   └── Procedural knowledge (workflows, steps, decision trees)
└── Bundled Resources
    ├── references/ - Domain expertise (structured per domain needs)
    ├── scripts/ - Executable code (tested, reliable)
    └── assets/ - Templates, boilerplate, images
```

### SKILL.md Requirements

| Component | Requirement |
|-----------|-------------|
| Line count | <500 lines (extract to references/) |
| Frontmatter | See `references/skill-patterns.md` |
| `name` | Lowercase, numbers, hyphens; ≤64 chars; match directory |
| `description` | [What] + [When]; ≤1024 chars; third-person |
| Description style | "This skill should be used when..." |
| Form | Imperative ("Do X" not "You should X") |
| Scope | What it does AND does not do |

### What Goes in references/

Embed domain knowledge discovered during research:

| Knowledge | Purpose |
|-----------|---------|
| Library/API documentation | Enable correct implementation |
| Best practices | Guide quality decisions |
| Code examples | Provide reference patterns |
| Anti-patterns | Prevent common mistakes |
| Domain-specific details | Support edge cases |

**Structure references/ based on domain needs.** For files >10k words, include grep search patterns in SKILL.md for efficient discovery.

### When to Generate scripts/

Generate scripts for deterministic, executable procedures:
- Setup/installation
- Processing (data/file transformation)
- Validation (compliance, verification)
- Deployment (services, infrastructure)

**Decision**: Complex, error-prone, or exactly-repeatable procedures → create script. Otherwise → document in SKILL.md or references/.

### When to Generate assets/

Generate assets for exact templates/boilerplate:
- Starting templates (HTML, component scaffolds)
- Configuration files (templates, schemas)
- Code boilerplate (base classes, starter code)

### What NOT to Include

- README.md (SKILL.md IS the readme)
- CHANGELOG.md
- LICENSE (inherited from repo)
- Duplicate information

### What Generated Skill Does at Runtime

```
User invokes skill
  ↓
Gather context from:
  1. Codebase (if existing project)
  2. Conversation (user requirements)
  3. Own references/ (embedded domain expertise)
  4. User-specific guidelines
  ↓
Implement ZERO-SHOT
```

### Include in Generated Skills

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

## Type-Aware Creation

After determining skill type, follow type-specific patterns:

| Type | Key Sections | Reference |
|------|--------------|-----------|
| **Builder** | Clarifications → Output Spec → Standards → Checklist | `skill-patterns.md#builder` |
| **Guide** | Workflow → Examples → Official Docs | `skill-patterns.md#guide` |
| **Automation** | Scripts → Dependencies → Error Handling | `skill-patterns.md#automation` |
| **Analyzer** | Scope → Criteria → Output Format | `skill-patterns.md#analyzer` |
| **Validator** | Criteria → Scoring → Thresholds → Remediation | `skill-patterns.md#validator` |

## Skill Creation Process

**Workflow**: Metadata → Discovery → Requirements → Analyze → Embed → Structure → Implement → Validate

See `references/creation-workflow.md` for detailed steps.

### Quick Steps

1. **Metadata**: Ask skill type + domain
2. **Discovery**: Research domain automatically
3. **Requirements**: Ask user's specific needs
4. **Analyze**: Identify procedural (HOW) + domain (WHAT) knowledge
5. **Embed**: Put domain expertise into `references/`
6. **Structure**: Initialize skill directory
7. **Implement**: Write SKILL.md + resources following type patterns
8. **Validate**: Run `scripts/package_skill.py` and test

### SKILL.md Template

```yaml
---
name: skill-name # lowercase, hyphens, ≤64 chars
description: | # ≤1024 chars
  [What] Capability statement.
  [When] Use when users ask to <triggers>.
allowed-tools: Read, Grep, Glob # optional: restrict tools
---
```

See `references/skill-patterns.md` for complete frontmatter spec and body patterns.

## Output Checklist

### Domain Discovery Complete

- [ ] Core concepts discovered and understood
- [ ] Best practices identified from authentic sources
- [ ] Anti-patterns documented
- [ ] Security considerations covered
- [ ] Official documentation linked
- [ ] User was NOT asked for domain knowledge

### Frontmatter

- [ ] `name`: lowercase, hyphens, ≤64 chars, matches directory
- [ ] `description`: [What]+[When], ≤1024 chars, clear triggers
- [ ] `allowed-tools`: Set if restricted access needed

### Structure

- [ ] SKILL.md <500 lines
- [ ] Progressive disclosure (details in references/)

### Design Principles

- [ ] Modular (one skill = one responsibility)
- [ ] Clear (explicit instruction, no ambiguity)
- [ ] Extensible (handles variations)

### Knowledge Coverage

- [ ] Domain expertise embedded
- [ ] Best practices documented
- [ ] Edge cases covered
- [ ] Security addressed

### Zero-Shot Implementation

- [ ] No external references required beyond skill
- [ ] Works without additional context gathering
- [ ] Claude can implement without user iteration

### Reusability

- [ ] Not tied to specific requirement
- [ ] Handles multiple use cases
- [ ] Adaptable to variations

### Type-Specific

- [ ] Follows chosen type patterns (see `references/skill-patterns.md`)

### Battle Testing (REQUIRED)

- [ ] Tested locally before delivery
- [ ] Works end-to-end
- [ ] Error handling verified
- [ ] Edge cases validated

## Reference Files

| File | Purpose |
|------|---------|
| `references/design-principles.md` | Detailed design philosophy |
| `references/skill-patterns.md` | Type-specific templates and patterns |
| `references/reusability-patterns.md` | Techniques for adaptable skills |
| `references/creation-workflow.md` | Step-by-step creation process |
| `references/validation-checklist.md` | Pre-delivery verification |
| `references/output-patterns.md` | Output formatting templates |
| `references/quality-patterns.md` | Quality gates and checklists |
| `references/technical-patterns.md` | Error handling, security, performance |
| `references/workflows.md` | Workflow documentation patterns |
| `scripts/init_skill.py` | Initialize new skill from template |
| `scripts/package_skill.py` | Validation and packaging tool |
| `scripts/quick_validate.py` | Quick validation check |

---

**This skill guides the creation of production-grade skills through structured domain discovery, clear requirements gathering, and type-aware implementation patterns.**
