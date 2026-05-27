---
name: to-prd
description: Turn the current conversation context into a PRD and submit it as a GitHub issue. No interview — just synthesizes what you've already discussed.
---

# /to-prd — Conversation to PRD

> "A problem well stated is a problem half solved." — Charles Kettering

## When to Use

- After `/skill:grill-me` or `/skill:grill-with-docs` has aligned on a feature
- When you have a clear understanding of what to build
- When you need a documented spec before implementation
- When the feature is complex enough to need a written plan

## When NOT to Use

- For trivial one-line fixes
- When the user says "just do it" and the scope is obvious
- When a PRD already exists for this feature

## What This Skill Does

1. Synthesizes the current conversation into a structured PRD
2. Reads `CONTEXT.md` to use correct domain language
3. Reads recent ADRs to respect existing decisions
4. Files the PRD as a GitHub issue (or Linear ticket, or local file)
5. Returns the issue number / file path for reference

## PRD Template

```markdown
# PRD: [Feature Name]

## Context
[2-3 sentences: what problem this solves, who it's for, why now]

## Goals
1. [Specific, measurable goal]
2. [Specific, measurable goal]
3. [Specific, measurable goal]

## Non-Goals (Explicitly Out of Scope)
1. [What we're NOT doing]
2. [What we're NOT doing]

## Success Criteria
- [ ] [Verifiable check — e.g., "User can complete checkout in <3 clicks"]
- [ ] [Verifiable check]
- [ ] [Verifiable check]

## Technical Approach

### Architecture
[High-level: which modules affected, which patterns used]

### Data Model
[Changes to database schema, API contracts, types]

### API Design
```
POST /api/v1/[endpoint]
Body: { ... }
Response: { ... }
```

### UI/UX
[Wireframe description or link to Figma]

## Rollout Plan
1. [Phase 1: MVP]
2. [Phase 2: Polish]
3. [Phase 3: Monitoring]

## Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| [e.g., Performance degradation] | Medium | High | [Load test before deploy] |

## Related
- CONTEXT.md terms: [list relevant domain terms]
- ADRs: [list relevant decisions]
- Issues: [list related issues]
```

## Process

### Step 1: Read Context

Before writing the PRD, read:
- `CONTEXT.md` (domain language)
- `docs/adr/` (recent decisions)
- `.kimi/skills-config.toml` (issue tracker config)

### Step 2: Synthesize from Conversation

Extract from the current session:
- Original request
- Decisions made during grilling
- Acceptance criteria agreed upon
- Files/modules identified as relevant
- Risks or concerns raised

### Step 3: Write PRD

Fill in the template above. Use the domain language from `CONTEXT.md`. Reference ADRs where relevant.

### Step 4: File as Issue

**If GitHub:**
```bash
gh issue create   --title "PRD: [Feature Name]"   --body-file /tmp/prd.md   --label "prd,feature"
```

**If Linear:**
```bash
# Use Linear CLI or API
# Requires LINEAR_API_KEY env var
```

**If Local:**
```bash
mkdir -p docs/prds
cp /tmp/prd.md "docs/prds/YYYY-MM-DD-[feature-name].md"
```

### Step 5: Return Reference

```
PRD filed as GitHub issue #42.
Link: https://github.com/owner/repo/issues/42

Next step: Break into issues with `/skill:to-issues`
```

## Edge Cases

**"We haven't aligned enough for a PRD"**
→ "The conversation doesn't have clear acceptance criteria yet. Let me run `/skill:grill-me` first to align, then we'll create the PRD."

**"This PRD would be 10 pages"**
→ Split into multiple PRDs: "Core PRD" + "Advanced Features PRD". File them as separate issues and link them.

**"The user wants to change the PRD after filing"**
→ Update the issue body. Add a "Changelog" section at the bottom documenting what changed and why.

## Success Criteria

This skill succeeded if:
- A PRD exists in a discoverable location (issue tracker or docs/)
- The PRD uses the project's domain language
- The PRD has clear success criteria
- The PRD explicitly states what's out of scope
- A link/reference is returned to the user
