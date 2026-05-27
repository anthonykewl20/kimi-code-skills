---
description: "Strict Red-Green-Refactor TDD. Triggers: user says 'test', 'TDD', 'failing test', 'red-green', OR task is a bug fix with a reproduction case, OR task is a new feature with defined acceptance criteria."
---

# TDD Workflow for Agentic AI — The Entropy Killer

> "This isn't 'write some tests.' This is entropy reversal at the agent level."

**MANDATORY**: Follow this workflow for every feature, bug fix, or refactoring task.

## The Core Rule

> **Test List → Red → Green → Refactor → Repeat**

Never write production code without a failing test first. Never write more than one test at a time.

## When to Use

- Building any new feature
- Fixing any bug
- Refactoring existing code
- Any time you want the agent to produce working, tested code

## When NOT to Use

- Pure documentation changes
- Configuration-only changes (no logic)
- One-line fixes where the test already exists

---

## Phase 0: Test List (Spec Document)

Before touching any code, create or update a markdown test list / spec document.

**Format:**
```markdown
# Feature: User Login

## Behaviors to Test
1. [ ] Valid credentials → success redirect
2. [ ] Invalid password → error message
3. [ ] Empty fields → validation errors
4. [ ] Locked account → specific error
5. [ ] Rate limiting → 429 response

## Edge Cases
- [ ] SQL injection in username field
- [ ] 1000-character password
- [ ] Unicode usernames
```

**Rules:**
- One spec per feature/story
- Update the spec as you discover new cases during implementation
- Check off items as you complete them
- If the AI tries to write implementation before the spec, STOP and write the spec first

---

## Phase 1: RED — Write the Failing Test

**Prompt structure:**
```
"Write the MINIMAL failing test for [behavior]. 
Testing framework: [Playwright/pytest/Jest/Vitest/etc.]
Do NOT write the implementation. Show the test and the expected failure message."
```

**Constraints:**
- One behavior per test
- Test name must describe the behavior, not the implementation
- Use Arrange-Act-Assert structure
- No mocks unless the dependency is non-deterministic (network, clock, random)
- Assert on outcomes, not internal state
- One test per **vertical slice**, not horizontal layer
  - ✅ GOOD: Test the full flow: input → processing → output
  - ❌ BAD: Write all unit tests first, then all integration tests, then implement

**Checklist before proceeding to GREEN:**
- [ ] Test is written and saved
- [ ] Test fails when run
- [ ] Failure message clearly shows what's missing
- [ ] Test uses only public APIs
- [ ] Test would survive a refactor (not tied to implementation details)

**Example (Playwright E2E):
```typescript
// GOOD: Describes user outcome
test('user with valid credentials is redirected to dashboard', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="username"]', 'alice');
  await page.fill('[name="password"]', 'correct');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});

// BAD: Describes implementation
test('submitLoginForm sets auth token in localStorage', async ({ page }) => {
  // ... implementation detail
});
```

---

## Phase 2: GREEN — Write Minimal Production Code

**Prompt structure:**
```
"Write the MINIMAL production code to make this test pass. 
No refactoring. No predicting future requirements. 
Naive implementation is acceptable."
```

**Constraints:**
- Only write code needed by the CURRENT test
- Duplication is acceptable in this phase
- If you find yourself designing abstractions, STOP — that's for Refactor
- If the test requires a new module/function, create it with the simplest possible signature

**Anti-pattern to avoid:**
- Writing generic code "for future use"
- Adding error handling for cases not tested yet
- Creating interfaces/classes before they're needed

**Checklist before proceeding to REFACTOR:**
- [ ] Test passes when run
- [ ] No other tests broke
- [ ] Implementation is minimal (no speculative generality)

---

## Phase 3: REFACTOR — Clean While Green

**Prompt structure:**
```
"Refactor the production code while keeping ALL tests green. 
Explain each change and which principle it follows (DRY, SRP, removing duplication, etc.)."
```

**What to refactor:**
- Remove duplication between test and production code
- Rename variables/functions for clarity (use CONTEXT.md domain language)
- Extract helper functions
- Improve readability
- **Do NOT** change behavior

**What NOT to refactor:**
- Adding untested features
- Changing public APIs without updating tests
- Optimizing for performance (unless it's a known bottleneck)

**Checklist before starting next cycle:**
- [ ] All tests still pass
- [ ] Code is cleaner than before
- [ ] No functionality was added or removed

### Step 4: Repeat

Start the next RED phase for the next behavior.

---

## Turn-by-Turn Discipline

If Kimi tries to jump ahead:

| Violation | Your Response |
|-----------|--------------|
| Writes implementation during Red | "That's the Green phase. We are still in Red. Write only the test." |
| Writes multiple tests at once | "One behavior at a time. Pick the smallest behavior first." |
| Refactors during Green | "No refactoring yet. Make the test pass with the simplest code." |
| Predicts future requirements | "YAGNI. Only solve the current test case." |

---

## Vertical Slicing vs Horizontal Slicing

**Horizontal Slicing (WRONG):**
```
1. Write ALL unit tests for the service layer
2. Write ALL unit tests for the repository layer
3. Implement ALL service layer code
4. Implement ALL repository layer code
5. Write integration tests
6. Fix everything that broke
```
→ Produces "crap tests" that are tightly coupled to implementation. When you refactor, all tests break.

**Vertical Slicing (CORRECT):**
```
1. RED: Test "user can register with valid email"
   GREEN: Implement minimal registration flow
   REFACTOR: Clean up
2. RED: Test "user cannot register with duplicate email"
   GREEN: Add duplicate check
   REFACTOR: Clean up
3. RED: Test "user receives confirmation email after registration"
   GREEN: Add email dispatch
   REFACTOR: Clean up
```
→ Each slice is a complete, testable behavior. Tests survive refactoring because they test outcomes, not structure.

## Good Test vs Bad Test Reference

### Good Test Example
```typescript
// Tests BEHAVIOR through public API
it("should calculate total with tax", () => {
  const cart = new Cart();
  cart.addItem({ price: 100, quantity: 2 }); // $200
  cart.addItem({ price: 50, quantity: 1 });  // $50

  const total = cart.getTotal({ taxRate: 0.08 });

  expect(total).toBe(270); // ($250 * 1.08)
});
```

### Bad Test Example
```typescript
// Tests IMPLEMENTATION details
it("should call calculateTax with correct arguments", () => {
  const spy = jest.spyOn(TaxService, "calculateTax");
  const cart = new Cart();
  cart.addItem({ price: 100, quantity: 2 });

  cart.getTotal({ taxRate: 0.08 });

  expect(spy).toHaveBeenCalledWith(250, 0.08);
});
```
→ If we refactor to inline the tax calculation, this test breaks even though behavior is identical.

---

## Edge Case Discovery Mode

After Green+Refactor, ask:

```
"Act as a hostile reviewer. Given the current production code, 
what test could I write that would fail? (Mutation testing mindset)
```

Common gaps to probe:
- Null/undefined inputs
- Empty collections
- Boundary values (0, MAX_INT, empty string)
- Concurrent access
- Network failures
- Timezone/DST edge cases

### Edge Case Q&A

**"But I don't know how to test this"**
→ If you can't write a test, you don't understand the requirement well enough. Go back to `/skill:grill-me`.

**"The existing codebase has no tests"**
→ Start with one test for the behavior you're about to change. Don't try to backfill all tests at once.

**"This is a UI change — how do I TDD that?"**
→ Test through component rendering (e.g., React Testing Library). RED: "button should be disabled when form is invalid". GREEN: Add disabled prop. REFACTOR: Extract validation logic.

---

## When to Use E2E vs Unit Tests

| Test Type | When to Use | Framework |
|-----------|------------|-----------|
| **E2E** | User-facing flows, critical paths, visual regression | Playwright, Cypress |
| **Integration** | API endpoints, database queries, service boundaries | pytest, Jest, Vitest |
| **Unit** | Pure functions, business logic, algorithms | pytest, Jest, Vitest |

**Rule**: Start with E2E for user-facing features. Drill down to unit tests only when the E2E test becomes too slow to give fast feedback.

---

## Playwright E2E TDD Pattern

For UI features, the "test" is often a user journey:

```typescript
// RED: Write failing E2E test
test('admin can ban a user from the dashboard', async ({ page }) => {
  await page.goto('/admin/users');
  await page.click('[data-testid="user-row-alice"] [data-testid="ban-button"]');
  await page.click('[data-testid="confirm-ban"]');
  await expect(page.locator('[data-testid="user-row-alice"] .status'))
    .toHaveText('Banned');
});
```

Then write the backend API + frontend code to make it pass.

**Screenshot Testing:**
- Use `toHaveScreenshot()` for visual regression on stable UI states
- Update baselines intentionally with `--update-snapshots`
- Never ignore screenshot failures without visual inspection

---

## Test Quality Checklist

Before declaring a task complete:

- [ ] Every production behavior has a failing test that precedes it
- [ ] Tests are independent (order doesn't matter)
- [ ] Tests describe WHAT, not HOW
- [ ] No test depends on internal implementation details
- [ ] Edge cases are covered
- [ ] E2E tests verify real user flows
- [ ] Tests run in < 10 seconds (unit) or < 60 seconds (E2E)
- [ ] No `test.only`, `describe.skip`, or commented-out tests

---

## Common TDD Mistakes (AVOID)

| Mistake | Why It Breaks TDD |
|---------|-------------------|
| "Write all tests, then all code" | Loses feedback loop; tests become specification documents, not design tools |
| "Build me a fully tested app" | Too broad; TDD works one micro-behavior at a time |
| "100% coverage goal" | Coverage is a side effect; behavioral confidence is the goal |
| Mocking everything | Tests verify mocks, not real behavior |
| Testing implementation | Refactoring breaks tests; tests should enable refactoring |
| Large steps (>15 min without green) | Cognitive debt accumulates; revert to last green if stuck |

---

## Why This Works at the Neural Level

TDD is a **cognitive forcing function** that exploits known LLM failure modes:

| LLM Failure Mode | TDD Countermeasure |
|---|---|
| **Action bias** — jumps to implementation | RED phase forces a hard stop: write the test FIRST |
| **Speculative generality** — builds for imaginary futures | GREEN phase constraint: "only code needed by the CURRENT test" |
| **Scope creep in token space** | Vertical slicing keeps each cycle small and bounded |
| **Hallucinated correctness** | Checklist per cycle verifies the test fails for the right reason, passes for the right reason |

## The Harness

Your constraints (skills, hooks, linter rules) are the "harness" that keeps the AI on track. Update them as you discover new anti-patterns in your codebase.

---

## Success Criteria

This skill succeeded if:
- Every feature has at least one test written BEFORE the implementation
- Tests describe behavior, not implementation
- Tests use public APIs only
- All tests pass after refactoring
- No test was changed to accommodate implementation (only to fix incorrect requirements)

### Learnings Capture (MANDATORY)
Before declaring this skill complete, write learnings to `~/.kimi/skills/tdd-workflow/learnings.md`:
```markdown
## $(date +%Y-%m-%d)
- Testing framework/version used in this codebase:
- User preferences discovered (naming, structure, mocking strategy):
- Anti-patterns observed in this codebase:
- Any adjustments to the TDD workflow for this project:
```
