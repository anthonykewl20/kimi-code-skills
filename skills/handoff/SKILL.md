---
name: handoff
description: Multi-agent handoff bridge. Triggers: user says 'handoff', 'switch agent', 'another agent', 'continue later', 'pause', OR session >20 turns.

---

# /handoff — Multi-Agent Bridge

> "The art of progress is to preserve order amid change and to preserve change amid order." — Alfred North Whitehead

## When to Use

- When switching from "research agent" to "implementation agent"
- When a session is getting too long and you want to start fresh
- When delegating to a subagent with specific context
- When pausing work and resuming later (possibly on a different machine)
- When the current task phase is complete and the next phase needs different skills

## When NOT to Use

- For trivial tasks (<5 minute conversations)
- When continuing in the same session is fine
- When the context is still short and manageable

## The Handoff Document Format

A handoff document is a structured markdown file that captures:
1. **Goal** — What we were trying to achieve
2. **Decisions** — What was decided and why
3. **State** — Current state of the codebase
4. **Next Steps** — What needs to happen next
5. **Risks** — What could go wrong
6. **References** — Key files, issues, PRs

### Template

```markdown
# Handoff: [Task Name]

**Date:** [YYYY-MM-DD]
**Agent:** [Agent identifier or session ID]
**Status:** [In Progress / Blocked / Ready for Next Phase]

## Goal
[One sentence: what we set out to do]

## Decisions Made

| Decision | Rationale | Date |
|---|---|---|
| [e.g., Use PostgreSQL over MongoDB] | [e.g., ACID compliance required for financial data] | [date] |
| [e.g., Adopt Zod for validation] | [e.g., Type-safe, integrates with TS] | [date] |

## Current State

### Completed
- [ ] [Specific accomplishment with file path]
- [ ] [Specific accomplishment with file path]

### In Progress
- [ ] [What was being worked on when handoff occurred]

### Blocked
- [ ] [What's blocked and why]

## Next Steps

1. [Step] — [Acceptance criteria] — [Estimated effort]
2. [Step] — [Acceptance criteria] — [Estimated effort]
3. [Step] — [Acceptance criteria] — [Estimated effort]

## Risks & Warnings

- [Risk]: [Mitigation or note]
- [e.g., "Database migration not tested on production data"]: ["Test with sanitized snapshot before deploy"]

## Key Files

| File | Purpose | Status |
|---|---|---|
| `src/auth/service.ts` | Authentication logic | Complete |
| `src/auth/middleware.ts` | JWT validation | In progress |
| `tests/auth.test.ts` | Auth tests | 8/12 passing |

## Context References

- Issue: [#42](link)
- PR: [#43](link)
- ADR: `docs/adr/20260517-auth-storage.md`
- CONTEXT.md terms: "persistent session", "secure cookie storage"

## Notes for Next Agent

- [Specific instruction, e.g., "Don't touch `src/legacy/auth.js` — it's being deprecated"]
- [e.g., "Run `npm run test:auth` before committing — integration tests are flaky"]
```

## Process

### Step 1: Summarize the Conversation

Extract from the session history:
- Original request
- Key decisions made (with rationale)
- Files modified
- Tests written and their status
- Open questions or blockers

### Step 2: Capture Current State

Run these commands to get objective state:

```bash
# Git status
git status --short

# Recent commits
git log --oneline -10

# Test status
npm test 2>&1 | tail -20

# Lint status
npm run lint 2>&1 | tail -10
```

### Step 3: Identify Next Steps

Look at:
- What was planned but not started
- What was started but not finished
- What's blocked and needs unblocking
- What dependencies need to be resolved

### Step 4: Write Handoff Document

Save to `.kimi/handoffs/YYYY-MM-DD-[task-name].md`

```bash
mkdir -p .kimi/handoffs
```

### Step 5: Verify Completeness

Checklist:
- [ ] A new agent could understand the task from this document alone
- [ ] All decisions have rationales
- [ ] File paths are exact and current
- [ ] Next steps have acceptance criteria
- [ ] Risks are noted with mitigations
- [ ] No institutional knowledge is assumed

## Loading a Handoff

When a new agent starts:

```bash
# In Kimi Code
/import .kimi/handoffs/2026-05-17-auth-refactor.md
```

Or manually:
```
> I'm continuing work from a previous agent. Please read .kimi/handoffs/2026-05-17-auth-refactor.md and confirm you understand the current state before proceeding.
```

## Edge Cases

**"The conversation is too long to summarize"**
→ Use `/compact` first to compress the conversation, then generate the handoff from the summary.

**"There are no clear next steps"**
→ That's valuable information! Document: "Next steps unclear — need product input on [specific question]."

**"The code is in a broken state"**
→ Document exactly what's broken and how to reproduce. The next agent needs to know they're starting from a red state.

## Success Criteria

This skill succeeded if:
- A new agent can continue the work without asking "what were we doing?"
- All key decisions are preserved with rationale
- No critical context is lost
- The handoff document is <2 pages (concise but complete)
