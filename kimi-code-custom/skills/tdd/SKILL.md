---
name: tdd
description: Test-driven development with a red-green-refactor loop. Builds features or fixes bugs one vertical slice at a time. Prevents crap tests and crap code.
---

# /tdd — Test-Driven Development

> "Always take small, deliberate steps. The rate of feedback is your speed limit. Never take on a task that's too big." — David Thomas & Andrew Hunt, *The Pragmatic Programmer*

## When to Use

- Building any new feature
- Fixing any bug
- Refactoring existing code
- Any time you want the agent to produce working, tested code

## When NOT to Use

- Pure documentation changes
- Configuration-only changes (no logic)
- One-line fixes where the test already exists

## The Red-Green-Refactor Loop

### Step 1: RED — Write a Failing Test

Before writing ANY implementation code, write a test that fails.

**Rules for the RED phase:**
1. The test must describe **behavior**, not implementation
   - ✅ GOOD: `it("should reject passwords shorter than 8 characters")`
   - ❌ BAD: `it("should call validatePassword with minLength=8")`

2. The test must use **public interfaces only**
   - ✅ GOOD: Test through the API endpoint or public method
   - ❌ BAD: Test internal helper functions directly

3. The test must fail for the **right reason**
   - Run the test. Confirm it fails.
   - Read the error. Is it failing because the feature doesn't exist yet? (Good)
   - Or is it failing because of a setup error? (Bad — fix setup first)

4. One test per **vertical slice**, not horizontal layer
   - ✅ GOOD: Test the full flow: input → processing → output
   - ❌ BAD: Write all unit tests first, then all integration tests, then implement

**Checklist before proceeding to GREEN:**
- [ ] Test is written and saved
- [ ] Test fails when run
- [ ] Failure message clearly shows what's missing
- [ ] Test uses only public APIs
- [ ] Test would survive a refactor (not tied to implementation details)

### Step 2: GREEN — Write Minimum Implementation

Write the **smallest amount of code** that makes the test pass.

**Rules for the GREEN phase:**
1. Do NOT write code for future requirements
2. Do NOT add error handling for impossible scenarios
3. Do NOT refactor yet — just make it pass
4. Hardcode if necessary — you'll refactor in the next step
5. If you need to change the test to make it pass, go back to RED

**Checklist before proceeding to REFACTOR:**
- [ ] Test passes when run
- [ ] No other tests broke
- [ ] Implementation is minimal (no speculative generality)

### Step 3: REFACTOR — Clean Up While Green

Now that you have working code + passing tests, improve the design.

**Rules for the REFACTOR phase:**
1. Tests must stay green throughout
2. Remove duplication
3. Improve names (use CONTEXT.md domain language)
4. Extract functions/classes only when you have 3+ uses
5. Add comments only for "why", not "what"

**Checklist before starting next cycle:**
- [ ] All tests still pass
- [ ] Code is cleaner than before
- [ ] No functionality was added or removed

### Step 4: Repeat

Start the next RED phase for the next behavior.

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

## Edge Cases

**"But I don't know how to test this"**
→ If you can't write a test, you don't understand the requirement well enough. Go back to `/skill:grill-me`.

**"The existing codebase has no tests"**
→ Start with one test for the behavior you're about to change. Don't try to backfill all tests at once.

**"This is a UI change — how do I TDD that?"**
→ Test through component rendering (e.g., React Testing Library). RED: "button should be disabled when form is invalid". GREEN: Add disabled prop. REFACTOR: Extract validation logic.

## Success Criteria

This skill succeeded if:
- Every feature has at least one test written BEFORE the implementation
- Tests describe behavior, not implementation
- Tests use public APIs only
- All tests pass after refactoring
- No test was changed to accommodate implementation (only to fix incorrect requirements)
