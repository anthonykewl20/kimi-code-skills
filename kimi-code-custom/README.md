# 🚀 Kimi Code Skills — Complete Setup Guide

> **Production-ready adaptation** of Matt Pocock's *Skills for Real Engineers* and Andrej Karpathy's *Behavioral Guidelines* for **Kimi Code CLI**.

---

## 📋 What You're Getting

This package installs **14 battle-tested skills** and **1 behavioral foundation file** that transform Kimi Code from a "vibe coder" into a **disciplined senior engineer**.

| Component | Source | Purpose |
|---|---|---|
| `AGENTS.md` | Karpathy-inspired | Behavioral floor — prevents assumptions, bloat, and orthogonal damage |
| `grill-me` | Matt Pocock | Alignment interview before any code is written |
| `grill-with-docs` | Matt Pocock | Alignment + builds `CONTEXT.md` ubiquitous language |
| `tdd` | Matt Pocock | Red-green-refactor enforcement at the agent level |
| `diagnose` | Matt Pocock | Disciplined debugging loop: reproduce → minimize → hypothesize → instrument → fix |
| `improve-codebase-architecture` | Matt Pocock | Entropy reversal — rescues ball-of-mud codebases |
| `caveman` | Matt Pocock | Ultra-compressed communication — cuts token usage ~75% |
| `handoff` | Matt Pocock | Multi-agent bridge — compact conversation for another agent to continue |
| `git-guardrails` | Matt Pocock | Runtime hooks that block dangerous git commands |
| `to-prd` | Matt Pocock | Synthesize conversation into a PRD (filed as GitHub issue) |
| `to-issues` | Matt Pocock | Break PRD into vertical-slice GitHub issues |
| `triage` | Matt Pocock | State-machine issue triage through structured roles |
| `zoom-out` | Matt Pocock | Force agent to explain code in system-wide context |
| `prototype` | Matt Pocock | Build throwaway prototypes before committing to implementation |
| `setup-kimi-skills` | This package | One-time scaffold: issue tracker, labels, docs layout |

---

## ⚡ Quick Start (2 Minutes)

### Step 1: Install Skills

```bash
# Clone this repo anywhere
git clone https://github.com/your-org/kimi-code-skills.git
cd kimi-code-skills

# Install all skills into your global Kimi skills directory
./install.sh
```

What `install.sh` does:
1. Detects your OS and Kimi Code installation
2. Creates `~/.kimi/skills/` (or uses `~/.config/agents/skills/` as fallback)
3. Copies all 14 skill directories with their `SKILL.md` files
4. Copies hook scripts to `~/.kimi/hooks/`
5. Appends hook configurations to `~/.kimi/config.toml`
6. Verifies installation with `kimi /skill:list`

### Step 2: Add Behavioral Foundation to Your Project

```bash
# For a NEW project
curl -o AGENTS.md https://raw.githubusercontent.com/your-org/kimi-code-skills/main/AGENTS.md

# For an EXISTING project (append)
echo "" >> AGENTS.md
curl https://raw.githubusercontent.com/your-org/kimi-code-skills/main/AGENTS.md >> AGENTS.md
```

### Step 3: Run Setup Skill in Kimi Code

```bash
cd your-project
kimi
```

Inside Kimi Code:
```
/skill:setup-kimi-skills
```

This will:
- Ask which issue tracker you use (GitHub, Linear, or local files)
- Ask what labels you use for triage
- Ask where to save docs (`docs/adr/`, `wiki/`, etc.)
- Create the initial `CONTEXT.md` scaffold

### Step 4: Start Using Skills

```
# Before building ANY feature — align first
/skill:grill-with-docs

# Then implement with TDD discipline
/skill:tdd

# When a bug appears
/skill:diagnose

# Once a week, rescue your codebase
/skill:improve-codebase-architecture
```

---

## 🏗️ Architecture: How Kimi Code Loads These

### Skill Discovery (Layered Loading)

Kimi Code CLI uses a **priority-ordered discovery mechanism**:

```
Project > User > Extra > Built-in
```

**User-level skills** (global, all projects):
- `~/.kimi/skills/` ← **We install here (brand group, highest priority)**
- `~/.config/agents/skills/` (generic group, fallback)

**Project-level skills** (repo-specific):
- `.kimi/skills/` (inside your project root)
- `.agents/skills/` (generic group)

When a skill name collision occurs, the **more specific scope wins**.

### Progressive Disclosure (The Secret Sauce)

This is why these skills are revolutionary and not just "long prompts":

| Level | What Gets Loaded | When | Token Cost |
|---|---|---|---|
| **Level 1** | YAML frontmatter only (`name`, `description`) | Kimi startup | ~50 tokens per skill |
| **Level 2** | Full `SKILL.md` body | When skill is matched to task | <3,000 tokens |
| **Level 3** | Deep references (`scripts/`, `references/`) | Only when explicitly needed | Unlimited, lazy-loaded |

**Result:** You can install 50 skills and Kimi's startup context barely grows. The AI only reads the full skill when your task actually needs it.

### How Skills Are Invoked

1. **Manual**: Type `/skill:<name>` (e.g., `/skill:tdd`)
2. **Auto-match**: Kimi reads the skill descriptions at startup. When you say "I need to add validation to the login form," Kimi matches your intent to the `tdd` skill description and loads it automatically.
3. **Flow skills**: Type `/flow:<name>` for multi-step automated workflows (Mermaid diagrams).

### Hooks System (Runtime Enforcement)

Kimi Code supports **13 lifecycle hook events**:

| Event | Trigger | Use Case |
|---|---|---|
| `PreToolUse` | Before any tool call | **Block dangerous commands**, inject context |
| `PostToolUse` | After tool succeeds | Auto-format code, run linters |
| `PostToolUseFailure` | After tool fails | Retry logic, alert notifications |
| `UserPromptSubmit` | Before user input processed | Add project context, validate input |
| `Stop` | When agent turn ends | Verify task completion |
| `SessionStart` | Session created/resumed | Load project state |
| `Notification` | When approval needed | Desktop alerts |

**Git guardrails use `PreToolUse`** to intercept `Shell` tool calls and block dangerous git commands before Kimi executes them.

---

## 📁 File Structure After Installation

```
~/.kimi/
├── skills/
│   ├── setup-kimi-skills/
│   │   └── SKILL.md
│   ├── grill-me/
│   │   └── SKILL.md
│   ├── grill-with-docs/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── context-template.md
│   ├── tdd/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── good-tests.md
│   │       └── bad-tests.md
│   ├── diagnose/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── debugging-patterns.md
│   ├── improve-codebase-architecture/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── deep-modules.md
│   ├── caveman/
│   │   └── SKILL.md
│   ├── handoff/
│   │   └── SKILL.md
│   ├── git-guardrails/
│   │   └── SKILL.md
│   ├── to-prd/
│   │   └── SKILL.md
│   ├── to-issues/
│   │   └── SKILL.md
│   ├── triage/
│   │   └── SKILL.md
│   ├── zoom-out/
│   │   └── SKILL.md
│   └── prototype/
│       └── SKILL.md
├── hooks/
│   ├── block-dangerous-git.sh
│   └── protect-env.sh
└── config.toml  ← (hooks appended here)

your-project/
├── AGENTS.md          ← Karpathy behavioral guidelines (project root)
├── CONTEXT.md         ← Generated by grill-with-docs
├── docs/
│   └── adr/           ← Architecture Decision Records
└── .kimi/
    └── skills/        ← (optional) project-specific overrides
```

---

## 🎯 Real-World Workflow Examples

### Workflow A: Building a New Feature (The "Right Way")

```bash
$ cd my-project
$ kimi
```

```
# Step 1: Align
> I want to add a "remember me" feature to the login page

Kimi: I see you want to add a "remember me" feature. Let me run the alignment skill first.
[Auto-loads /skill:grill-with-docs]

Kimi: Before I write any code, I need to clarify:
1. Should "remember me" persist across browser sessions or just within the session?
2. What's the security policy for token storage? (localStorage vs secure httpOnly cookie)
3. Should this apply to all auth methods or just password login?
4. What's the max duration before re-authentication is required?

> 1. Across sessions. 2. Secure httpOnly cookie. 3. All methods. 4. 30 days.

Kimi: Got it. I'll update CONTEXT.md with these terms: "persistent session", "secure cookie storage", "universal auth", "30-day re-auth window". Now let me create the PRD.
[Auto-loads /skill:to-prd]

# Step 2: Plan
Kimi: PRD created as GitHub issue #42. Breaking into vertical slices:
- Issue #43: Add "remember_me" column to users table (migration)
- Issue #44: Implement secure cookie generation and validation
- Issue #45: Add UI checkbox to login form
- Issue #46: Wire checkbox to auth flow
[Auto-loads /skill:to-issues]

# Step 3: Implement with TDD
> Let's start with issue #44

Kimi: Loading TDD skill.
[Auto-loads /skill:tdd]

Kimi: RED — Writing failing test: "should reject expired remember-me cookie"
Kimi: RED confirmed — test fails as expected.
Kimi: GREEN — Implementing cookie validation with 30-day TTL...
Kimi: REFACTOR — Extracting cookie parser into reusable module...

# Step 4: Architecture check
> /skill:improve-codebase-architecture

Kimi: Scanning codebase... Found 2 deepening opportunities:
1. Auth module is shallow (7 public methods, 3 used externally). Consider facade pattern.
2. Cookie utilities scattered across 3 files. Consolidate into `src/security/cookies/`.
```

### Workflow B: Debugging a Production Issue

```
> The payment webhook is failing intermittently. /skill:diagnose

Kimi: Starting disciplined diagnosis loop.

Step 1 — REPRODUCE: I'll check logs for the last 10 webhook failures...
Step 2 — MINIMISE: All failures share one trait: they occur when the invoice total > $999.99
Step 3 — HYPOTHESISE: Possible floating-point precision issue in amount validation
Step 4 — INSTRUMENT: Adding targeted logging to payment gateway adapter...
Step 5 — FIX: The validation uses `parseFloat` which loses precision at 3+ decimal places. Switching to integer cents representation.
Step 6 — REGRESSION TEST: Writing test for $999.99, $1000.00, and $10000.00 edge cases...
```

### Workflow C: Multi-Agent Handoff

```
# Agent A (Research phase)
> /skill:handoff

Kimi: Compacting conversation into handoff document...
Saved to `.kimi/handoffs/2026-05-17-auth-refactor.md`

# Later, Agent B (Implementation phase)
$ kimi --session implementation
> /import .kimi/handoffs/2026-05-17-auth-refactor.md

Kimi: Loaded handoff. I see the research phase identified:
- 3 candidate libraries for JWT handling
- Decision: Use `jose` (smallest bundle, best Edge runtime support)
- Risk: Need custom refresh token rotation
- Next: Implement token pair generation with TDD discipline
```

---

## 🔒 Security: Hooks Deep Dive

### Git Guardrails Hook

**What it blocks:**
- `git push` to protected branches (main, master, production)
- `git reset --hard`
- `git clean -f`
- `git branch -D` on branches with unpushed commits
- Force pushes (`git push --force`, `git push -f`)

**How it works:**
1. Kimi calls `Shell` tool with a git command
2. `PreToolUse` hook fires, receives JSON via stdin:
   ```json
   {
     "tool_name": "Shell",
     "tool_input": {"command": "git push origin main"}
   }
   ```
3. Hook script checks against blocklist regex
4. If blocked, exits with code `2` and sends stderr to Kimi:
   ```
   ❌ BLOCKED: Direct push to 'main' is not allowed.
   Use Pull Requests instead. Run `git checkout -b feature/xxx` to create a branch.
   ```
5. Kimi receives the correction and adapts its plan

### Environment File Protection Hook

Blocks accidental writes to `.env`, `.env.local`, `.env.production`:
```toml
[[hooks]]
event = "PreToolUse"
matcher = "WriteFile|StrReplaceFile"
command = "~/.kimi/hooks/protect-env.sh"
timeout = 10
```

---

## ⚙️ Configuration Reference

### `~/.kimi/config.toml` (Hooks Section)

After running `install.sh`, your config will include:

```toml
# ============================================
# KIMI CODE SKILLS — HOOKS CONFIGURATION
# ============================================

# Auto-format after file edits
[[hooks]]
event = "PostToolUse"
matcher = "WriteFile|StrReplaceFile"
command = "jq -r '.tool_input.file_path' | xargs prettier --write"
timeout = 30

# Block dangerous git commands
[[hooks]]
event = "PreToolUse"
matcher = "Shell"
command = "~/.kimi/hooks/block-dangerous-git.sh"
timeout = 10

# Block edits to .env files
[[hooks]]
event = "PreToolUse"
matcher = "WriteFile|StrReplaceFile"
command = "~/.kimi/hooks/protect-env.sh"
timeout = 10

# Desktop notification when approval needed
[[hooks]]
event = "Notification"
matcher = "permission_prompt"
command = "osascript -e 'display notification "Kimi needs attention" with title "Kimi CLI"'"

# Verify tasks complete before stopping
[[hooks]]
event = "Stop"
command = "~/.kimi/hooks/check-complete.sh"
timeout = 30
```

### Custom Skills Directory

If you want skills in a different location:

```bash
# Option 1: CLI flag
kimi --skills-dir /path/to/my-skills

# Option 2: Config file (additive)
# In ~/.kimi/config.toml:
extra_skill_dirs = [
    "~/my-skills-collection",
    ".claude/plugins/my-skills",
    "/opt/team-shared/skills"
]
```

---

## 🛠️ Troubleshooting

### "Skill not found"

```bash
# Check if skills are discovered
kimi /skill:list

# If empty, verify directory structure:
ls ~/.kimi/skills/
# Should show: setup-kimi-skills, grill-me, tdd, diagnose, etc.

# Check permissions
chmod 755 ~/.kimi/skills/*/SKILL.md
```

### "Hooks not firing"

```bash
# Verify hook config loaded
kimi /hooks

# Check hook script permissions
chmod +x ~/.kimi/hooks/*.sh

# Test hook manually
echo '{"tool_name":"Shell","tool_input":{"command":"git push"}}' | ~/.kimi/hooks/block-dangerous-git.sh
echo $?  # Should output 2 (blocked)
```

### "AGENTS.md not being read"

Kimi Code **does** read `AGENTS.md` automatically via the `KIMI_AGENTS_MD` builtin variable injected into the system prompt. citeweb_search:9#6 However, if you're using the **VS Code Extension**, there was a feature request (issue #850) for auto-loading that may still be pending. citeweb_search:8#14 

**Workaround for VS Code Extension:**
```
@AGENTS.md Please follow these guidelines for this project.
```

**CLI always works** — `AGENTS.md` is automatically injected on session start.

---

## 📚 Philosophy: Why This Works

### The Four Failure Modes (Matt Pocock)

| # | Failure Mode | Skill Fix | Engineering Principle |
|---|---|---|---|
| 1 | Agent didn't do what I want | `grill-me`, `grill-with-docs` | *The Pragmatic Programmer* — "No one knows exactly what they want" |
| 2 | Agent is way too verbose | `CONTEXT.md` ubiquitous language | *Domain-Driven Design* — shared language between devs and domain experts |
| 3 | Code doesn't work | `tdd`, `diagnose` | *Extreme Programming* — feedback loops are your speed limit |
| 4 | Built a ball of mud | `improve-codebase-architecture` | *A Philosophy of Software Design* — invest in design every day |

### The Four Behavioral Principles (Karpathy)

| Principle | What It Prevents | Real-World Cost Without It |
|---|---|---|
| Think Before Coding | Wrong assumptions, hidden confusion | 3-hour rewrite because the agent built the wrong feature |
| Simplicity First | Overcomplicated APIs, bloated abstractions | 1000-line module that should be 100 lines, unmaintainable |
| Surgical Changes | Orthogonal damage, breaking adjacent code | "Fix the bug" breaks 3 unrelated features in the diff |
| Goal-Driven Execution | Vague tasks, unverifiable work | "Make it work" → works on agent's machine, fails in production |

---

## 🔄 Updating Skills

```bash
# Pull latest skills
cd ~/kimi-code-skills
git pull origin main

# Re-run installer
./install.sh

# Or update specific skill
cp -r skills/tdd ~/.kimi/skills/tdd
```

---

## 📝 License

MIT — Fork, adapt, and share. These are **open ideas**, not proprietary code.

---

> *"Software engineering fundamentals matter more than ever. These skills are my best effort at condensing these fundamentals into repeatable practices, to help you ship the best apps of your career."* — Matt Pocock
