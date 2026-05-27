---
name: triage
description: State-machine issue triage. Triggers: user says 'triage', 'prioritize', 'sprint planning', 'backlog', 'organize issues'.

---

# /triage — Issue State Machine

> "Not everything that is faced can be changed, but nothing can be changed until it is faced." — James Baldwin

## When to Use

- When new issues are piling up and need organization
- At the start of a sprint or planning session
- When you need to prioritize what to work on next
- When issues are mixed (bugs, features, tech-debt, questions)

## When NOT to Use

- When there's only 1-2 issues (just pick one)
- When issues are already well-organized
- During active development (use after, not during)

## Triage Roles (State Machine)

Issues move through these states. Each state has specific criteria for advancement.

```
Incoming → Triage → Backlog → Todo → In Progress → Review → Done
            ↑___________________________________________↓
                          (rejected/needs-more-info)
```

### State Definitions

| State | Definition | Exit Criteria |
|---|---|---|
| **Incoming** | New issue, unread, unclassified | Read and classify |
| **Triage** | Being evaluated for priority and type | Has label, has estimate, has assignee |
| **Backlog** | Accepted but not scheduled | Ready to pull into sprint |
| **Todo** | Scheduled for current sprint | Has acceptance criteria, no blockers |
| **In Progress** | Being worked on | PR opened |
| **Review** | PR submitted, awaiting review | Approved by reviewer |
| **Done** | Merged and deployed | Verified in production |

### Triage Labels

Read from `.kimi/skills-config.toml`:

```toml
[triage]
labels = ["bug", "feature", "tech-debt", "blocked", "needs-design", "question"]
states = ["backlog", "todo", "in-progress", "review", "done"]
```

## Process

### Step 1: Fetch Incoming Issues

```bash
# GitHub
gh issue list --state open --label "incoming" --limit 50

# Or fetch all open issues if no "incoming" label exists
gh issue list --state open --limit 50
```

### Step 2: Classify Each Issue

For each issue, determine:

**Type:**
- `bug` — Something is broken
- `feature` — New capability
- `tech-debt` — Code improvement, no user-facing change
- `blocked` — Cannot proceed due to external dependency
- `needs-design` — Requires design input before engineering
- `question` — Not a work item, needs clarification

**Priority:**
- `P0` — Production incident, fix immediately
- `P1` — Blocks release or major feature
- `P2` — Important, schedule soon
- `P3` — Nice to have, backlog

**Effort (T-shirt size):**
- `XS` — <2 hours
- `S` — Half day
- `M` — 1-2 days
- `L` — 3-5 days
- `XL` — 1-2 weeks (should be sliced)

### Step 3: Apply Labels and State

```bash
# Example: Classify issue #42
gh issue edit 42 --add-label "bug,P1,M"
gh issue edit 42 --remove-label "incoming"
# If using project boards, move to "Triage" column
```

### Step 4: Identify Blockers and Dependencies

For each issue, check:
- Does it depend on another issue? (Add "Blocked by: #X")
- Is it blocked by an external factor? (Add `blocked` label, note in description)
- Does it block other issues? (Add "Blocks: #Y")

### Step 5: Present Triage Summary

```
## Triage Summary

### P0 (Fix Immediately)
- #42 — [Title] — [Type] — [Effort]

### P1 (This Sprint)
- #43 — [Title] — [Type] — [Effort]
- #44 — [Title] — [Type] — [Effort]

### P2 (Next Sprint)
- #45 — [Title] — [Type] — [Effort]

### P3 (Backlog)
- #46 — [Title] — [Type] — [Effort]
- #47 — [Title] — [Type] — [Effort]

### Needs More Info
- #48 — [Title] — (asked user for clarification)

### Tech Debt (Schedule Maintenance Day)
- #49 — [Title] — [Effort]
```

## Edge Cases

**"This issue is both a bug and a feature"**
→ Pick the primary type. If fixing a bug requires adding a feature, split into two issues: "Fix bug #X" and "Add feature #Y".

**"Everything is P1"**
→ Force ranking. If everything is priority 1, nothing is. Ask: "If you could only fix one thing today, which would it be?"

**"Issue has no description"**
→ Add `needs-info` label. Comment: "@user Could you add: 1) Steps to reproduce, 2) Expected behavior, 3) Actual behavior?"

## Success Criteria

This skill succeeded if:
- All open issues have a type label
- All open issues have a priority label
- All open issues have an effort estimate
- Blockers and dependencies are documented
- The user knows what to work on next
