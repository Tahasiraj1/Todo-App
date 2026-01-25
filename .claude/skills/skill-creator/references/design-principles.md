# Design Principles for Skills

This document adapts Eric Raymond's 17 Unix Philosophy rules to AI skill design.

## The 17 Rules Applied to Skills

### 1. Rule of Modularity

> "Write simple parts connected by clean interfaces"

- One skill = one responsibility
- Skills should compose rather than monoliths
- Clear input/output flows

### 2. Rule of Clarity

> "Clarity is better than cleverness"

- Explicit instructions over implicit magic
- Anyone reading SKILL.md understands the skill's purpose
- No hidden assumptions

### 3. Rule of Composition

> "Design programs to be connected to other programs"

- Skills produce outputs other skills consume
- Use standard formats (markdown, JSON, YAML)
- Chain-friendly design

### 4. Rule of Separation

> "Separate policy from mechanism; separate interfaces from engines"

- SKILL.md contains policy (what/when)
- references/ contains mechanism (how)
- Clear boundary between intent and implementation

### 5. Rule of Simplicity

> "Design for simplicity; add complexity only where you must"

- Start with minimal viable skill
- Add complexity only when necessary
- Fewer clarifications beats more clarifications

### 6. Rule of Parsimony

> "Write big programs only when nothing else will do"

- Don't create skills for one-off tasks
- Skills address recurring patterns
- Justify the skill's existence

### 7. Rule of Transparency

> "Design for visibility to make inspection and debugging easier"

- Skills explain their actions
- Surface assumptions explicitly
- Include "Before Implementation" context gathering

### 8. Rule of Robustness

> "Robustness is the child of transparency and simplicity"

- Simple + transparent = robust
- Complex + opaque = fragile
- Prefer obvious solutions

### 9. Rule of Representation

> "Fold knowledge into data so program logic can be stupid and robust"

- Encode domain expertise in references/ (data)
- Keep SKILL.md logic simple
- Let data drive behavior

### 10. Rule of Least Surprise

> "In interface design, always do the least surprising thing"

- Same inputs produce predictable behavior
- Follow established conventions
- Meet user expectations

### 11. Rule of Silence

> "When a program has nothing surprising to say, it should say nothing"

- Don't over-explain routine operations
- Report only exceptions
- Signal-to-noise ratio matters

### 12. Rule of Repair

> "When you must fail, fail noisily and as soon as possible"

- Validate inputs early
- Provide clear error messages with remediation
- Fail fast, fail clearly

### 13. Rule of Economy

> "Programmer time is expensive; conserve it in preference to machine time"

- Skills save human time
- Token cost acceptable if it reduces human effort
- Optimize for user productivity

### 14. Rule of Generation

> "Avoid hand-hacking; write programs to write programs when you can"

- Skills can create skills
- skill-creator embodies this principle
- Automate skill generation patterns

### 15. Rule of Optimization

> "Prototype before polishing. Get it working before you optimize it"

- Version 1: make it work
- Version 2: make it good
- Don't over-engineer initially

### 16. Rule of Diversity

> "Distrust all claims for 'one true way'"

- Accommodate valid variations
- Provide flexibility where appropriate
- Multiple approaches can be correct

### 17. Rule of Extensibility

> "Design for the future, because it will be here sooner than you think"

- Build for variations, not single requirements
- Use clarifications for variables
- Anticipate change

## The Meta-Rule

> "When in doubt, make it simpler, clearer, and more explicit."

Complexity is easy; simplicity is hard. **Simplicity wins.**

## Applied to Skill Creation

| Principle | Application |
|-----------|-------------|
| Modularity | One skill, one responsibility |
| Clarity | SKILL.md readable by anyone |
| Composition | Standard output formats |
| Separation | Policy in SKILL.md, mechanism in references/ |
| Simplicity | Minimal viable skill first |
| Parsimony | Only for recurring patterns |
| Transparency | Explicit context gathering |
| Robustness | Simple + transparent |
| Representation | Domain knowledge in references/ |
| Least Surprise | Predictable behavior |
| Silence | Only report exceptions |
| Repair | Fail fast with clear messages |
| Economy | Save human time |
| Generation | Skills create skills |
| Optimization | Working before polished |
| Diversity | Accommodate variations |
| Extensibility | Build for change |

## Source

These principles derive from Eric S. Raymond's *The Art of Unix Programming* (2003), codifying 50+ years of Unix design wisdom. They remain durable because they address fundamental software design tensions independent of technology.
