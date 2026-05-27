---
name: setup-kimi-skills
description: One-time scaffold for the Kimi Code Skills system. Configures issue tracker, triage labels, and docs layout so other skills can consume them.
---

# Setup Kimi Code Skills

Run this skill **once per repository** before using any other engineering skills (`to-issues`, `to-prd`, `triage`, `diagnose`, `tdd`, `improve-codebase-architecture`, or `zoom-out`).

## What This Does

1. Detects your issue tracker (GitHub, Linear, or local files)
2. Configures triage label vocabulary
3. Sets up docs directory layout (`docs/adr/`, `CONTEXT.md`)
4. Creates `.kimi/skills/` project override directory (optional)

## Pre-Conditions

- You are in the project root directory
- You have initialized a git repository (`git init` or cloned)

## Step-by-Step

### Step 1: Detect Issue Tracker

Check for issue tracker signals in the project:

```bash
# GitHub
ls .github/ISSUE_TEMPLATE* 2>/dev/null
ls .github/workflows/ 2>/dev/null
git remote -v | grep github

# Linear
ls .linear/ 2>/dev/null
grep -r "linear.app" . 2>/dev/null | head -5

# Jira
ls .jira/ 2>/dev/null
grep -r "atlassian.net" . 2>/dev/null | head -5
```

**Ask the user:**
> Which issue tracker do you use for this project?
> 1. GitHub Issues
> 2. Linear
> 3. Jira
> 4. Local files only (no external tracker)
> 5. Other (please specify)

Record the answer in `.kimi/skills-config.toml`:

```toml
[issue_tracker]
type = "github"  # or "linear", "jira", "local", "other"
project = "owner/repo"  # for GitHub
# team = "TEAM-KEY"     # for Linear
```

### Step 2: Configure Triage Labels

**Ask the user:**
> What labels do you apply to issues when you triage them? (e.g., `bug`, `feature`, `tech-debt`, `blocked`, `needs-design`)

Record in `.kimi/skills-config.toml`:

```toml
[triage]
labels = ["bug", "feature", "tech-debt", "blocked", "needs-design"]
states = ["backlog", "todo", "in-progress", "review", "done"]
```

### Step 3: Set Up Docs Layout

**Ask the user:**
> Where do you want to save documentation created by skills?
> 1. `docs/` (default)
> 2. `wiki/`
> 3. `adr/` (Architecture Decision Records only)
> 4. Other path

Create the directory structure:

```bash
mkdir -p docs/adr
mkdir -p docs/context
touch docs/adr/.gitkeep
touch docs/context/.gitkeep
```

Record in `.kimi/skills-config.toml`:

```toml
[docs]
adr_dir = "docs/adr"
context_dir = "docs/context"
```

### Step 4: Create CONTEXT.md Scaffold

Create `CONTEXT.md` at project root with a template:

```markdown
# Domain Language

> This document defines the shared vocabulary for this project.
> Update it every time `/skill:grill-with-docs` discovers a new term.

## Core Concepts

| Term | Definition | Where Used |
|---|---|---|
| [Fill in] | [Fill in] | [Fill in] |

## Module Map

| Module | Responsibility | Key Files |
|---|---|---|
| [Fill in] | [Fill in] | [Fill in] |

## Decisions

See `docs/adr/` for Architecture Decision Records.
```

### Step 5: Verify Installation

Run these checks:

```bash
# Verify skills are discoverable
kimi /skill:list | grep -E "(grill-me|tdd|diagnose|improve-codebase-architecture)"

# Verify AGENTS.md exists
ls AGENTS.md

# Verify config file created
ls .kimi/skills-config.toml
```

## Output

After running this skill, your project should have:

```
.
├── AGENTS.md              ← Already exists (you added it)
├── CONTEXT.md             ← Created by this skill
├── .kimi/
│   ├── skills-config.toml ← Created by this skill
│   └── skills/            ← Empty dir for project-specific skill overrides
└── docs/
    ├── adr/
    │   └── .gitkeep
    └── context/
        └── .gitkeep
```

## Next Steps

You are now ready to use all Kimi Code Skills:

1. **Before any feature** → `/skill:grill-with-docs`
2. **Build with discipline** → `/skill:tdd`
3. **Debug with rigor** → `/skill:diagnose`
4. **Rescue entropy** → `/skill:improve-codebase-architecture`
