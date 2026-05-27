---
name: diagnose
description: 6-step disciplined debugging. Triggers: user says 'bug', 'broken', 'error', 'crash', 'hang', 'race condition', 'intermittent failure', 'production incident'.

---

# /diagnose — Disciplined Debugging

> "Debugging is twice as hard as writing the code in the first place. Therefore, if you write the code as cleverly as possible, you are, by definition, not smart enough to debug it." — Brian Kernighan

## When to Use

- Any bug that takes >10 minutes to understand
- Intermittent / flaky failures
- Performance regressions
- "It works on my machine" issues
- Production incidents

## When NOT to Use

- Syntax errors (compiler tells you the fix)
- Obvious null reference with clear stack trace
- One-line fixes where the cause is self-evident

## The Diagnosis Loop

### Step 1: REPRODUCE — Make It Fail Consistently

**Goal:** Convert an intermittent or vague bug into a reliable reproduction.

**Actions:**
1. Identify the exact conditions that trigger the bug
   - Specific input data?
   - Specific sequence of actions?
   - Specific environment (OS, browser, Node version)?
   - Race condition or timing-dependent?

2. Create a minimal reproduction script
   - Strip away unrelated code
   - Use hardcoded data instead of database queries
   - Run in isolation (no other services)

3. Verify reproduction reliability
   - Run the repro script 5+ times
   - If it fails 5/5, you have a solid repro
   - If it fails 3/5, you have a race condition — note the pattern

**Checklist:**
- [ ] I can make the bug happen on demand
- [ ] I have a script/test that reproduces it
- [ ] I know which conditions are necessary vs coincidental

### Step 2: MINIMISE — Strip to the Essential Failure

**Goal:** Remove everything that doesn't contribute to the bug.

**Actions:**
1. Binary search through the code
   - Comment out half the function → does it still fail?
   - If yes, the bug is in the remaining half
   - If no, the bug is in the commented half
   - Repeat until you find the minimal failing code

2. Remove dependencies
   - Can you reproduce without the database? Use mock data.
   - Can you reproduce without the frontend? Test the API directly.
   - Can you reproduce without the framework? Test the pure function.

3. Minimise data
   - What's the smallest input that triggers the bug?
   - Can you reproduce with 1 record instead of 1000?

**Checklist:**
- [ ] I have the smallest possible code that still fails
- [ ] I have the smallest possible input that triggers it
- [ ] I've eliminated all unrelated dependencies

### Step 3: HYPOTHESISE — Form a Testable Theory

**Goal:** Generate specific, falsifiable theories about the cause.

**Actions:**
1. List 3-5 possible causes, ranked by likelihood
   - Don't just guess one — list multiple
   - Consider: logic error, data issue, environment, dependency, race condition

2. For each hypothesis, define:
   - What you'd expect to see if this hypothesis is TRUE
   - What you'd expect to see if this hypothesis is FALSE
   - How to test it (specific experiment)

3. Pick the most likely hypothesis to test first
   - Usually the simplest explanation (Occam's Razor)
   - But don't ignore "unlikely" hypotheses if they fit the data

**Example:**
```
Hypothesis A: Floating-point precision loss in amount calculation
  → If TRUE: $999.99 works, $1000.00 fails
  → Test: Log raw values before/after parseFloat

Hypothesis B: Database timeout on large invoices
  → If TRUE: Small invoices work, large ones fail
  → Test: Reproduce with $10 invoice vs $10,000 invoice

Hypothesis C: Race condition in concurrent webhook processing
  → If TRUE: Single webhook works, multiple simultaneous fail
  → Test: Send 1 webhook, then 10 simultaneously
```

**Checklist:**
- [ ] I have 3+ ranked hypotheses
- [ ] Each hypothesis is testable (has a pass/fail experiment)
- [ ] I know what result would disprove each hypothesis

### Step 4: INSTRUMENT — Add Targeted Logging

**Goal:** Collect data to confirm or reject your leading hypothesis.

**Actions:**
1. Add logging at key points (not everywhere)
   - Input values before processing
   - Intermediate calculation results
   - State before/after critical operations
   - External API responses

2. Use assertions as "living logs"
   ```javascript
   console.assert(amount >= 0, `Invalid amount: ${amount}`);
   ```

3. Run the repro script and collect output
   - Save logs to a file for analysis
   - Look for patterns, not single anomalies

**Rules:**
- Don't add logging "just in case" — target your hypothesis
- Remove or disable instrumentation after fixing
- Don't change behavior while instrumenting (Heisenberg principle)

**Checklist:**
- [ ] I've added targeted logging for my leading hypothesis
- [ ] I've run the repro and collected output
- [ ] The data supports or rejects my hypothesis

### Step 5: FIX — Apply the Minimal Correct Fix

**Goal:** Fix the root cause, not the symptom.

**Actions:**
1. Verify you've found the ROOT cause
   - Ask "why" 5 times:
     - Why did it fail? → parseFloat lost precision
     - Why did parseFloat lose precision? → We passed a string with 3 decimal places
     - Why did we pass 3 decimal places? → Currency rounding upstream
     - Why did rounding produce 3 places? → Rounding function uses toFixed(3)
     - Why toFixed(3)? → Copy-paste from weight calculation
   → Root cause: Wrong rounding precision for currency

2. Apply the smallest fix that addresses the root cause
   - Don't refactor adjacent code
   - Don't "improve" while fixing
   - One fix per change

3. Verify the fix with your repro script
   - Run the repro 5+ times — it should pass every time
   - If it still fails, your fix addressed a symptom, not the cause

**Checklist:**
- [ ] I've identified the root cause (not just a symptom)
- [ ] The fix is minimal and targeted
- [ ] The repro script passes consistently

### Step 6: REGRESSION TEST — Prevent Recurrence

**Goal:** Ensure this bug never returns silently.

**Actions:**
1. Add a test that would have caught this bug
   - Use the minimal repro as the test case
   - Name it descriptively: `should handle amounts over $999.99`

2. Add tests for adjacent edge cases
   - If the bug was at $1000, also test $999.99, $1000.01, $9999.99
   - Think: "What other values could trigger the same root cause?"

3. Document the fix
   - In the commit message, explain the root cause
   - Reference the bug report/issue number

**Checklist:**
- [ ] A regression test exists and passes
- [ ] Edge cases are covered
- [ ] Commit message explains the root cause

## Edge Cases

**"I can't reproduce it"**
→ Check environment differences (OS, Node version, database state, env vars). Use Docker to match production exactly.

**"It only happens in production"**
→ Add structured logging to production. Use feature flags to enable verbose logging for specific users/sessions. Reproduce with production data snapshot (sanitized).

**"It's a race condition"**
→ Add artificial delays (`setTimeout`, `sleep`) to exaggerate the race. Run the repro 100x in a loop. Use thread sanitizers or concurrency analyzers.

## Success Criteria

This skill succeeded if:
- The bug is reliably reproducible
- The root cause is identified (not just a symptom)
- The fix is minimal and doesn't touch unrelated code
- A regression test prevents recurrence
- The commit message explains WHY, not just WHAT

### Learnings Capture (MANDATORY)
Before declaring this skill complete, write learnings to `~/.kimi/skills/diagnose/learnings.md`:
```markdown
## $(date +%Y-%m-%d)
- Bug category/pattern encountered:
- Diagnostic technique that worked:
- False leads that wasted time:
- Tool or approach that helped:
```

---

## Auto-Activation & Cross-References

**This skill auto-activates when:** See description frontmatter for trigger keywords.

**Chains to (downstream only — no circular loops):**
- `tdd-workflow` — typically used after this skill completes

**Base layer always active:**
- `aaa-anti-patterns` — quality gates on every output
- `optimized-workflow` — execution rules on every task
- `e2e-validation` — test requirements on every production write
