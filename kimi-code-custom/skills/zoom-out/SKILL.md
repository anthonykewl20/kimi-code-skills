---
name: zoom-out
description: Tell the agent to zoom out and give broader context or a higher-level perspective on an unfamiliar section of code.
---

# /zoom-out — System Context Retrieval

> "We can't see the forest for the trees." — When you're deep in implementation, you lose sight of the architecture.

## When to Use

- When you encounter unfamiliar code and need to understand its purpose
- When a change requires touching multiple files and you're not sure why
- When you need to explain a module's role to a teammate
- Before `/skill:improve-codebase-architecture` to understand current design

## When NOT to Use

- When you already understand the code (wastes tokens)
- For trivial, self-contained functions
- When you're in the middle of implementing (context switch cost)

## What This Skill Does

1. Identifies the current file/module
2. Reads `CONTEXT.md` for domain language
3. Reads the module's entry point or index file
4. Traces imports/exports to understand the module's boundaries
5. Explains the module's role in the system architecture

## Process

### Step 1: Identify Current Context

Determine what file/module the user is asking about:
- If user mentions a specific file, use that
- If user says "this code", check the most recently viewed file
- If unclear, ask: "Which file or module should I zoom out on?"

### Step 2: Read Module Boundaries

Read the module's:
- Entry point (`index.ts`, `main.py`, etc.)
- Public API (exported functions/classes)
- README or module documentation (if exists)

### Step 3: Trace Dependencies

```bash
# Find what this module imports (its dependencies)
grep -r "^import.*from" src/module/ | head -20

# Find what imports this module (its consumers)
grep -r "from.*module" src/ | head -20
```

### Step 4: Explain in System Context

Produce a concise explanation:

```
## Zoom-Out: [Module Name]

**Role in System:** [One sentence — what this module does for the whole app]

**Domain Language:**
- [Term from CONTEXT.md]: [How this module implements it]

**Dependencies:**
- [Module A]: [Why it needs it]
- [Module B]: [Why it needs it]

**Consumers:**
- [Module C]: [How it uses this module]
- [Module D]: [How it uses this module]

**Architecture Pattern:**
[e.g., "Repository pattern — abstracts data access from business logic"]

**Key Design Decisions:**
- [ADR reference or inline note]
- [Why this design was chosen]

**When to Touch This Module:**
- [Scenario 1: e.g., "Adding a new entity type"]
- [Scenario 2: e.g., "Changing database schema"]

**When NOT to Touch This Module:**
- [Scenario 1: e.g., "UI changes — go to components/ instead"]
```

## Example

```
## Zoom-Out: src/auth/

**Role in System:** Manages identity verification and session lifecycle for all user-facing features.

**Domain Language:**
- "persistent session": Implemented via secure httpOnly cookies with 30-day TTL
- "token pair": Access token (15min) + refresh token (30 days)

**Dependencies:**
- `src/users/`: Reads/writes user records during authentication
- `src/security/`: Uses `PasswordHasher` and `TokenGenerator`
- `src/email/`: Dispatches verification and password reset emails

**Consumers:**
- `src/api/middleware.ts`: Uses `AuthGuard` to protect routes
- `src/pages/`: Uses `useAuth()` hook to check login state
- `src/admin/`: Uses `requireAdmin()` for role-based access

**Architecture Pattern:**
Port-Adapter pattern. `AuthService` is the port. `JWTAdapter` and `CookieAdapter` are implementations.

**Key Design Decisions:**
- ADR 20260517: Chose httpOnly cookies over localStorage for XSS protection
- ADR 20260518: Chose token rotation over long-lived sessions for security

**When to Touch This Module:**
- Adding new auth methods (OAuth, SSO)
- Changing session duration or security policies
- Adding role-based access control

**When NOT to Touch This Module:**
- UI layout changes (go to `src/components/`)
- API route additions (go to `src/api/routes/`)
- Database schema changes unrelated to auth (go to `src/users/`)
```

## Edge Cases

**"This module has no documentation"**
→ Infer from code structure, imports, and naming. Use `CONTEXT.md` terms to fill gaps. Note: "No documentation found — inferred from code."

**"This module is a third-party library"**
→ Explain how YOUR code uses it, not what the library does. "We use Express as the HTTP server framework. Our custom middleware lives in `src/api/middleware/`."

## Success Criteria

This skill succeeded if:
- The user understands the module's role in the system
- The user knows which other modules depend on this one
- The user knows when it's appropriate to modify this module
- The explanation uses the project's domain language
