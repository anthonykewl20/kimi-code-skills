# Debugging Patterns Reference

## Common Bug Categories & Diagnostic Techniques

### 1. Off-By-One Errors
**Symptoms:** Loop boundaries, array indexing, pagination
**Technique:** Test with n=0, n=1, n=2, n=max
**Example:** `for (let i = 0; i <= arr.length; i++)` → should be `<` not `<=`

### 2. Null / Undefined Reference
**Symptoms:** `Cannot read property 'x' of undefined`
**Technique:** Trace the variable's lifecycle. Where is it set? Where could it be unset?
**Fix:** Add early return or default value at the source, not at every usage.

### 3. Async / Await Issues
**Symptoms:** Promise not awaited, race conditions, "undefined" in async context
**Technique:** Add `console.log` before and after every async call. Check for missing `await`.
**Common causes:**
- `async` function without `await`
- `.then()` without returning the promise
- `forEach` with async callbacks (use `for...of` instead)

### 4. State Mutation
**Symptoms:** Value changes unexpectedly, "ghost" data
**Technique:** Log object identity (`===`) before/after operations. Check for shallow copy vs deep copy.
**Fix:** Use immutable patterns. `const newObj = { ...oldObj, field: newValue }`

### 5. Floating-Point Precision
**Symptoms:** $100.00 becomes $99.9999999999
**Technique:** Log raw values with full precision. Check `parseFloat` vs integer math.
**Fix:** Store currency as integer cents. Never use floating-point for money.

### 6. Encoding / Character Issues
**Symptoms:** Garbled text, `Ã©` instead of `é`, CSV import fails
**Technique:** Check file encoding (UTF-8 BOM?). Check database charset. Check HTTP headers.
**Fix:** Standardize on UTF-8 everywhere. Explicitly declare encoding in all I/O operations.

### 7. Cache Invalidation
**Symptoms:** Stale data, updates not reflecting, "works after refresh"
**Technique:** Check cache TTL. Check cache key generation. Check invalidation triggers.
**Fix:** Use cache-busting keys. Invalidate on write, not on read.

### 8. Environment Differences
**Symptoms:** "Works on my machine", CI failures only
**Technique:** Compare `process.env`, Node versions, OS differences, timezone settings
**Fix:** Use `.nvmrc`, Docker, or `engines` in package.json. Standardize env vars.
