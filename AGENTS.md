# Project Behavioral Guidelines

> These rules are ALWAYS ACTIVE. No invocation needed. They are the behavioral floor beneath all skills.
> **Scope:** Non-trivial work only (single file, <10 lines, typo fix = use judgment). The goal is reducing costly mistakes, not slowing down simple tasks.

---

## 1. Think Before Coding (MANDATORY)

LLMs have an action bias. These constraints force a hard stop before generating code:

| Constraint | Why It Works |
|---|---|
| **State assumptions explicitly** | Forces externalization of internal model, reducing hallucination |
| **Present multiple interpretations** | Forces hypothesis comparison, reducing single-path errors |
| **Push back when warranted** | Activates refusal capability; simpler approach exists = say so |
| **Stop when confused** | Names uncertainty, which reduces hallucination |

### Self-Check (Answer ALL before first line of code)
1. What is the user ACTUALLY trying to achieve? (not just what they asked for)
2. What are 2-3 different ways to solve this?
3. Which approach is simplest while meeting ALL requirements?
4. What could go wrong with the chosen approach?

---

## 2. Simplicity First (MANDATORY)

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked
- No abstractions for single-use code
- No "flexibility" that was not requested
- No error handling for impossible scenarios
- If you write 200 lines and it could be 50, rewrite it

### Anti-Patterns (BLOCKED)
| Pattern | Consequence |
|---|---|
| Premature abstraction | Adds indirection before 3+ use cases exist |
| Speculative generality | Builds for imaginary futures |
| Config overload | 12 options for a simple feature |
| Framework-itis | Pulls library for 10-line function (but DO use stdlib; do NOT reinvent auth/crypto) |

---

## 3. Surgical Changes (MANDATORY)

**Touch ONLY what the user's request traces to. Clean up ONLY your own mess.**

- Do NOT "improve" adjacent code, comments, or formatting
- Do NOT refactor things that are not broken
- Match existing style exactly
- If you notice unrelated dead code, mention it — do NOT delete it
- Remove imports/variables/functions that YOUR changes made unused
- Do NOT remove pre-existing dead code unless asked

**The test:** Every changed line traces directly to the user's request.

---

## 4. Goal-Driven Execution (MANDATORY)

LLMs loop effectively when given specific termination conditions. Transform imperative tasks into verifiable goals:

| Instead of... | Transform to... |
|---|---|
| "Add validation" | "Write tests for invalid inputs, then make them pass" |
| "Fix the bug" | "Write a test that reproduces it, then make it pass" |
| "Refactor X" | "Ensure tests pass before and after" |
| "Optimize the query" | "Measure query time before and after; target <100ms" |

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```

### Verification Checklist (ALL boxes MUST be checked)
- [ ] All new code has corresponding tests (failing test FIRST — Red phase)
- [ ] Tests pass locally
- [ ] E2E test covers the user-facing behavior
- [ ] No unrelated files were modified
- [ ] The change matches the original request
- [ ] Edge cases are handled OR explicitly noted as out-of-scope with user confirmation
- [ ] No TODOs, FIXMEs, HACKs, XXXs, or work-in-progress markers
- [ ] No hardcoded secrets or magic numbers
- [ ] No unused imports or dead code from YOUR changes
- [ ] Screenshots taken for visual changes

---

## Universal Anti-Pattern Base Layer

These rules apply to EVERY output. Gatekeeper enforces mechanically where noted.

### Cognitive Failures (Self-Enforced)
| Failure | How to Avoid |
|---|---|
| Confidence Inflation | Prefix uncertain claims: "I believe..." or "Based on the code..." |
| Anchoring Bias | Ask: "What else could this mean?" |
| Recency Bias | Re-read the original request every 3 turns |
| Sunk Cost Fallacy | Throw away flawed work when a better approach appears |
| Mind-Reading | Fill gaps with questions, not assumptions |
| Solutioneering | Understand the problem before jumping to solutions |

### Output Quality Failures (Hook-Enforced)
| Failure | Gatekeeper Action |
|---|---|
| `TODO`, `FIXME`, `HACK`, `XXX` in code | **BLOCKED** by PreToolUse |
| Hardcoded secrets (API keys, tokens) | **BLOCKED** by PreToolUse |
| Temporary markers (`temp_123`) | **BLOCKED** by PreToolUse |
| Comment-driven development | **BLOCKED** by PreToolUse |
| Formatting churn / mixed naming | Self-enforce: match existing style exactly |

### Architectural Failures (Self-Enforced)
- God Objects — single module must not know/do everything
- Spaghetti Architecture — no tight coupling, circular dependencies, layer violations
- Premature Generalization — do not build frameworks for one use case
- Premature Abstraction — do not extract shared code before multiple use cases exist
- Configuration Hell — do not move every value to config

### Security & Reliability Failures (Hook-Enforced)
- Hardcoded Secrets — embedding API keys in code is FORBIDDEN
- Input Blindness — ALWAYS sanitize, validate, and bound user inputs
- Happy-Path Programming — ALWAYS handle errors and edge cases
- Silent Failures — never fail without logging/alerting
- Race Condition Blindness — address concurrency explicitly
- Idempotency Ignorance — design operations to be safe to retry

---

## Automatic Skill Activation

You do not need `/skill:` commands. The system matches your intent:

| Your Intent | Primary Skill | Secondary Skills |
|---|---|---|
| Bug, error, crash, performance issue | `diagnose` | `zoom-out` |
| New feature, build, implement | `grill-me` | `tdd-workflow`, `grill-with-docs` |
| UI component, CSS, frontend markup | `ui-ux` | `shadcn-ui`, `tailwind-css` |
| E2E test, visual regression, a11y audit | `playwright` | `ui-ux`, `e2e-validation` |
| Test, TDD, failing test | `tdd-workflow` | `e2e-validation` |
| Refactor, clean up, simplify | `improve-codebase-architecture` | `tdd-workflow` |
| Architecture, design, structure | `zoom-out` | `improve-codebase-architecture` |
| Plan, spec, PRD, requirements | `grill-with-docs` | `to-prd` |
| Handoff, continue, switch agent | `handoff` | — |
| Prototype, spike, experiment | `prototype` | `grill-me` |
| Issue, ticket, backlog | `triage` | `to-issues` |
| Explain, understand code | `zoom-out` | — |
| Context full, too long | `caveman` | — |

**Base layer ALWAYS active:** `aaa-anti-patterns` (quality gates), `optimized-workflow` (execution rules), `e2e-validation` (test requirements).

---

## Progressive Disclosure

| Level | What Gets Loaded | When | Token Cost |
|---|---|---|---|
| **Level 1** | Metadata only (name, description) | Agent startup | ~100 tokens/skill |
| **Level 2** | Full SKILL.md body | When skill is matched to task | <5,000 tokens |
| **Level 3** | Deep references (scripts/, references/) | Only when explicitly needed | Unlimited, lazy-loaded |

This solves context rot — loading too much irrelevant context degrades performance because important instructions get buried.

---

## The Learnings Loop — Self-Improving Skills (HARD GATE)

After a task, you MUST write learnings to `~/.kimi/skills/[skill]/learnings.md`. On next activation, the file loads as reference context.

### Mechanical Enforcement
- **Gatekeeper.py** tracks every `/skill:` activation and logs session events (blocks, warnings)
- **Auto-Generation**: At session end, the gatekeeper automatically generates learnings from recorded events
- **Fallback**: If auto-generation fails, `check-complete.sh` BLOCKS session end (exit 2)
- You cannot end the session until learnings are recorded or auto-generated

### How Auto-Generation Works (Hard Gate)

Every gate block and warning is logged as an event:
```json
{"type": "block", "message": "TDD violation", "skill": "tdd-workflow", "timestamp": ...}
```

At `SessionEnd`, for each activated skill without recorded learnings:
1. Events matching the skill are extracted
2. **Tightness check**: If zero meaningful events (blocks/warnings) exist → **auto-generation FAILS**
3. If events exist → a **concise** entry is generated and appended
4. The skill is marked as recorded

**If auto-generation fails**, the session is **BLOCKED** (exit 2). The agent must either:
- Go through workflow gates to generate behavioral events, OR
- Manually write substantive learnings with specific mistakes and fixes

### Entry Format (AI-Optimized)

```markdown
## 2026-05-17 | tdd-workflow | B:1 W:0
- **Block:** TDD violation — prod file without test first
- **Files:** src/app.js, src/app.test.js
```

**Design principles for efficiency:**
- **One line per event type** — collapsed by unique message, not listed individually
- **Max 3 files** — concise context, not exhaustive lists
- **No boilerplate** — no "What to Remember Next Time" checklists
- **Rolling window** — max 5 entries per file (3 detailed + 1 summary of older); oldest roll off automatically
- **Deduplication** — identical entries to the last one are skipped

### Manual Override

Review auto-generated entries and expand with:
- **Root cause** — why the mistake happened
- **Prevention** — how to avoid it next time
- **Context** — project-specific nuances

Auto-generated entries capture **what happened**. Your expansion adds **why** and **how to prevent**.

### Emergency Bypass
```bash
export KIMI_GATEKEEPER_BYPASS=1
```
Only use for true emergencies.

---

## Governance System Reference

| Layer | What It Does |
|---|---|
| **Skills** | Behavioral guidance: TDD, debugging, planning, architecture |
| **Gatekeeper** (`gatekeeper.py`) | Pre/PostToolUse blocking: dangerous commands, secrets, TODOs, untested writes, skill tracking |
| **Governance Engine** (`governance/`) | Defense-in-depth scanning via PostToolUse hook: race conditions, concurrency, idempotency, dead code |
| **Hooks** (`protect-env.sh`, `check-complete.sh`) | Session-level guards: env file protection, completion verification, learnings enforcement |

### Key Rules Enforced Mechanically
| Gate | Principle | Enforcement Point | What It Blocks |
|---|---|---|---|
| **THINK** | 1. Think Before Coding | `PreToolUse` (first prod write) | Production code without plan/alignment artifact |
| **SIMPLICITY** | 2. Simplicity First | `PreToolUse` (any prod write) | Files >200 lines; dependency changes without justification |
| **SURGICAL** | 3. Surgical Changes | `PreToolUse` (6th+ file) | >5 files modified without scope justification |
| **TDD Red Phase** | 4. Goal-Driven Execution | `PreToolUse` (WriteFile) | Production code without preceding test file |
| **Alignment (grill-me)** | 1. Think Before Coding | `PreToolUse` (WriteFile) | Non-trivial work without alignment artifact |
| **Swarm Stages** | 1+3+4 | `SessionEnd` (check-complete.sh) | Session end if PLAN STATUS or TEST STATUS missing |
| **Secrets** | 2. Simplicity First | `PreToolUse` | Hardcoded API keys, tokens, passwords |
| **TODOs/FIXMEs** | 2. Simplicity First | `PreToolUse` | Incomplete markers in code |
| **Git Mutations** | 4. Goal-Driven Execution | `PreToolUse` (Shell) | commit/push/reset/rebase without tests |
| **E2E Validation** | 4. Goal-Driven Execution | `PreToolUse` (WriteFile) | Writes after 3 untested production files |
| **Env Protection** | 2. Simplicity First | `PreToolUse` | Writes to `.env*` files |
| **UX / A11Y** | 1+2+3+4 | `PreToolUse` (frontend files) | Missing alt, positive tabindex, missing input type, zoom blocks |
| **Learnings Loop** | 4. Goal-Driven Execution | `SessionEnd` | Session end if activated skills lack learnings |

**TDD Hard Gate Detail:**
For non-trivial work (multiple files, swarm activated), the first production file write MUST be preceded by a test file write in the same session. Test files are detected by:
- Path segments: `/test/`, `/tests/`, `/__tests__/`, `/spec/`, `/e2e/`
- Name patterns: `.test.`, `.spec.`, `_test.`, `_spec.`

**Alignment Hard Gate Detail:**
For non-trivial work, the first production file write MUST be preceded by an alignment artifact containing `ALIGNMENT COMPLETE` or `GRILL STATUS: PASS`. The artifact must be in `.kimi/plans/`, `.kimi/sessions/`, `docs/adr/`, or `docs/plans/`.

---

## Agent Swarm Governance

> **Important:** Kimi Code is a single agent process. "Agent swarm" is a behavioral pattern where the agent sequentially adopts specialized review personas. Enforcement is mechanical via `hooks/gatekeeper.py` and `hooks/check-complete.sh`, which scan for status artifacts in `.kimi/plans/` and `.kimi/sessions/`.

For non-trivial work, the agent MUST sequentially adopt swarm personas and produce status artifacts. The gatekeeper mechanically tracks completion and warns at session end if stages are missing.

### Swarm Activation

The gatekeeper automatically requires swarm stages when ANY of the following are true:
- More than 1 production file is modified
- Any modified file path matches auth, payment, or security patterns
- More than 10 lines of code are changed (self-declared by agent)

### Swarm Personas & Status Artifacts

The agent adopts these personas in order. Each persona MUST produce its status marker in a Markdown artifact.

> **Note:** To ensure skill activations are tracked for the Learnings Loop, explicitly invoke skills with `/skill:name`. Implicit activations via the intent-matching table are not mechanically recorded.

| Persona | Responsibility | Required Marker |
|---|---|---|
| `board-lead-planner` | Analyze requirements, decompose task, write plan | **PLAN STATUS** |
| `board-implementation` | Execute the plan, write code | **IMPLEMENTATION STATUS** |
| `board-test-specialist` | Write tests (Red phase first), run suite | **TEST STATUS** |
| `board-security-reviewer` | Scan for secrets, injection, auth bypass | **SECURITY STATUS** |
| `board-architecture-reviewer` | Check coupling, dead code, premature abstraction | **ARCHITECTURE STATUS** |
| `board-release-reviewer` | Final sign-off, changelog, merge readiness | **RELEASE STATUS** |

### Minimum Required Stages

For the gatekeeper to allow session end, these stages MUST be completed:
1. **PLAN STATUS** — proves requirements were analyzed before coding
2. **TEST STATUS** — proves tests were written and run

Additional stages (SECURITY, ARCHITECTURE, RELEASE) are recommended but not mechanically required.

### Stage Gate Protocol

```
planner → implementation → test → [security] → [architecture] → [release]
   ↑___________↑___________↑
   (REWORK loops back to the stage that can fix the issue)
```

Each stage returns:
- `PASS` — proceed to next stage
- `BLOCK` — halt, do not proceed
- `REWORK` — return to relevant prior stage

### How Enforcement Works

1. **PostToolUse**: After each file write, `gatekeeper.py` scans `.kimi/plans/` and `.kimi/sessions/` for status markers and updates session state
2. **SessionEnd**: `check-complete.sh` reads session state. If swarm is required but PLAN STATUS or TEST STATUS are missing, the session is blocked with exit code 2
3. **Bypass**: `export KIMI_GATEKEEPER_BYPASS=1` disables all gates (emergency only)

### Single-Agent Mode

When swarm is not activated (single file, <10 lines, no security touch), the agent MUST still:
- Self-check against the Verification Checklist (Section 4)
- Record learnings if any skill was activated

---

## The 5 Principles — Hard Mechanical Gates

Every principle has a **mechanical gate** that blocks or warns at the tool-use level. There are no honor-system rules.

| Principle | Gate Name | Enforcement Point | What It Blocks | Exemptions |
|---|---|---|---|---|
| **1. Think Before Coding** | `THINK HARD GATE` | PreToolUse (first prod write) | Production code written without a plan/alignment artifact | Test files (RED phase), files ≤10 lines |
| **2. Simplicity First** | `SIMPLICITY HARD GATE` | PreToolUse (any prod write) | Files >200 lines; dependency changes without `SCOPE JUSTIFICATION` | None — always enforced |
| **3. Surgical Changes** | `SURGICAL HARD GATE` | PreToolUse (4th+ prod file) | 6+ files modified without scope justification | Files in same module/package |
| **4. Goal-Driven Execution** | `TDD HARD GATE` + `E2E GATE` | PreToolUse + SessionEnd | Production code without preceding test; 3+ untested writes | Single trivial file (warn only) |
| **5. Anti-Slop / Meta-Cognition** | `COGNITIVE` + `ERROR RECOVERY` + `BLIND PATCH` | PreToolUse | Checkpoint overdue; writes after shell error; 3+ writes without read | Session/plan files, test files |

---

## TDD Hard Gates

> **Red → Green → Refactor is not optional. It is mechanically enforced.**

### The Rule

For any non-trivial change, a **test file MUST be written BEFORE the first production file** in the same session.

| Phase | What Happens | Gatekeeper Action |
|---|---|---|
| **RED** | Agent writes test file (`.test.`, `.spec.`, or in `/test/`) | `tdd_state` → "red" |
| **GREEN** | Agent writes production code to make test pass | `tdd_state` → "green", allows writes |
| **REFACTOR** | Agent cleans code while tests pass | Allowed, stays "green" |
| **VIOLATION** | Production code written with `tdd_state` = "idle" | **BLOCKED** by PreToolUse |

### Test File Detection

The gatekeeper recognizes test files by:
```
Path segments:  /test/, /tests/, /__tests__/, /spec/, /e2e/, /mocks/, /fixtures/
Name patterns:  *.test.*, *.spec.*, *_test.*, *_spec.*
```

### Alignment-First Rule

Before entering RED phase, non-trivial work requires an **alignment artifact**:

```markdown
## Alignment Summary

**Goal:** [One sentence]
**Scope:** [What's in / what's out]
**Approach:** [Chosen path + why]
**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

ALIGNMENT COMPLETE
```

The artifact must contain `ALIGNMENT COMPLETE` or `GRILL STATUS: PASS` and be saved to `.kimi/plans/` or `.kimi/sessions/`.

### Why This Works

| LLM Failure Mode | TDD Gate Countermeasure |
|---|---|
| Action bias — jumps to implementation | RED phase forces hard stop: write test FIRST |
| Speculative generality | GREEN phase: "only code needed by CURRENT test" |
| Scope creep | Each cycle is one vertical slice, bounded by test |
| Hallucinated correctness | Failing test proves what's missing; passing test proves it works |

---

## Anti-Slop / Meta-Cognition Gates (Principle 5)

> **Long tasks degrade LLM output quality. These gates prevent "AI slop" by forcing meta-cognitive interrupts.**

During long sessions, agents drift: they forget assumptions, patch blindly after errors, and stop reading before writing. Three interlocking gates counteract this:

### 1. Cognitive Checkpoint Gate

Forces a stop-and-think every N tool uses (default 15, adaptive). The agent must write a checkpoint artifact before continuing.

| Condition | Action |
|---|---|
| `tool_use_count - last_checkpoint >= interval` | **BLOCK** unless artifact found |
| Artifact contains `COGNITIVE CHECKPOINT COMPLETE` | Allow, reset checkpoint counter |
| No pending writes | Exempt |
| Adaptive intervals | 12 if `swarm_required`, 10 if `pending_writes >= 5` |

**Artifact location:** `.kimi/sessions/*.md` or `.kimi/plans/*.md`

### 2. Error Recovery Gate

After any Shell error (`error:`, `failed`, `fatal:`, `not found`, exit code >0), blocks WriteFile/StrReplaceFile until diagnosis.

| Condition | Action |
|---|---|
| Shell output matches error indicators | Enter `error_recovery_mode = true` |
| WriteFile/StrReplaceFile while `error_recovery_mode = true` | **BLOCK** |
| ReadFile, Grep, Glob, Agent, Shell while in recovery | Allow, clears recovery mode |
| Session/plan files or test files | Exempt from block |

**Rule: Diagnose BEFORE you patch. No blind patching after errors.**

### 3. Blind Patch Gate

Warns at 2 consecutive writes without reading. Blocks at 3+.

| Consecutive Writes | Action |
|---|---|
| 1 | Warn |
| 2 | **BLOCK** (3rd write total) |
| 3+ | **BLOCK** |
| Error recovery active + 1+ writes | **BLOCK** (escalated) |

**"Read" tools that reset the counter:** ReadFile, Grep, Glob, Agent, Shell, FetchURL, SearchWeb

### Why This Works

| LLM Failure Mode | Anti-Slop Countermeasure |
|---|---|
| Recency bias — forgets original goal | Cognitive checkpoint forces re-statement of goal |
| Action bias — patches blindly after errors | Error recovery forces diagnosis first |
| Overconfidence — writes without reading | Blind patch gate forces verification |
| Degradation over long context | Periodic checkpoints reset cognitive state |

---

## Project-Specific Guidelines

> Add project-specific rules below. These override the general guidelines when conflicting.

### Tech Stack
- Python 3.10+ (gatekeeper), Bash (hooks), Node.js (governance bridge)
- Kimi Code CLI with PreToolUse / PostToolUse / SessionEnd hooks

### Architecture
- Hooks-based enforcement: `gatekeeper.py` (Pre/Post/SessionEnd), `protect-env.sh` (Pre), `check-complete.sh` (SessionEnd)
- State machine in `~/.kimi/.gatekeeper/` (JSON per session)
- Skills auto-load from `~/.kimi/skills/` and `~/.claude/skills/`
- Anti-Slop gates: Cognitive Checkpoint, Error Recovery, Blind Patch (Principle 5)

### Testing
- pytest for gatekeeper unit tests (`hooks/gatekeeper.test.py`)
- Manual integration testing via shell commands

### Code Style
- Python: PEP 8, 100 char line length
- Bash: `set -euo pipefail`, `shellcheck`-clean
- Match existing style exactly

### Security
- No secrets in code (mechanically enforced by PreToolUse)
- `.env*` file writes blocked by `protect-env.sh`
- Parameterized queries only
- Path traversal validated on file writes

---

*Derived from Andrej Karpathy's observations on LLM coding pitfalls. Adapted for Kimi Code.*
