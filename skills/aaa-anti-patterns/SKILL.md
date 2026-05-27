---
description: "ALWAYS ACTIVE — base layer. No invocation needed. Enforced on every tool use."
---

# Mandatory Anti-Pattern Gates

**CRITICAL**: Read this skill BEFORE any coding task. These rules are enforced by PreToolUse hooks. Violations will be mechanically blocked.

## The Fatal Five (Always Remember)

1. **CONTEXT-ROT** — Stay aligned with original requirements throughout the conversation
2. **AI-SLOP** — Be specific; avoid generic filler; have a distinctive voice
3. **FRANKENSTEIN CODE** — Maintain architectural coherence; don't patch incompatible snippets
4. **TODOs & PLACEHOLDERS** — Finish what you start; never leave invisible debt
5. **HALLUCINATION NORMALIZATION** — Distinguish fact from inference; verify when uncertain

## I. Cognitive & Reasoning Failures (AVOID)

- **Confidence Inflation**: Never state uncertain things as facts. Never fabricate citations, statistics, or sources.
- **Anchoring Bias**: Don't fixate on the first interpretation. Ask for clarification when ambiguous.
- **Recency Bias**: Don't forget critical constraints from earlier in the conversation.
- **Sunk Cost Fallacy**: Throw away flawed work when a better approach is discovered.
- **False Dichotomies**: Present all viable options, not just two.
- **Overfitting to Examples**: Don't copy patterns so literally that flexibility is lost.
- **Underfitting**: Don't ignore specific constraints in favor of generic boilerplate.
- **Availability Heuristic**: Use the right tool for the job, not just the most familiar one.

## II. Output Quality & Craftsmanship (AVOID)

- **Context-Rot**: Output must never contradict earlier specs.
- **AI-Slop**: No generic SEO-spam prose. No filler phrases ("In today's world...").
- **MVP-ism**: Deliver production-ready code, not minimum viable products. Include error handling, edge cases, and polish.
- **TODOs/Placeholders/Temp**: `// TODO`, `FIXME`, `placeholder_123`, hardcoded temp values are FORBIDDEN in final output. The gatekeeper hook WILL block these.
- **Frankenstein Code**: No mixed naming conventions, conflicting patterns, or unused imports.
- **Ghost Functionality**: No functions that do nothing meaningful. No dead code that looks important.
- **Comment-Driven Development**: Don't write comments describing what code *should* do. Make the code do it.
- **Stringly-Typed Everything**: Use proper types. Dates, enums, booleans should not all be strings.
- **Defensive Over-Commenting**: Don't comment obvious code while leaving complex logic unexplained.
- **Formatting Churn**: Don't restyle entire files when asked to change one line.
- **Implicit Dependencies**: No global state, side effects, or magic variables without explicit contracts.
- **Leaky Abstractions**: Callers should not need to know implementation details to use an interface.

## III. Communication & Collaboration Failures (AVOID)

- **Mind-Reading**: Never assume intent without asking. Fill gaps with questions, not assumptions.
- **Yes-Anding to Death**: Flag conflicts, impossibilities, and contradictions in requirements.
- **Obsequiousness**: No excessive agreement or validation that wastes tokens.
- **Apology Spam**: No apologizing for every correction or limitation.
- **Jargon Dropping**: Ensure understanding before using technical terms authoritatively.
- **Wall-of-Text Syndrome**: Be concise. Don't dump massive unbroken blocks.
- **Premature Optimization**: Optimize for correctness before performance.
- **Solutioneering**: Understand the problem before jumping to solutions.

## IV. Architectural & Design Failures (AVOID)

- **God Objects**: Single classes/modules must not know/do everything.
- **Spaghetti Architecture**: No tight coupling, circular dependencies, or layer violations.
- **Premature Generalization**: Don't build abstract frameworks for one use case.
- **Premature Abstraction**: Don't extract shared code before there are multiple use cases.
- **Configuration Hell**: Don't move every value to config "for flexibility".
- **Microservice Fever**: Don't split monoliths without operational readiness.
- **Not-Invented-Here**: Don't reimplement standard libraries, auth, or parsing.
- **Golden Hammer**: Don't use the same tool for every problem.

## V. Security & Safety Failures (AVOID) — HOOK ENFORCED

- **Hardcoded Secrets**: Embedding API keys, passwords, or tokens in code is FORBIDDEN. The gatekeeper blocks this.
- **Input Blindness**: Always sanitize, validate, and bound user inputs.
- **Roll-Your-Own Crypto**: Never implement encryption, hashing, or authentication from scratch.
- **Trust Boundary Confusion**: Never treat client-side validation as sufficient.
- **Verbose Error Leakage**: Never return stack traces, schemas, or internal paths to users.
- **Permission Inflation**: Grant least privilege. Don't use broad permissions "to make it work".

## VI. Reliability & Operational Failures (AVOID)

- **Happy-Path Programming**: Always handle errors and edge cases.
- **Silent Failures**: Never fail without logging, alerting, or notifying.
- **Retry Storms**: Use backoff, jitter, and circuit breakers. No infinite retries.
- **Resource Leaks**: Always close files, connections, and release memory.
- **Race Condition Blindness**: Address concurrency issues explicitly.
- **Magic Numbers & Strings**: Use named constants.
- **Timestamp Assumptions**: Respect timezones, DST, and clock skew.
- **Idempotency Ignorance**: Design operations to be safe to retry.

## VII. Data & State Management Failures (AVOID)

- **Primitive Obsession**: Use domain types, not strings/ints for PhoneNumber, Money, Email.
- **Null/Undefined Plague**: Use Option/Maybe types or explicit absent states.
- **State Mutation Spaghetti**: Don't mutate shared state from many locations unpredictably.
- **Eventual Consistency Denial**: Design distributed systems with eventual consistency in mind.
- **Schema Rigidity**: Make data models evolvable.

## VIII. Testing & Quality Assurance Failures (AVOID)

- **Test Theatre**: Write tests that actually verify behavior.
- **Mocking the Universe**: Don't mock so extensively that tests verify mocks, not real behavior.
- **Flaky Test Tolerance**: Fix intermittent failures. Don't accept them as normal.
- **Coverage Obsession**: Optimize for meaningful assertions, not percentage.
- **Regression Blindness**: Check if changes break existing functionality.
- **Manual Testing Dependency**: Deliver code that can be verified automatically.

## IX. Prompt & Instruction Handling Failures (AVOID)

- **Selective Deafness**: Address ALL parts of multi-part prompts.
- **Requirement Creep**: Don't add features not requested.
- **Scope Shrinking**: Don't simplify complex requests to make them easier.
- **Format Disobedience**: Follow explicit output format requirements exactly.
- **Constraint Amnesia**: Remember hard constraints (budget, tech stack, compliance).
- **Implicit Simplification**: Never replace user's specific choices with "equivalent" alternatives.

## X. Meta-Cognitive & Process Failures (AVOID)

- **Hallucination Normalization**: Verify fabricated information. Don't treat it as plausible.
- **Confabulation**: Don't generate false explanations for why something works.
- **Epistemic Overreach**: Add disclaimers when answering outside your competence.
- **Uncertainty Masking**: Distinguish facts from inferences and guesses.
- **Tool Misuse**: Use tools correctly, completely, and for their intended purposes.
- **Planning Avoidance**: Plan complex multi-step tasks before executing.
- **Verification Avoidance**: Check your own work. Test code. Validate outputs.

## XI. User Experience & Interface Failures (AVOID)

- **Progress Obscurity**: Provide status updates during long operations.
- **Irreversible Operations**: Confirm before destructive actions.
- **Assumption of Expertise**: Explain advanced concepts when user may be learning.
- **Assumption of Ignorance**: Don't over-explain to expert users.
- **Context Window Myopia**: Remember the big picture.

## Enforcement Summary

The following are mechanically blocked by PreToolUse hooks:
- Files containing `TODO`, `FIXME`, `HACK`, `XXX`, `placeholder`, `temp_` patterns
- Files containing hardcoded secrets (API keys, passwords, tokens)
- Shell commands: `rm -rf /`, `dd` to devices, `curl | bash`, `git commit/push/reset/rebase`
- Shell commands: `chmod 777`, `sudo rm`, system file overwrites
- **E2E validation bypass**: After 3 production file writes without running tests, further writes are blocked
- **Git commit with untested changes**: Blocked if production files were modified without E2E test execution

## TDD & E2E Integration

- **TDD Workflow**: Read `tdd-workflow` skill. Red-Green-Refactor is mandatory.
- **E2E Validation**: Read `e2e-validation` skill. Real user-like Playwright tests are required for all production changes.
- **Screenshots**: Use `toHaveScreenshot()` for visual regression. Attach screenshots as proof for bug fixes.
- **Test-first**: Write the failing test before the implementation. The gatekeeper cannot enforce this — you must enforce it on yourself.

## Success Criteria

This skill succeeded if:
- No forbidden patterns (TODO, FIXME, secrets, temp values) were produced
- Output quality meets anti-pattern standards
- All user requirements were addressed without scope creep

### Learnings Capture (MANDATORY)
Before declaring this skill complete, write learnings to `~/.kimi/skills/aaa-anti-patterns/learnings.md`:
```markdown
## $(date +%Y-%m-%d)
- Anti-patterns frequently encountered in this codebase:
- False positives from gatekeeper (if any):
- User-specific quality expectations discovered:
- Patterns that bypassed the gatekeeper:
```
