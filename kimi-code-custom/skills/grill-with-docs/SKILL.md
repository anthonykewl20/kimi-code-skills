---
name: grill-with-docs
description: Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates CONTEXT.md and ADRs inline. The single most powerful technique in this repo.
---

# /grill-with-docs — Alignment + Domain Language

> "With a ubiquitous language, conversations among developers and expressions of the code are all derived from the same domain model." — Eric Evans, *Domain-Driven Design*

## When to Use

- Starting work on a new project or major feature
- Onboarding a new team member (human or AI)
- When code reviews reveal naming inconsistencies
- When you find yourself explaining the same concept repeatedly
- Before `/skill:to-prd` or `/skill:to-issues`

## What Makes This Different from /grill-me

`/grill-me` aligns on WHAT to build. `/grill-with-docs` also:
1. Extracts and sharpens your project's **domain language**
2. Documents hard-to-explain decisions as **ADRs**
3. Updates `CONTEXT.md` with new terms and module maps
4. Reduces future token usage by giving the AI a concise vocabulary

## The Power of Shared Language

Example from a real project:

**BEFORE** (verbose, ambiguous):
> "There's a problem when a lesson inside a section of a course is made 'real' (i.e. given a spot in the file system)"

**AFTER** (concise, precise):
> "There's a problem with the materialization cascade"

This concision pays off session after session:
- Variables, functions, and files are named consistently
- The codebase is easier to navigate for the agent
- The agent spends fewer tokens thinking (more concise language)

## Process

### Phase 1: Read Existing Context

Before interviewing, read:
1. `CONTEXT.md` (if exists)
2. `docs/adr/` (recent ADRs)
3. Key source files in the area you're about to touch

### Phase 2: The Interview (Same as /grill-me, PLUS)

In addition to the 5 standard question categories, add:

**6. Domain Language Audit**
- "What do you call [concept X] in your team?"
- "Is there a standard term for [process Y]?"
- "Have you noticed any naming confusion in this area?"
- "What would a senior engineer on your team call this?"

**7. Decision Archaeology**
- "Why was [current approach] chosen over [alternative]?"
- "What constraints existed when this was originally built?"
- "Are there any 'weird' things in the code that have a historical reason?"
- "What would break if we changed [specific pattern]?"

### Phase 3: Update CONTEXT.md

After the interview, update `CONTEXT.md` with new or refined terms:

```markdown
# Domain Language

## [New/Updated Term]

**Term:** materialization cascade
**Definition:** The process of converting a virtual lesson into a real file-system entity, triggering updates to parent sections and the course index.
**Synonyms:** (avoid) "making it real", "file creation"
**Used in:** `src/courses/materialization.ts`, `src/sections/update.ts`
**Related:** `dematerialization`, `ghost lesson`

## [Another Term]
...
```

Rules for adding terms:
- One term per section with clear definition
- List synonyms that should be AVOIDED (the old verbose terms)
- Link to files where the term is used
- Cross-reference related terms

### Phase 4: Create or Update ADR

If the interview surfaced a non-obvious decision, create an ADR:

```bash
# Generate ADR filename
date +"%Y%m%d"  # e.g., 20260517
```

File: `docs/adr/20260517-remember-me-auth-storage.md`

```markdown
# ADR: Remember-Me Auth Storage

## Status
Accepted

## Context
The user wants a "remember me" feature. We had to choose between localStorage (client-side, vulnerable to XSS) and httpOnly cookies (server-side, CSRF-protected).

## Decision
Use secure httpOnly cookies with 30-day TTL.

## Consequences
- ✅ Secure against XSS extraction
- ✅ Automatic browser handling (no JS needed)
- ⚠️ Requires CSRF token mechanism
- ❌ Cannot be cleared by client-side "logout" alone (needs server endpoint)

## Related
- CONTEXT.md: "persistent session", "secure cookie storage"
```

### Phase 5: Summarize & Confirm

Same as `/skill:grill-me`, but include:

```
## Domain Updates
- Added terms: [list]
- Updated terms: [list]
- New ADR: [filename]
- Updated ADR: [filename]

## Alignment Summary
[Same as grill-me]
```

## Success Criteria

This skill succeeded if:
- `CONTEXT.md` was updated with at least one new or refined term
- The user confirmed the alignment summary
- You can explain the change using only the shared language (no verbose explanations needed)
- A new ADR was created if a non-trivial decision was made
