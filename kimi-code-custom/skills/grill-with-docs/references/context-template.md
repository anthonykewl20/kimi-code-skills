# CONTEXT.md Template

# Domain Language

> This document defines the shared vocabulary for this project.
> Update it every time `/skill:grill-with-docs` discovers a new term.
> This is a living document — it should grow as the project grows.

## How to Use This Document

- **When naming things**: Check if a term already exists before inventing a new one
- **When reviewing code**: Verify that code uses the shared language consistently
- **When onboarding**: New team members (human or AI) should read this first
- **When writing docs**: Use these terms to keep documentation concise

## Core Concepts

| Term | Definition | Where Used | Avoid Saying |
|---|---|---|---|
| [Example] materialization | Converting a virtual entity into a real file-system object | `src/materialization.ts` | "making it real", "file creation" |
| [Fill in] | | | |

## Module Map

| Module | Responsibility | Key Files | Depends On |
|---|---|---|---|
| [Example] Auth | Authentication, session management, token handling | `src/auth/` | Users, Security |
| [Fill in] | | | |

## Process Map

| Process | Trigger | Steps | Output |
|---|---|---|---|
| [Example] User Registration | POST /register | 1. Validate input 2. Hash password 3. Create user 4. Send welcome email | User record + session token |
| [Fill in] | | | |

## Anti-Language (Terms We Do NOT Use)

| Don't Say | Say Instead | Why |
|---|---|---|
| "the thing" | [specific term] | Ambiguous |
| "fix it" | [specific action] | Vague |

## Decisions

See `docs/adr/` for Architecture Decision Records.
Key decisions affecting language:
- [Link to ADR] → defines terms [list]
