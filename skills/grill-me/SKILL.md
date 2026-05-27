---
name: grill-me
description: Relentless alignment interview (min 5 questions). Triggers: user says 'new feature', 'build this', 'implement', 'design', 'plan', OR task requires modifying >5 files, OR user provides <3 sentences of requirements.

---

# /grill-me — Alignment Interview

> "No-one knows exactly what they want" — David Thomas & Andrew Hunt, *The Pragmatic Programmer*

## When to Use

- Before building any feature that takes >30 minutes
- When requirements feel vague or ambiguous
- When you're about to say "just make it work"
- When the user says "I think I want..." (uncertainty signal)

## When NOT to Use

- Fixing a one-line typo
- Adding an obvious missing import
- Any task where the solution is self-evident

## Process

### Phase 1: Surface the Request

Restate the user's request in your own words. Do NOT start coding.

```
"You want to [restate request]. Before I write any code, I need to make sure I understand this correctly. Let me ask you some questions."
```

### Phase 2: The Interview (Minimum 5 Questions)

Ask at least 5 clarifying questions. These should cover:

**1. The Goal (Why, not What)**
- "What problem are you trying to solve?" (not "what feature do you want?")
- "What does success look like for this?"
- "Who is the user, and what is their current pain point?"

**2. Scope Boundaries**
- "What is explicitly OUT of scope for this change?"
- "Are there related features that should NOT be touched?"
- "What's the smallest version of this that would still be useful?"

**3. Constraints & Context**
- "Are there performance requirements?" (latency, throughput, memory)
- "Are there security or compliance constraints?"
- "Does this need to work offline / on mobile / in the browser?"
- "What's the deadline or priority level?"

**4. Existing State**
- "Is there existing code that does something similar I should know about?"
- "Are there known technical debts in the area I'm about to touch?"
- "Has this been attempted before? What happened?"

**5. Acceptance Criteria**
- "How will we know this is done and working correctly?"
- "What tests or verifications should I include?"
- "What would make you reject the implementation?"

### Phase 3: Decision Tree Resolution

For each ambiguous branch in the user's answers, force a choice:

```
"You mentioned two possible approaches: A) [approach] and B) [approach].
These have different tradeoffs:
- A is [faster / simpler / cheaper] but [limitation]
- B is [more robust / more flexible] but [cost]

Which do you prefer? Or is there a third option?"
```

Do NOT proceed until every branch is resolved.

### Phase 4: Summarize & Confirm

Produce a concise summary:

```
## Alignment Summary

**Goal:** [One sentence]
**Scope:** [What's in / what's out]
**Approach:** [Chosen path + why]
**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
**Files to Touch:** [List]
**Files to NOT Touch:** [List]

Does this match your understanding? Say "yes" and I'll start coding. Say "no" and I'll re-interview.
```

Wait for explicit confirmation before writing code.

## Edge Cases

**User says "just do what you think is best"**
→ "I need your input on the tradeoffs. Here are 2-3 options with pros/cons. Pick one or tell me to pick based on [specific criterion]."

**User is impatient / wants to skip**
→ "This takes 2 minutes now and saves 2 hours of rewrites later. The last time we skipped this, we had to [reference previous failure]."

**User keeps expanding scope mid-interview**
→ "That's a great idea for a follow-up issue. For THIS change, let's stay focused on [original scope]. I'll note the expansion for later."

## Success Criteria

This skill succeeded if:
- The user said "yes" to the alignment summary
- You can list 3+ specific acceptance criteria
- You know which files to touch AND which to avoid
- You identified at least one risk or tradeoff

---

## Auto-Activation & Cross-References

**This skill auto-activates when:** See description frontmatter for trigger keywords.

**Chains to (downstream only — no circular loops):**
- `grill-with-docs` — typically used after this skill completes
- `to-prd` — typically used after this skill completes

**Base layer always active:**
- `aaa-anti-patterns` — quality gates on every output
- `optimized-workflow` — execution rules on every task
- `e2e-validation` — test requirements on every production write
