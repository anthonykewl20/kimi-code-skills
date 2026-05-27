# Skill: playwright

> End-to-end testing with Playwright using MCP (Model Context Protocol) browser control.
> Use when: writing E2E tests, debugging frontend bugs visually, verifying UI/UX compliance,
> running accessibility audits, capturing screenshots for PRs, testing responsive breakpoints.
> 
> Primary companion: `ui-ux` (design principles, accessibility rules)
> Secondary: `e2e-validation` (test requirements, validation gates)

---

## Playwright MCP Integration

The Playwright MCP server exposes browser control to the agent. Available capabilities:

| MCP Tool | Purpose | When to Use |
|---|---|---|
| `browser_navigate` | Load a URL | Start every test session |
| `browser_click` | Click an element | Simulate user actions |
| `browser_type` | Type into input | Form filling, search |
| `browser_select_option` | Select dropdown value | Form interactions |
| `browser_scroll` | Scroll page/element | Test infinite scroll, lazy load |
| `browser_screenshot` | Capture screenshot | Visual regression, bug reports |
| `browser_hover` | Hover over element | Test tooltip, dropdown reveal |
| `browser_drag` | Drag-and-drop | Test reordering, file upload zones |
| `browser_press_key` | Press keyboard key | Test shortcuts, accessibility |
| `browser_evaluate` | Execute JS in page context | Extract data, manipulate state |
| `browser_get_content` | Get page HTML/text | Assert DOM state |
| `browser_go_back/forward` | Navigation history | Test breadcrumb, back button |
| `browser_close` | Close browser | Cleanup after test |

### MCP Session Pattern

```
1. browser_navigate(url)
2. browser_screenshot() → verify initial state
3. browser_click(selector) → perform action
4. browser_screenshot() → verify result
5. browser_get_content() → assert DOM/text
6. browser_close()
```

---

## E2E Test Architecture

### Project Structure

```
e2e/
├── fixtures/           # Test data, mock responses
├── pages/              # Page Object Models
│   ├── LoginPage.ts
│   ├── DashboardPage.ts
│   └── CheckoutPage.ts
├── tests/
│   ├── auth/
│   │   ├── login.spec.ts
│   │   └── register.spec.ts
│   ├── checkout/
│   │   └── full-flow.spec.ts
│   └── accessibility/
│       └── axe-audit.spec.ts
├── utils/
│   ├── test-helpers.ts
│   └── axe-helper.ts
├── playwright.config.ts
└── .env.test
```

### Page Object Model (POM)

**Rule:** Every major page/screen gets a POM. Never write raw selectors in test files.

```typescript
// pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  readonly emailInput = this.page.locator('[data-testid="email-input"]');
  readonly passwordInput = this.page.locator('[data-testid="password-input"]');
  readonly submitButton = this.page.locator('[data-testid="login-submit"]');
  readonly errorMessage = this.page.locator('[data-testid="login-error"]');

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toHaveText(message);
  }
}
```

### Test File Pattern

```typescript
// tests/auth/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../../pages/LoginPage';

test.describe('Login Flow', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('successful login redirects to dashboard', async ({ page }) => {
    await loginPage.login('user@example.com', 'correct-password');
    await expect(page).toHaveURL('/dashboard');
  });

  test('invalid credentials show error', async () => {
    await loginPage.login('user@example.com', 'wrong-password');
    await loginPage.expectError('Invalid email or password');
  });

  test('empty fields show validation errors', async () => {
    await loginPage.submitButton.click();
    await loginPage.expectError('Email is required');
  });
});
```

---

## Selector Strategy

| Priority | Selector Type | Example | Why |
|---|---|---|---|
| 1 | `data-testid` | `[data-testid="submit-btn"]` | Stable, semantic, not affected by styling |
| 2 | `role` + `name` | `page.getByRole('button', { name: 'Submit' })` | Accessible, user-centric |
| 3 | `label` | `page.getByLabel('Email')` | Accessible, works with screen readers |
| 4 | `placeholder` | `page.getByPlaceholder('Search...')` | User-visible text |
| 5 | `text` | `page.getByText('Welcome back')` | Visible text content |
| ❌ Avoid | CSS class | `.btn-primary` | Brittle — changes with redesign |
| ❌ Avoid | XPath | `//div[3]/span` | Brittle, unreadable |
| ❌ Avoid | Position | `:nth-child(2)` | Breaks on layout changes |

**Rule:** If a component doesn't have `data-testid`, add it during implementation — don't work around it with fragile selectors.

---

## Accessibility Testing with Playwright

### axe-core Integration

```typescript
// utils/axe-helper.ts
import { Page, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

export async function expectNoAccessibilityViolations(page: Page) {
  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
}
```

```typescript
// tests/accessibility/axe-audit.spec.ts
import { test } from '@playwright/test';
import { expectNoAccessibilityViolations } from '../../utils/axe-helper';

test('homepage has no accessibility violations', async ({ page }) => {
  await page.goto('/');
  await expectNoAccessibilityViolations(page);
});
```

### What axe-core Catches
- Missing alt text on images
- Insufficient color contrast
- Missing form labels
- Empty headings
- Invalid ARIA attributes
- Missing focus indicators
- Keyboard traps

### What axe-core Misses (Manual Check Required)
- Logical reading order
- Meaningful alt text (it checks existence, not quality)
- Color-only information
- Timing and motion sensitivity
- Cognitive accessibility

---

## Visual Regression Testing

### Screenshot Comparison

```typescript
import { test, expect } from '@playwright/test';

test('login page matches snapshot', async ({ page }) => {
  await page.goto('/login');
  await expect(page).toHaveScreenshot('login-page.png', {
    maxDiffPixels: 100,  // Allow minor anti-aliasing differences
  });
});
```

### Component-Level Screenshots

```typescript
test('button states', async ({ page }) => {
  await page.goto('/components');
  
  const button = page.locator('[data-testid="primary-btn"]');
  
  // Default state
  await expect(button).toHaveScreenshot('button-default.png');
  
  // Hover state
  await button.hover();
  await expect(button).toHaveScreenshot('button-hover.png');
  
  // Focus state
  await button.focus();
  await expect(button).toHaveScreenshot('button-focus.png');
  
  // Active/pressed state
  await button.click();
  await expect(button).toHaveScreenshot('button-active.png');
});
```

---

## Responsive & Mobile Testing

### Viewport Presets

```typescript
// playwright.config.ts
const viewports = [
  { name: 'mobile', width: 375, height: 667 },   // iPhone SE
  { name: 'tablet', width: 768, height: 1024 },  // iPad
  { name: 'desktop', width: 1280, height: 720 }, // Standard
  { name: 'wide', width: 1920, height: 1080 },   // Desktop
];

for (const viewport of viewports) {
  test(`checkout works on ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    // ... test logic
  });
}
```

### Touch Event Testing

```typescript
test('swipe to delete on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/inbox');
  
  const message = page.locator('[data-testid="message-1"]');
  
  // Swipe left
  await message.dragTo(message, {
    sourcePosition: { x: 350, y: 30 },
    targetPosition: { x: 50, y: 30 },
  });
  
  await expect(page.locator('[data-testid="delete-btn"]')).toBeVisible();
});
```

---

## Performance Testing with Playwright

### Core Web Vitals Measurement

```typescript
import { test, expect } from '@playwright/test';

test('homepage meets performance budget', async ({ page }) => {
  await page.goto('/');
  
  // Wait for LCP element
  const lcpElement = await page.locator('img[fetchpriority="high"]').first();
  await expect(lcpElement).toBeVisible();
  
  // Get performance metrics
  const metrics = await page.evaluate(() => {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    return {
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.startTime,
      loadComplete: navigation.loadEventEnd - navigation.startTime,
    };
  });
  
  expect(metrics.domContentLoaded).toBeLessThan(1500);
  expect(metrics.loadComplete).toBeLessThan(3000);
});
```

### Network Interception

```typescript
test('shows skeleton loader while API loads', async ({ page }) => {
  // Slow down API response
  await page.route('/api/dashboard', async (route) => {
    await new Promise((r) => setTimeout(r, 2000));
    await route.continue();
  });
  
  await page.goto('/dashboard');
  
  // Skeleton should be visible immediately
  await expect(page.locator('[data-testid="skeleton-loader"]')).toBeVisible();
  
  // Content replaces skeleton after load
  await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible({ timeout: 3000 });
});
```

---

## Test Data & Mocking

### API Mocking

```typescript
import { test, expect } from '@playwright/test';

test('shows empty state when no orders', async ({ page }) => {
  await page.route('/api/orders', async (route) => {
    await route.fulfill({
      status: 200,
      body: JSON.stringify({ orders: [] }),
    });
  });
  
  await page.goto('/orders');
  await expect(page.locator('[data-testid="empty-orders"]')).toBeVisible();
});
```

### Authentication State

```typescript
// fixtures/auth.ts
export async function loginAsUser(page: Page, user: TestUser) {
  await page.goto('/login');
  await page.fill('[data-testid="email-input"]', user.email);
  await page.fill('[data-testid="password-input"]', user.password);
  await page.click('[data-testid="login-submit"]');
  await page.waitForURL('/dashboard');
}

// Global setup for authenticated tests
// playwright.config.ts:
// globalSetup: './global-setup.ts'
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

### Playwright Config Best Practices

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e/tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'] } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 12'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## MCP-Driven Debugging Workflow

When a frontend bug is reported, use this sequence:

```
1. browser_navigate(url) → reproduce the issue
2. browser_screenshot() → capture current state
3. browser_get_content() → inspect DOM structure
4. browser_evaluate("document.querySelector('[buggy-element]').getBoundingClientRect()")
   → get exact position/sizing data
5. browser_evaluate("window.getComputedStyle(document.querySelector('[buggy-element]'))")
   → get computed styles
6. Fix code → browser_navigate(url) → browser_screenshot() → verify fix
```

**Screenshots for every visual change:** Before/after screenshots are mandatory for any PR that modifies UI.

---

## Common Anti-Patterns

| Anti-Pattern | Why It's Wrong | Fix |
|---|---|---|
| `page.waitForTimeout(3000)` | Flaky — timing varies | Use `expect(locator).toBeVisible()` instead |
| `page.click('.btn-primary')` | Class selectors are brittle | Use `data-testid` or `getByRole` |
| Tests depend on execution order | Isolation violation | Each test must be independent |
| No cleanup in `afterEach` | State leaks between tests | Reset DB, clear storage, logout |
| Testing implementation details | Brittle — breaks on refactor | Test user-visible behavior |
| Only testing "happy path" | Misses real bugs | Always test error states, empty states, edge cases |
| Hardcoded URLs in tests | Breaks on environment change | Use `baseURL` config + relative paths |

---

## Integration with Other Skills

| Context | Primary Skill | Playwright Role |
|---|---|---|
| Building a new UI component | `ui-ux` + `shadcn-ui` | Write visual regression test, a11y audit |
| Fixing a frontend bug | `diagnose` + `ui-ux` | Use MCP to screenshot, inspect DOM, verify fix |
| Adding a checkout flow | `ui-ux` + `tdd-workflow` | Write E2E test first (RED), implement (GREEN) |
| Refactoring CSS | `tailwind-css` + `ui-ux` | Screenshot comparison to catch visual regressions |
| Performance optimization | `ui-ux` | Measure LCP, INP, CLS with Playwright |
| Accessibility audit | `ui-ux` | Run axe-core scan, manual keyboard testing |

---

## Learnings Capture Template

After each Playwright session, record:

```markdown
## YYYY-MM-DD | playwright | B:N W:N
- **Block:** [What test failure or gate blocked progress]
- **Warn:** [What pattern caused a warning]
- **Pattern:** [Reusable insight: selector strategy, test structure, MCP technique]
- **Files:** [Test files created/modified]
```
