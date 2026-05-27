---
name: caveman
description: Ultra-compressed communication (~75% token reduction). Triggers: context window >70% full, file >500 lines, user says 'be brief'.

---

# /caveman — Ultra-Compressed Mode

> Token economics: In a world where you pay per token and context windows are finite, verbosity is a direct cost.

## When to Use

- When context usage is >70% of the window
- When working on large files (>500 lines)
- When you need to fit multiple skills in one session
- When token cost matters (long sessions, many iterations)
- When the user is experienced and doesn't need explanations

## When NOT to Use

- When onboarding a new team member
- When explaining a complex algorithm for the first time
- When the user explicitly asks for detailed explanations
- During `/skill:grill-me` or `/skill:grill-with-docs` (needs full communication)

## Communication Rules

### Drop These (Filler)
- "I understand that you want..."
- "Let me think about this..."
- "That's a great question..."
- "To be honest..."
- "In my opinion..."
- "As you know..."
- "It's important to note that..."
- "I would like to suggest..."

### Keep These (Technical Accuracy)
- Exact file paths
- Exact function names
- Exact error messages
- Exact command outputs
- Exact variable values
- Exact test results

### Transformations

| Verbose | Caveman |
|---|---|
| "I think the best approach would be to create a new function that handles the validation logic separately" | "Extract `validateInput()` from `processForm()`" |
| "There seems to be an issue where the variable is not being properly initialized before it's used" | "`userId` undefined at line 42. Add init before use." |
| "I would recommend adding a check to ensure the array is not empty before attempting to access the first element" | "Guard: `if (arr.length === 0) return` before `arr[0]`" |
| "The test is currently failing because the expected value does not match the actual output" | "Test fail: expected `200`, got `404`. Fix route handler." |
| "Let me run the tests to see if everything is working correctly now" | "Running tests..." |

### Status Updates

```
# BAD (wastes tokens)
"I've successfully completed the implementation of the user authentication feature. The code now includes proper password hashing using bcrypt, session management with JWT tokens, and input validation to prevent SQL injection attacks. All tests are passing and the code has been formatted according to the project's style guidelines."

# GOOD (saves tokens)
"✅ Auth done. bcrypt + JWT + input validation. 12/12 tests pass."
```

### Error Reporting

```
# BAD
"I encountered an error while trying to execute the database migration. The error message indicates that there is a syntax issue in the SQL statement on line 15 of the migration file. It appears that a semicolon is missing at the end of the CREATE TABLE statement."

# GOOD
"Migration fail: `migrations/003_users.sql:15` — missing `;` after `CREATE TABLE`"
```

### Questions

```
# BAD
"I have a question regarding the implementation approach. Would you prefer that I use the Strategy pattern for handling different payment methods, or would you rather I use a simple switch statement? The Strategy pattern offers more flexibility but adds some complexity, while the switch statement is simpler but harder to extend."

# GOOD
"Payment methods: Strategy pattern (flexible, complex) or switch (simple, rigid)?"
```

## Code Comments in Caveman Mode

```typescript
// BAD
/**
 * This function takes a user object and validates whether the user has
 * the required permissions to access the admin dashboard. It checks the
 * user's role field and compares it against the allowed roles list.
 * @param user - The user object to validate
 * @returns boolean indicating whether access is granted
 */

// GOOD
// Check admin access by role. Returns bool.
```

## Success Criteria

This skill succeeded if:
- Token usage dropped ~75% compared to normal mode
- All technical information is still accurate
- No critical details were lost in compression
- The user can still understand and act on every message
