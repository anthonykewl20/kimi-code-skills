---
name: improve-codebase-architecture
description: Entropy reversal scanning. Triggers: user says 'refactor', 'code quality', 'entropy', 'deep modules', 'god object', OR codebase has not been reviewed in 3+ days.

---

# /improve-codebase-architecture — Entropy Reversal

> "Invest in the design of the system every day." — Kent Beck, *Extreme Programming Explained*

> "The best modules are deep. They allow a lot of functionality to be accessed through a simple interface." — John Ousterhout, *A Philosophy Of Software Design*

## When to Use

- Once every 2-3 days during active development
- Before a major release or refactor
- When the codebase feels "hard to change"
- When new features require touching 5+ files
- After a sprint of rapid AI-assisted coding

## When NOT to Use

- On a brand new project (<1 week old)
- When under deadline pressure (schedule it for after)
- On code you don't own (open source contributions)

## What This Skill Does

1. Reads `CONTEXT.md` to understand the domain language
2. Reads recent ADRs in `docs/adr/` to understand decisions
3. Scans the codebase for "shallow modules" and "deep modules"
4. Identifies entropy indicators
5. Produces actionable RFCs (filed as issues or saved to `docs/architecture-rfcs/`)

## Key Concepts

### Deep Module vs Shallow Module

**Deep Module:**
- Simple interface (few public methods)
- Complex implementation (many private helpers)
- High functionality-to-interface ratio
- Example: `fs.readFile(path)` — one call, massive complexity inside

**Shallow Module:**
- Complex interface (many public methods)
- Simple implementation (thin wrappers)
- Low functionality-to-interface ratio
- Example: A utility class with 20 one-line methods

### Entropy Indicators

| Indicator | What It Means | Example |
|---|---|---|
| **Fan-out explosion** | One file imports 10+ others | `src/pages/Dashboard.tsx` imports 15 components |
| **Leaky abstractions** | Internal details exposed | `UserService` exposes `queryBuilder` to callers |
| **God modules** | 500+ lines, 20+ public methods | `src/utils/helpers.ts` with 45 unrelated functions |
| **Tight coupling** | Changing A always breaks B | `OrderService` directly calls `EmailService.send()` |
| **Duplicated logic** | Same pattern in 3+ places | Validation rules copy-pasted in 4 controllers |
| **Dead code** | Functions never called | `calculateLegacyTax()` still exists after migration |
| **Inconsistent naming** | Same concept, different names | `userId`, `user_id`, `uid`, `customerId` for same field |

## Process

### Step 1: Read Context

Read these files before scanning:
- `CONTEXT.md` (domain language)
- `docs/adr/` (recent decisions, last 5 ADRs)
- `package.json` / `pyproject.toml` / equivalent (dependencies)

### Step 2: Scan for Entropy

Run these analyses (use Kimi's file tools):

**A. Module Depth Analysis**
```bash
# Find files with many imports (high fan-out)
find src -name "*.ts" -exec sh -c 'echo "$(grep -c "^import" "$1") $1"' _ {} \; | sort -rn | head -20

# Find files with many exports (complex interface)
find src -name "*.ts" -exec sh -c 'echo "$(grep -c "^export" "$1") $1"' _ {} \; | sort -rn | head -20
```

**B. God Module Detection**
```bash
# Find the largest files
find src -name "*.ts" -exec wc -l {} + | sort -rn | head -20
```

**C. Naming Inconsistency**
```bash
# Search for multiple naming conventions for same concept
grep -r "userId\|user_id\|uid\|customerId" src/ | wc -l
```

**D. Dead Code Detection**
```bash
# Find exported functions never imported (requires static analysis)
# Use ts-prune or equivalent:
npx ts-prune | head -30
```

### Step 3: Identify Deepening Opportunities

For each entropy indicator found, propose a "deepening" — making a module deeper (more functionality, simpler interface).

**Example Opportunities:**

| Current State | Deepening Opportunity | Effort | Impact |
|---|---|---|---|
| 3 files validate email differently | Extract `EmailValidator` with one `validate()` method | Low | High |
| `Dashboard` imports 15 components | Create `DashboardLayout` that composes sections | Medium | High |
| `UserService` has 20 public methods | Split into `AuthService`, `ProfileService`, `PreferenceService` | Medium | Medium |
| `utils/helpers.ts` has 45 functions | Group into `StringUtils`, `DateUtils`, `ArrayUtils` | Low | Medium |
| `OrderService` directly calls `EmailService` | Introduce `NotificationPort` interface, inject adapter | High | High |

### Step 4: Prioritize & File RFCs

Rank opportunities by:
1. **Impact** × **Effort** ratio (highest first)
2. **Risk of regression** (lower first)
3. **Alignment with current sprint goals**

Create an RFC for each high-priority opportunity:

```markdown
# RFC: Extract EmailValidator

## Problem
Email validation exists in 3 places with different rules:
- `src/auth/register.ts` (regex A)
- `src/users/profile.ts` (regex B)
- `src/admin/invites.ts` (no validation)

## Proposal
Create `src/validation/EmailValidator.ts` with one public method:
```typescript
class EmailValidator {
  validate(email: string): Result<{ valid: true }, ValidationError>
}
```

## Acceptance Criteria
- [ ] All 3 locations use `EmailValidator`
- [ ] Old validation code removed
- [ ] Tests cover: valid email, invalid email, empty string, unicode email

## Effort: 2 hours
## Risk: Low (pure refactor, no behavior change)
```

File as:
- GitHub issue (if using GitHub)
- Linear ticket (if using Linear)
- `docs/architecture-rfcs/` (if using local files)

### Step 5: Present to User

```
## Architecture Scan Results

I scanned [N] files and found [M] entropy indicators.

**Top 3 deepening opportunities:**

1. [RFC title] — [effort], [impact]
   → [One-sentence description]

2. [RFC title] — [effort], [impact]
   → [One-sentence description]

3. [RFC title] — [effort], [impact]
   → [One-sentence description]

I've filed these as issues [list].
Shall I start implementing RFC #1?
```

## Edge Cases

**"Everything looks fine"**
→ Good! But still check:
- Are there modules that are deep but could be deeper?
- Are there emerging patterns that should be abstracted soon?
- Is the domain language in CONTEXT.md still accurate?

**"The codebase is too large to scan"**
→ Focus on the area you're currently working in. Run the scan on `src/features/current-feature/` instead of the whole repo.

**"This would require a massive refactor"**
→ Break it into incremental steps. Each PR should be reviewable in <30 minutes. File a "meta-RFC" that links to smaller child RFCs.

## Success Criteria

This skill succeeded if:
- At least 3 entropy indicators were identified
- At least 1 RFC was filed with clear acceptance criteria
- The user approved at least 1 RFC for implementation
- No false positives (every identified issue is real)

---

## Auto-Activation & Cross-References

**This skill auto-activates when:** See description frontmatter for trigger keywords.

**Chains to (downstream only — no circular loops):**
- `zoom-out` — typically used after this skill completes
- `tdd-workflow` — typically used after this skill completes

**Base layer always active:**
- `aaa-anti-patterns` — quality gates on every output
- `optimized-workflow` — execution rules on every task
- `e2e-validation` — test requirements on every production write
