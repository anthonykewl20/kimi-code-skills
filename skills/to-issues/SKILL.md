---
name: to-issues
description: Breaks PRD into vertical-slice GitHub issues. Triggers: user says 'break into issues', 'vertical slices', 'parallel development', OR after a PRD exists and >3 implementation steps are identified.

---

# /to-issues — PRD to Vertical Slices

> "The best way to eat an elephant is one bite at a time." — But only if each bite is independently edible.

## When to Use

- After `/skill:to-prd` has created a PRD
- When a feature is too large for one PR
- When you want parallel development (multiple agents or devs)
- When you need incremental delivery

## When NOT to Use

- For trivial features that fit in one PR
- When the user wants everything in one go
- When the PRD is already broken into tasks

## What This Skill Does

1. Reads the PRD
2. Identifies vertical slices (end-to-end behaviors)
3. Creates one GitHub issue per slice
4. Links issues with "Blocked by" / "Blocks" relationships
5. Labels issues for triage

## Vertical Slicing Rules

### What IS a Vertical Slice

A vertical slice delivers **one complete user-visible behavior** from top to bottom:

```
User Action → UI → API → Business Logic → Database → Response → UI Update
```

Example: "User can register with email and password"
- Includes: form UI, validation, API endpoint, user creation, email dispatch, success screen
- Does NOT include: password reset, social login, admin dashboard

### What is NOT a Vertical Slice

**Horizontal layers (WRONG):**
- "Create database schema" (no user value)
- "Build API endpoints" (no UI to use them)
- "Write frontend components" (no backend to populate them)

**Technical tasks (WRONG):**
- "Set up Redis" (infrastructure, not behavior)
- "Add logging" (cross-cutting, not a feature)
- "Refactor auth module" (should be its own issue, not part of a feature slice)

## Process

### Step 1: Read PRD

Read the PRD issue or file. Identify:
- Core behaviors (user stories)
- Supporting infrastructure (auth, logging, etc.)
- Nice-to-haves vs must-haves

### Step 2: Identify Slices

For each user-visible behavior, create a slice:

```
PRD: "Build a course platform with lessons, sections, and progress tracking"

Slices:
1. "User can view a list of available courses"
2. "User can enroll in a course"
3. "User can view lessons within a section"
4. "User can mark a lesson as complete"
5. "User can see overall course progress"
6. "User can resume from last viewed lesson"
```

### Step 3: Size Check

Each slice should be:
- **Completable in 1-2 days** by one developer
- **Reviewable in <30 minutes**
- **Deployable independently** (feature flags if needed)

If a slice is too big, split it:
```
"User can enroll in a course" → too big?
Split into:
- "User can view course details before enrolling"
- "User can pay for a course"
- "User can access enrolled course content"
```

### Step 4: Create Issues

For each slice, create an issue with this template:

```markdown
# [Slice Name]

## Parent PRD
[Link to PRD issue]

## Acceptance Criteria
- [ ] [Specific, verifiable criterion]
- [ ] [Specific, verifiable criterion]
- [ ] [Specific, verifiable criterion]

## Technical Notes
- [Files to touch]
- [Dependencies]
- [Risks]

## Out of Scope
- [What's NOT included in this slice]

## Related Issues
- Blocked by: #[issue]
- Blocks: #[issue]
```

### Step 5: Link and Label

```bash
# Add "Blocked by" relationships
gh issue edit 43 --body "Blocked by: #42"
gh issue edit 44 --body "Blocked by: #43"

# Add labels
gh issue edit 43 --add-label "slice,backend"
gh issue edit 44 --add-label "slice,frontend"
```

### Step 6: Present to User

```
I've broken the PRD into [N] vertical slices:

1. #[issue] — [name] — [effort estimate]
2. #[issue] — [name] — [effort estimate]
3. #[issue] — [name] — [effort estimate]

Dependencies:
- #43 must be done before #44
- #45 and #46 can be done in parallel

Ready to start with slice #1?
```

## Edge Cases

**"All slices depend on infrastructure setup"**
→ Create a "Slice 0: Infrastructure Setup" issue. But keep it minimal — only what's needed for Slice 1. Don't build the entire infrastructure upfront.

**"The PRD has 20 behaviors"**
→ Group related behaviors into "epic" issues, then slice the first epic. Don't create 20 issues at once — it's overwhelming.

**"Some slices share code"**
→ That's fine. Each slice still delivers end-to-end value. The shared code will be built in the first slice that needs it.

## Success Criteria

This skill succeeded if:
- Each issue represents one complete user-visible behavior
- Issues can be developed and deployed independently
- Dependencies are clearly marked
- No issue is too large for a single PR
- The user can pick any issue and understand what to build

---

## Auto-Activation & Cross-References

**This skill auto-activates when:** See description frontmatter for trigger keywords.

**Chains to (downstream only — no circular loops):**
- `triage` — typically used after this skill completes
- `tdd-workflow` — typically used after this skill completes

**Base layer always active:**
- `aaa-anti-patterns` — quality gates on every output
- `optimized-workflow` — execution rules on every task
- `e2e-validation` — test requirements on every production write
