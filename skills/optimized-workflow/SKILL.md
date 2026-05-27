---
description: "ALWAYS ACTIVE — base layer. No invocation needed. Applied to every task."
---

# Optimized Coding Workflows for Kimi CLI

Use this skill when starting any non-trivial task to ensure maximum efficiency and output quality.

## Task Classification & Mode Selection

Before starting, classify the task:

| Task Type | Required Mode | Why |
|-----------|--------------|-----|
| Multi-file changes, architecture decisions, new features | **Plan Mode** (`EnterPlanMode`) | Prevents sunk cost fallacy, ensures coherent design |
| Bug fixes with unknown root cause | **Explore first, then Plan** | Understand before fixing |
| Single-file, single-function change | Direct execution | Planning overhead not justified |
| Codebase research only | **Explore subagent** | Read-only, fast, parallelizable |

**Rule**: If the task touches more than 2 files OR involves architectural decisions, you MUST use Plan Mode.

## Parallel Execution Strategy

You can output multiple tool calls in a single response. **Always parallelize when safe:**

1. **Read Phase**: Read multiple unrelated files in parallel
2. **Search Phase**: Run multiple `Grep` and `Glob` calls in parallel
3. **Write Phase**: Write to unrelated files in parallel
4. **Test Phase**: Run tests and linting in parallel

**Never parallelize**:
- Sequential operations (read → analyze → write the same file)
- Operations with data dependencies
- Git operations that must be ordered

## Exploration Protocol

For existing codebases, follow this order:

1. **Quick Scan**: `Glob` for key config files (`package.json`, `pyproject.toml`, etc.)
2. **Architecture Map**: `ReadFile` on main entry points and config files
3. **Deep Dive**: Use `Agent(subagent_type="explore")` for modules requiring >3 search queries
4. **Parallel Research**: Launch multiple explore agents for independent questions

## Implementation Protocol

1. **Understand First**: Read relevant code before modifying
2. **Minimal Changes**: Change only what's necessary. Follow existing style.
3. **TDD Discipline**: Read `tdd-workflow` skill. Red-Green-Refactor for every behavior.
4. **E2E Validation**: Read `e2e-validation` skill. Run Playwright E2E tests after production changes.
5. **Test After Every Change**: Run tests immediately after writes
6. **Iterate**: Read error → Fix → Re-test. Never batch untested changes.
7. **Verify**: After completion, run full test suite, linters, AND E2E suite

## Code Quality Checklist (Before Every Write)

- [ ] No TODOs, FIXMEs, or placeholders
- [ ] Error handling for all failure paths
- [ ] Edge cases considered
- [ ] Follows existing naming conventions
- [ ] No unused imports or dead code
- [ ] Complex logic has explanatory comments (not obvious code)
- [ ] No hardcoded secrets or magic numbers
- [ ] Idempotent operations where applicable
- [ ] Failing test written FIRST (Red phase)
- [ ] E2E test covers the user-facing behavior
- [ ] Screenshots taken for visual changes

## Communication Efficiency

- **Be concise**: One sentence beats a paragraph when equivalent
- **Use structured output**: Bullet points, tables, and code blocks over prose
- **Show, don't tell**: Include code diffs, not descriptions of diffs
- **Status updates**: For operations >30s, inform user of progress
- **Error context**: When reporting failures, include the specific error + your diagnosis

## Context Management

- **Track requirements**: Refer back to original constraints in every turn
- **Summarize long outputs**: Don't dump raw logs; extract the key error
- **Update todo list**: Use `SetTodoList` to track multi-step progress
- **Compact gracefully**: When context compacts, reaffirm current task state

## Security Defaults

- **Least privilege**: Don't chmod 777 or run as root unnecessarily
- **Validate inputs**: All user-facing endpoints must sanitize input
- **No secrets in code**: Use env vars, never hardcode credentials
- **Confirm destructive ops**: Ask before `rm -rf`, `git push --force`, schema drops

## Subagent Delegation Rules

- **Delegate when**: Task requires >10 tool calls OR is self-contained research
- **Provide full context**: Subagents don't see parent context
- **Prefer resume**: Resume existing subagents when continuing prior work
- **Foreground default**: Use background only when result isn't needed immediately

## Success Criteria

This skill succeeded if:
- The task was classified correctly (plan vs direct)
- Exploration was thorough before implementation
- Implementation followed the checklist
- Code quality gates passed
- Subagents were delegated appropriately

### Learnings Capture (MANDATORY)
Before declaring this skill complete, write learnings to `~/.kimi/skills/optimized-workflow/learnings.md`:
```markdown
## $(date +%Y-%m-%d)
- Task classification patterns for this codebase:
- Optimal exploration depth discovered:
- Subagent delegation strategy that worked:
- Communication style preference of user:
```
