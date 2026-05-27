---
description: "ALWAYS ACTIVE — base layer. No invocation needed. Enforced after production writes."
---

# E2E Validation & Playwright Testing

**CRITICAL**: This skill is enforced by mechanical hooks. Production file writes without subsequent E2E test execution will be blocked after 3 writes. Git commits with untested changes are blocked.

## The Golden Rule

> **Unit tests prove the code works. E2E tests prove the USER can use it.**

Both are required. E2E is NOT optional.

---

## When E2E Validation is Required

**ALWAYS run E2E tests before considering a task complete when:**
- Any PHP/JS/TS/CSS/HTML template file is modified
- Authentication or authorization logic changes
- UI components, layouts, or styling changes
- Form validation or submission flows change
- Navigation, routing, or redirects change
- Database schema or query logic changes
- API response formats change

**E2E is NOT required for:**
- Documentation updates (README, comments)
- Configuration files (CI/CD, linter rules)
- Test file changes themselves
- Asset updates (images, fonts) without layout impact

---

## Playwright E2E Strategy

### 1. Centralized E2E Suite

Keep E2E tests in a dedicated location (e.g., `e2e/tests/`). Do not scatter E2E tests across the codebase.

```
e2e/
  tests/
    auth.spec.ts          # Authentication flows
    dashboard.spec.ts     # Main user journeys
    admin.spec.ts         # Admin-only features
    regression.spec.ts    # Known bug regressions
  fixtures/               # Test data, auth states
  screenshots/            # Baseline screenshots
  playwright.config.ts
```

### 2. User-Like Process Flows

Write tests that simulate REAL user behavior, not API calls.

**GOOD — User journey:**
```typescript
test('user can complete checkout with credit card', async ({ page }) => {
  await page.goto('/products');
  await page.click('[data-testid="product-1"]');
  await page.click('[data-testid="add-to-cart"]');
  await page.goto('/cart');
  await page.click('[data-testid="checkout"]');
  await page.fill('[name="card-number"]', '4111111111111111');
  await page.click('[data-testid="place-order"]');
  await expect(page.locator('[data-testid="order-confirmation"]'))
    .toBeVisible();
});
```

**BAD — API testing disguised as E2E:**
```typescript
// This is an integration test, not E2E
test('POST /api/checkout returns 200', async ({ request }) => {
  const res = await request.post('/api/checkout', { data: { ... } });
  expect(res.status()).toBe(200);
});
```

### 3. Stable Selectors (Avoid False Positives)

False positives in E2E usually come from brittle selectors.

| Strategy | Example | Reliability |
|----------|---------|-------------|
| `data-testid` | `[data-testid="submit-button"]` | ⭐⭐⭐ Best |
| Role + name | `page.getByRole('button', { name: 'Submit' })` | ⭐⭐⭐ Best |
| Text content | `page.getByText('Welcome back')` | ⭐⭐ Good |
| CSS class | `.btn-primary` | ⭐ Brittle |
| XPath position | `//div[3]/button[1]` | ❌ Fragile |

**Rule**: Prefer `data-testid` or ARIA roles. Never use positional selectors or generated class names.

### 4. Wait Conditions (Avoid Flakiness)

Flaky tests are worse than no tests.

```typescript
// GOOD: Wait for specific state
await page.waitForURL('/dashboard');
await expect(page.locator('[data-testid="loading"]')).toBeHidden();
await expect(page.locator('[data-testid="content"]')).toBeVisible();

// BAD: Arbitrary sleep
await page.waitForTimeout(2000);  // NEVER do this
```

**Use these wait strategies:**
- `await expect(locator).toBeVisible()` — waits up to timeout
- `await page.waitForURL(pattern)` — navigation completion
- `await page.waitForLoadState('networkidle')` — all network settled
- `await page.waitForResponse(url)` — specific API call finished

### 5. Screenshot Evidence

Take screenshots when visual changes are involved or when reproducing bugs.

```typescript
// Visual regression baseline
test('dashboard renders correctly', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixels: 100,  // Allow minor anti-aliasing differences
  });
});

// Bug reproduction evidence
test('bug: modal overflow on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/modal-page');
  await page.click('[data-testid="open-modal"]');
  await page.screenshot({ path: 'test-results/modal-bug.png', fullPage: true });
  // Assert + screenshot serves as proof of fix
});
```

**When to use screenshots:**
- CSS/styling changes → `toHaveScreenshot()`
- Bug fix verification → manual `screenshot()` as evidence
- Responsive design changes → multi-viewport screenshots
- Complex user flows → screenshot at each step for debugging

---

## Running E2E Tests

### Basic Commands

```bash
# Run all E2E tests
cd e2e && npx playwright test

# Run specific test file
cd e2e && npx playwright test auth.spec.ts

# Run with UI mode for debugging
cd e2e && npx playwright test --ui

# Update screenshot baselines
cd e2e && npx playwright test --update-snapshots

# Run against specific URL
cd e2e && BASE_URL=http://localhost:8090 npx playwright test
```

### CI/CD Integration

```bash
# Full validation pipeline
cd e2e && npx playwright test --reporter=list,html
# Check exit code: 0 = pass, 1 = fail
```

---

## False Positive Prevention

### 1. Test Data Stability

```typescript
// GOOD: Use fixtures for deterministic data
test('admin can delete user', async ({ page, adminUser }) => {
  // adminUser is a fixture that creates a known test user
  await page.goto(`/admin/users/${adminUser.id}`);
  await page.click('[data-testid="delete"]');
});
```

### 2. Isolate Tests

Each test should set up its own state. Don't rely on test order.

```typescript
test.beforeEach(async ({ page }) => {
  // Reset to known state before each test
  await page.goto('/logout');
  await page.goto('/login');
});
```

### 3. Environment Parity

E2E tests should run against an environment that matches production:
- Same database schema
- Same feature flags
- Real (not mocked) backend where possible

### 4. Retry Configuration

```typescript
// playwright.config.ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,  // Retry in CI for flaky environments
  workers: process.env.CI ? 1 : undefined,  // Sequential in CI
});
```

---

## E2E Validation Workflow

### After Production Code Changes:

1. **Write E2E test** (if new feature) or **identify affected E2E tests** (if bug fix)
2. **Run E2E suite**: `cd e2e && npx playwright test`
3. **If failures**: Debug, fix code, re-run. Do NOT skip failing tests.
4. **If visual changes**: Update baselines intentionally with `--update-snapshots`
5. **Screenshot evidence**: Attach screenshots to bug fix reports when applicable
6. **Only then**: Consider the task complete

### Gatekeeper Enforcement:

The gatekeeper tracks production file writes. After **3 production files** are modified without a test run, further writes are blocked. Git commits with untested production changes are also blocked.

**To clear the gate**: Run any test command (Playwright, pytest, jest, vitest, etc.)

---

## Debugging Failed E2E Tests

1. **Run with UI mode**: `npx playwright test --ui`
2. **Check trace**: Open `e2e/test-results/*/trace.zip` in https://trace.playwright.dev
3. **Check screenshot/video**: `e2e/test-results/` contains artifacts on failure
4. **Run single test**: `npx playwright test -g "test name"`
5. **Slow motion**: `await page.slowMo(1000)` or run with `--headed`

---

## Anti-Patterns (AVOID)

| Anti-Pattern | Why It Destroys E2E |
|-------------|---------------------|
| `waitForTimeout` | Flaky; fails on slow CI machines |
| Positional selectors | Breaks when UI layout changes |
| Testing in production | Risky; no rollback safety |
| Skipping failing tests | Hides real bugs; creates false confidence |
| No screenshot on failure | Impossible to debug CI failures |
| Sharing state between tests | Order-dependent flakiness |
| Mocking the backend | You're not testing the real integration |
| Only happy-path E2E | Critical bugs live in edge cases |

## Success Criteria

This skill succeeded if:
- E2E tests verify real user flows (not API calls)
- Selectors are stable (`data-testid` or ARIA roles)
- Screenshots are used for visual regression and bug evidence
- Tests are isolated and deterministic

### Learnings Capture (MANDATORY)
Before declaring this skill complete, write learnings to `~/.kimi/skills/e2e-validation/learnings.md`:
```markdown
## $(date +%Y-%m-%d)
- E2E framework/version used:
- Selector strategy that works for this UI:
- Flaky test patterns observed:
- Screenshot baseline update policy:
```
