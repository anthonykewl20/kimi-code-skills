#!/usr/bin/env python3
"""
Kimi CLI Mechanical Gatekeeper
MANDATORY HARD GATES for tool use operations.

Exit codes:
  0 = allow (with optional JSON stdout for structured decisions)
  2 = block (reason in stderr)

This script implements mechanical enforcement of anti-patterns and E2E validation.
It is fail-open: any crash or exception allows the operation.

Environment variables:
  KIMI_GATEKEEPER_BYPASS=1  — Bypass all gates (emergency only)
  KIMI_E2E_BUFFER=N         — Number of production file writes allowed before
                              requiring tests (default: 3)
"""

import fcntl
import json
import os
import re
import sys
import time
from pathlib import Path


# ── Configuration ──────────────────────────────────────────────────────────────

E2E_BUFFER = int(os.environ.get("KIMI_E2E_BUFFER", "3"))
BYPASS = os.environ.get("KIMI_GATEKEEPER_BYPASS", "").strip() in ("1", "true", "yes")

# Production code extensions (files that require E2E validation when changed)
PROD_EXTENSIONS = {
    ".php", ".js", ".ts", ".jsx", ".tsx", ".py", ".go", ".java", ".rb",
    ".rs", ".c", ".cpp", ".h", ".swift", ".kt", ".scala", ".cs", ".fs",
    ".elm", ".vue", ".svelte", ".css", ".scss", ".less", ".html", ".htm",
    ".tpl", ".blade.php", ".twig", ".smarty",
}

# Extensions that NEVER trigger E2E validation
EXCLUDED_EXTENSIONS = {
    ".json", ".md", ".yml", ".yaml", ".toml", ".ini", ".env", ".sql",
    ".sh", ".dockerfile", ".lock", ".txt", ".xml", ".svg", ".ico",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".webm",
}

# Path segments that indicate test/non-prod files
EXCLUDED_PATH_SEGMENTS = ("/test/", "/tests/", "/e2e/", "/__tests__/", "/spec/", "/mocks/", "/fixtures/")

# ── Anti-Slop Gate Configuration ───────────────────────────────────────────────

DEFAULT_CHECKPOINT_INTERVAL = int(os.environ.get("KIMI_CHECKPOINT_INTERVAL", "15"))
CHECKPOINT_MARKER = "COGNITIVE CHECKPOINT COMPLETE"
CHECKPOINT_DIRS = (".kimi/sessions", ".kimi/plans")
ERROR_RECOVERY_INDICATORS = [
    r"(?i)error\s*:",
    r"(?i)failed",
    r"(?i)fatal\s*:",
    r"(?i)not\s+found",
    r"(?i)command\s+not\s+found",
    r"(?i)no\s+such\s+file",
    r"(?i)cannot\s+find",
    r"(?i)exit\s+(?:[1-9]\d*)",
]
# Tools that count as "read" operations (reset consecutive_writes_without_read)
READ_TOOLS = {"ReadFile", "Grep", "Glob", "Agent", "Shell", "FetchURL", "SearchWeb"}
# Tools that count as "write" operations (increment consecutive_writes_without_read)
WRITE_TOOLS = {"WriteFile", "StrReplaceFile"}

# Test command patterns (matched against shell commands)
TEST_COMMAND_PATTERNS = [
    r"(?i)playwright\s+test",
    r"(?i)npx\s+playwright",
    r"(?i)pytest",
    r"(?i)python\s+-m\s+pytest",
    r"(?i)jest",
    r"(?i)npx\s+jest",
    r"(?i)vitest",
    r"(?i)npx\s+vitest",
    r"(?i)npm\s+test",
    r"(?i)npm\s+run\s+test",
    r"(?i)yarn\s+test",
    r"(?i)yarn\s+test:\w+",
    r"(?i)pnpm\s+test",
    r"(?i)cargo\s+test",
    r"(?i)go\s+test",
    r"(?i)deno\s+test",
    r"(?i)bun\s+test",
    r"(?i)phpunit",
    r"(?i)vendor/bin/phpunit",
    r"(?i)artisan\s+test",
    r"(?i)php\s+artisan\s+test",
    r"(?i)mix\s+test",
    r"(?i)ruby\s+-Ilib:test",
]

# Skill activation patterns (matched against shell commands or tool input)
SKILL_ACTIVATION_PATTERN = re.compile(r"/(skill):([a-zA-Z0-9_-]+)")

# Learnings file pattern
LEARNINGS_FILE_PATTERN = re.compile(r".*/skills/([^/]+)/learnings\.md$")

# Swarm stage markers (detected in plan/session artifacts)
SWARM_STATUS_MARKERS = {
    "PLAN STATUS": "plan",
    "IMPLEMENTATION STATUS": "implementation",
    "TEST STATUS": "test",
    "SECURITY STATUS": "security",
    "ARCHITECTURE STATUS": "architecture",
    "RELEASE STATUS": "release",
}

# Paths scanned for swarm artifacts (relative to cwd)
SWARM_ARTIFACT_PATHS = [".kimi/plans/", ".kimi/sessions/", ".kimi/governance/reports/"]

# File path patterns that auto-trigger swarm (auth, payment, security)
SWARM_SENSITIVE_PATTERNS = [
    re.compile(r"(?i)(auth|login|password|oauth|session|csrf|xss|sql.?inject)"),
    re.compile(r"(?i)(coinpayments|stripe|paypal|paystack|razorpay|braintree|wallet|payment)"),
    re.compile(r"(?i)(migration|schema|alter\s+table|create\s+table)"),
]

# ── TDD Hard Gate Configuration ───────────────────────────────────────────────

# Test file extensions and path patterns
TEST_FILE_PATTERNS = [
    re.compile(r"(?i)(\.test\.|\.spec\.|_test\.|_spec\.)"),
    re.compile(r"(?i)(/test[s]?/|/__tests__/|/spec/|/e2e/)",),
]

# TDD state machine values: "idle" | "red" | "green"
# idle  = no active TDD cycle
# red   = test file written, waiting for production code
# green = production code written after test, cycle complete

# Alignment markers (detected in plan/session artifacts for grill-me enforcement)
ALIGNMENT_MARKERS = [
    "ALIGNMENT COMPLETE",
    "GRILL STATUS: PASS",
    "GRILL STATUS: COMPLETE",
    "ALIGNMENT SUMMARY",
]

# Path segments that indicate alignment / planning artifacts
ALIGNMENT_ARTIFACT_PATHS = [".kimi/plans/", ".kimi/sessions/", "docs/adr/", "docs/plans/"]

# ── State Management ───────────────────────────────────────────────────────────

def _state_file(session_id: str) -> Path:
    state_dir = Path.home() / ".kimi" / ".gatekeeper"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / f"kimi_gatekeeper_{session_id}.json"


def load_state(session_id: str) -> dict:
    """Load gatekeeper state for a session. Returns empty state if missing/corrupt.
    DEPRECATED: Use load_state_locked for all writes to prevent races."""
    return load_state_locked(session_id)


def save_state(session_id: str, state: dict) -> None:
    """Persist gatekeeper state atomically with file locking. Fail silently."""
    try:
        path = _state_file(session_id)
        tmp_path = Path(f"/tmp/kimi_gatekeeper_{session_id}.tmp")
        # Atomic write: write to temp, then rename
        tmp_path.write_text(json.dumps(state), encoding="utf-8")
        os.replace(str(tmp_path), str(path))
    except Exception:
        pass


def load_state_locked(session_id: str) -> dict:
    """Load state with exclusive file locking to prevent races."""
    try:
        path = _state_file(session_id)
        if path.exists():
            with open(path, "r+") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    data = f.read()
                    if data:
                        return json.loads(data)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception:
        pass
    return {
        "session_id": session_id,
        "pending_writes": 0,
        "changed_files": [],
        "last_test_run": None,
        "validation_required": False,
        # Base layer skills are always active
        "activated_skills": ["aaa-anti-patterns", "optimized-workflow", "e2e-validation"],
        "learnings_recorded": [],
        "swarm_stages_completed": [],
        "swarm_required": False,
        # TDD hard gate state
        "tdd_state": "idle",  # "idle" | "red" | "green"
        "test_files_written": [],
        "prod_files_written": [],
        # Alignment (grill-me) hard gate state
        "alignment_completed": False,
        "alignment_artifact_found": False,
        # Automated learnings event log
        "events": [],  # List of {type, message, timestamp, skill}
        # Anti-Slop gate state
        "tool_use_count": 0,
        "last_checkpoint_at": 0,
        "consecutive_writes_without_read": 0,
        "error_recovery_mode": False,
        "error_recovery_set_at": None,
        "last_error_brief": "",
        "checkpoint_interval": DEFAULT_CHECKPOINT_INTERVAL,
    }


def save_state_locked(session_id: str, state: dict) -> None:
    """Save state with exclusive file locking."""
    try:
        path = _state_file(session_id)
        tmp_path = Path(f"/tmp/kimi_gatekeeper_{session_id}.tmp")
        with open(path, "a+") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                tmp_path.write_text(json.dumps(state), encoding="utf-8")
                os.replace(str(tmp_path), str(path))
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception:
        pass


def clear_state(session_id: str) -> None:
    """Remove state file for a session."""
    try:
        path = _state_file(session_id)
        if path.exists():
            with open(path, "a+") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    path.unlink(missing_ok=True)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception:
        pass


# ── Helpers ────────────────────────────────────────────────────────────────────

def block(reason: str) -> None:
    sys.stderr.write(f"[GATEKEEPER BLOCKED] {reason}\n")
    sys.exit(2)


def allow() -> None:
    sys.exit(0)


def warn(message: str) -> None:
    sys.stderr.write(f"[GATEKEEPER WARNING] {message}\n")


def log_event(session_id: str, event_type: str, message: str, skill: str = "") -> None:
    """Log a gate event for automated learnings generation."""
    if not session_id:
        return
    state = load_state_locked(session_id)
    events = state.get("events", [])
    events.append({
        "type": event_type,
        "message": message,
        "timestamp": time.time(),
        "skill": skill,
    })
    state["events"] = events
    save_state_locked(session_id, state)


def is_production_file(filepath: str) -> bool:
    """Determine if a file change should trigger E2E validation requirements."""
    if not filepath:
        return False
    path_lower = filepath.lower()

    # Exclude test paths
    for seg in EXCLUDED_PATH_SEGMENTS:
        if seg in path_lower:
            return False

    # Exclude by extension
    for ext in EXCLUDED_EXTENSIONS:
        if path_lower.endswith(ext):
            return False

    # Exclude files with .test. or .spec. in name
    if ".test." in path_lower or ".spec." in path_lower:
        return False

    # Include by known production extension
    for ext in PROD_EXTENSIONS:
        if path_lower.endswith(ext):
            return True

    # Default: exclude unknown extensions to avoid false positives
    return False


def is_test_command(command: str) -> bool:
    """Check if a shell command runs tests."""
    if not command:
        return False
    for pattern in TEST_COMMAND_PATTERNS:
        if re.search(pattern, command):
            return True
    return False


def is_git_mutation(command: str) -> bool:
    """Check if command is a git mutation."""
    if not command:
        return False
    git_patterns = [
        r"(?i)git\s+(commit|push|reset|rebase|merge\s+--squash)",
        r"(?i)git\s+checkout\s+-[bB]",
    ]
    for p in git_patterns:
        if re.search(p, command):
            return True
    return False


def extract_skill_activations(command: str) -> list:
    """Extract skill names from shell commands like /skill:tdd or skill:grill-me."""
    if not command:
        return []
    return SKILL_ACTIVATION_PATTERN.findall(command)


def is_learnings_file(filepath: str) -> tuple:
    """Check if filepath is a skill learnings.md. Returns (is_learnings, skill_name)."""
    if not filepath:
        return (False, "")
    match = LEARNINGS_FILE_PATTERN.match(filepath)
    if match:
        return (True, match.group(1))
    return (False, "")


def is_test_file(filepath: str) -> bool:
    """Determine if a file is a test file (for TDD red-phase tracking)."""
    if not filepath:
        return False
    path_lower = filepath.lower()
    # Check test path segments (with or without leading slash)
    test_segments = ("/test/", "/tests/", "/e2e/", "/__tests__/", "/spec/", "/mocks/", "/fixtures/")
    for seg in test_segments:
        if seg in path_lower or seg.lstrip("/") in path_lower:
            return True
    # Check test file name patterns
    for pattern in TEST_FILE_PATTERNS:
        if pattern.search(path_lower):
            return True
    # Check test extensions
    if ".test." in path_lower or ".spec." in path_lower:
        return True
    if "_test." in path_lower or "_spec." in path_lower:
        return True
    return False


def _find_alignment_artifacts() -> bool:
    """Scan artifact paths for alignment/grill-me completion markers."""
    cwd = Path.cwd()
    for rel_path in ALIGNMENT_ARTIFACT_PATHS:
        artifact_dir = cwd / rel_path
        if not artifact_dir.exists():
            continue
        for filepath in artifact_dir.rglob("*"):
            if not filepath.is_file():
                continue
            if filepath.suffix not in (".md", ".txt", ""):
                continue
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                for marker in ALIGNMENT_MARKERS:
                    if marker in content:
                        return True
            except Exception:
                continue
    return False


# ── Pattern Databases ──────────────────────────────────────────────────────────

CONTENT_BLOCK_PATTERNS = [
    (r"(?i)\bplaceholder[_\-]?\d*\b", "Stub values are forbidden. Use real implementation."),
    (r"(?i)\btemp[_\-]?\d+[_\-]?\b", "Temporary values are forbidden. Use proper naming."),
    (r"(?i)(api[_\-]?key|password|secret|token|auth)\s*[=:]\s*[\"'][^\"']{8,}[\"']", "Hardcoded secrets are forbidden. Use environment variables or config files."),
    (r"(?i)(sk-|ghp-|glpat-|hp_|AKIA|aws[_\-]?secret)[a-zA-Z0-9_\-]{10,}", "Hardcoded API keys or tokens detected."),
    (r"(?i)rm\s+-rf\s+(/|\.\./|~/)", "Dangerous rm command pattern in file content."),
    (r"(?i)chmod\s+777", "Overly permissive chmod 777 is forbidden."),
]

CONTENT_CODE_PATTERNS = [
    (r"(?i)(#|//|/\*|\*)\s*(TODO|FIXME|HACK|XXX|BUG|OPTIMIZE|REVIEW)\s*[:\-]", "TODOs/FIXMEs are forbidden. Finish what you start."),
    (r"(?i)#\s*this\s+should\s+(do|implement|handle)", "Comment-driven development detected. Implement the code, don't just describe it."),
    (r"(?i)#\s*(not|isn\'t)\s+(implemented|working|used|finished)", "Incomplete implementations must be finished before commit."),
]

# Legacy alias for backward compatibility
CONTENT_FORBIDDEN_PATTERNS = CONTENT_BLOCK_PATTERNS + CONTENT_CODE_PATTERNS

SHELL_DANGEROUS_PATTERNS = [
    (r"(?i)rm\s+-rf\s*/\s*($|;|&&|\|\|)", "rm -rf / is permanently blocked."),
    (r"(?i)rm\s+-rf\s+/\s*\S", "rm -rf on absolute paths is blocked without explicit confirmation."),
    (r"(?i)rm\s+-rf\s+\.\.+\s*($|;|&&|\|\|)", "rm -rf on parent directories is blocked."),
    (r"(?i)rm\s+-rf\s+\*\s*($|;|&&|\|\|)", "rm -rf * is blocked. Be specific about what to delete."),
    (r"(?i)dd\s+.*of=/dev/[sh]d", "Direct disk writes with dd are blocked."),
    (r"(?i)mkfs\.[a-z0-9]+\s+/dev/", "Filesystem creation on devices is blocked."),
    (r"(?i)>:?\s*/dev/[sh]d", "Writing to block devices is blocked."),
    (r"(?i)curl\s+.*\|\s*(bash|sh|zsh)", "curl | shell pipe patterns are blocked. Download and inspect first."),
    (r"(?i)wget\s+.*\|\s*(bash|sh|zsh)", "wget | shell pipe patterns are blocked. Download and inspect first."),
    (r"(?i)sudo\s+rm", "sudo rm is blocked."),
    (r"(?i)chown\s+-R\s+root", "Recursive root chown is blocked."),
    (r"(?i)chmod\s+-R\s+777", "Recursive chmod 777 is blocked."),
    (r"(?i)mv\s+/\S+\s+/\S+", "Moving system files is blocked."),
    (r"(?i)>:?\s+/etc/", "Overwriting system config files is blocked."),
    (r"(?i)>:?\s+/usr/", "Overwriting system directories is blocked."),
]

SHELL_WARNING_PATTERNS = [
    (r"(?i)pip\s+install\s+(--user|-U|--upgrade)?\s*\S+", "Package installation outside virtual env. Consider using venv."),
    (r"(?i)npm\s+install\s+-g", "Global npm install detected. Consider local install."),
]


# ── Validators ─────────────────────────────────────────────────────────────────

# File types where code-quality patterns (TODO, comment-driven-dev) apply
CODE_EXTENSIONS = {
    ".php", ".js", ".ts", ".jsx", ".tsx", ".py", ".go", ".java", ".rb",
    ".rs", ".c", ".cpp", ".h", ".swift", ".kt", ".scala", ".cs", ".fs",
    ".elm", ".vue", ".svelte", ".css", ".scss", ".less", ".html", ".htm",
    ".tpl", ".blade.php", ".twig", ".smarty", ".sh", ".bash", ".zsh",
}

# Binary extensions to skip entirely
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".webm", ".ico",
    ".svg", ".pdf", ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z",
    ".woff", ".woff2", ".ttf", ".otf", ".eot", ".mp3", ".wav",
}


def _is_code_file(filepath: str) -> bool:
    """Determine if filepath is a code file (vs docs/binary)."""
    if not filepath:
        return True  # Default to strict when path unknown
    path_lower = filepath.lower()
    for ext in CODE_EXTENSIONS:
        if path_lower.endswith(ext):
            return True
    return False


def validate_file_content(content: str, filepath: str = "") -> None:
    if not content:
        return
    path_lower = (filepath or "").lower()
    # Skip binary files
    for ext in BINARY_EXTENSIONS:
        if path_lower.endswith(ext):
            return
    # Universal blocks (secrets, dangerous commands, temp markers)
    for pattern, reason in CONTENT_BLOCK_PATTERNS:
        if re.search(pattern, content):
            block(f"Content violation in {filepath or 'file'}: {reason}")
    # Code-only blocks (TODOs, comment-driven dev)
    if _is_code_file(filepath):
        for pattern, reason in CONTENT_CODE_PATTERNS:
            if re.search(pattern, content):
                block(f"Content violation in {filepath or 'file'}: {reason}")


def validate_shell_command(command: str) -> None:
    if not command:
        return
    for pattern, reason in SHELL_DANGEROUS_PATTERNS:
        if re.search(pattern, command):
            block(f"Dangerous command blocked: {reason}")
    for pattern, reason in SHELL_WARNING_PATTERNS:
        if re.search(pattern, command):
            warn(f"Shell command warning: {reason}")


def validate_post_tool(tool_name: str, tool_input: dict, tool_output: str) -> None:
    if tool_name == "Shell":
        output_lower = tool_output.lower()
        error_indicators = [
            "permission denied", "not found", "no such file",
            "command not found", "fatal:", "error:", "failed",
        ]
        if any(ind in output_lower for ind in error_indicators):
            warn("Shell output contains error indicators. Ensure errors are handled, not silently ignored.")

    if tool_name in ("WriteFile", "StrReplaceFile"):
        content = tool_input.get("content", "")
        if not content:
            edit = tool_input.get("edit", {})
            if isinstance(edit, list):
                for e in edit:
                    content = e.get("new", "")
                    for pattern, reason in CONTENT_FORBIDDEN_PATTERNS:
                        if re.search(pattern, content):
                            warn(f"File may contain anti-pattern: {reason}")
            elif isinstance(edit, dict):
                content = edit.get("new", "")
                for pattern, reason in CONTENT_FORBIDDEN_PATTERNS:
                    if re.search(pattern, content):
                        warn(f"File may contain anti-pattern: {reason}")
        else:
            for pattern, reason in CONTENT_FORBIDDEN_PATTERNS:
                if re.search(pattern, content):
                    warn(f"File may contain anti-pattern: {reason}")


# ── E2E Validation State Machine ───────────────────────────────────────────────

def track_skill_activation(session_id: str, command: str) -> None:
    """Record skill activations from shell commands. Idempotent."""
    skills = extract_skill_activations(command)
    if not skills:
        return
    state = load_state_locked(session_id)
    for _, skill_name in skills:
        if skill_name not in state["activated_skills"]:
            state["activated_skills"].append(skill_name)
    save_state_locked(session_id, state)


def track_learnings_write(session_id: str, filepath: str) -> None:
    """Record when a skill's learnings.md is written. Idempotent."""
    is_learnings, skill_name = is_learnings_file(filepath)
    if not is_learnings:
        return
    state = load_state_locked(session_id)
    if skill_name not in state["learnings_recorded"]:
        state["learnings_recorded"].append(skill_name)
    save_state_locked(session_id, state)


def check_learnings_gate(session_id: str) -> None:
    """Hard gate: skills activated MUST have learnings recorded.
    
    Attempts auto-generation first. If auto-generation fails (no meaningful
    events captured), BLOCKS the session. The agent must either:
    1. Trigger gate events during the session (go through TDD/alignment/etc.)
    2. Manually write learnings with substantive reflection
    """
    state = load_state_locked(session_id)
    activated = state.get("activated_skills", [])
    recorded = state.get("learnings_recorded", [])
    missing = [s for s in activated if s not in recorded]
    if missing:
        # Try auto-generation first
        auto_written = auto_write_learnings(session_id)
        if auto_written:
            skill_list = ", ".join(auto_written)
            warn(
                f"AUTO-LEARNINGS: Generated concise learnings for {skill_list}. "
                f"Review at ~/.kimi/skills/[skill]/learnings.md"
            )
            return
        # Auto-generation failed — no meaningful behavioral data captured
        skill_list = ", ".join(missing)
        log_event(session_id, "block", f"Learnings auto-generation failed for {skill_list}", "")
        block(
            f"LEARNINGS HARD GATE: Skills activated but no behavioral data captured: {skill_list}. "
            f"Auto-generation failed because zero gate events (blocks/warnings) were logged. "
            f"Either: (1) Go through the workflow gates to generate events, OR "
            f"(2) Manually write substantive learnings to ~/.kimi/skills/[skill]/learnings.md "
            f"with specific mistakes, root causes, and prevention strategies."
        )


def _hash_entry(skill: str, events: list) -> str:
    """Create a fingerprint for deduplication."""
    msgs = sorted(set(e.get("message", "") for e in events))
    return f"{skill}:{':'.join(msgs)}"


def _compress_learnings(content: str) -> str:
    """Compress learnings file to prevent agent overwhelm.
    
    Strategy: Keep last 3 detailed entries + 1 summary of older entries.
    Total: ~10-15 lines max. AI agents can scan this in <2 seconds.
    """
    if not content:
        return content
    
    parts = content.split("\n---\n")
    if len(parts) <= 5:
        # Header + 4 entries or less — no compression needed
        return content
    
    header = parts[0]
    raw_entries = parts[1:]
    
    # Filter out empty strings and existing Patterns summaries
    entries = []
    for e in raw_entries:
        e = e.strip()
        if not e or e.startswith("## Patterns"):
            continue
        entries.append(e)
    
    if len(entries) <= 4:
        # After filtering, not enough to compress
        return "\n---\n".join([header] + raw_entries)
    
    # Keep last 3 detailed entries
    recent = entries[-3:]
    older = entries[:-3]
    
    # Summarize older entries: extract unique block/warn patterns with counts
    block_msgs = {}
    warn_msgs = {}
    files_seen = set()
    
    for entry in older:
        for line in entry.split("\n"):
            line = line.strip()
            if line.startswith("- **Block:**"):
                msg = line.replace("- **Block:**", "").strip()
                block_msgs[msg] = block_msgs.get(msg, 0) + 1
            elif line.startswith("- **Warn:**"):
                msg = line.replace("- **Warn:**", "").strip()
                warn_msgs[msg] = warn_msgs.get(msg, 0) + 1
            elif line.startswith("- **Files:**"):
                files = line.replace("- **Files:**", "").strip().split(", ")
                for f in files:
                    f = f.split("(+")[0].strip()  # Remove overflow marker
                    if f:
                        files_seen.add(f)
    
    # Build summary entry
    summary_lines = ["## Patterns (older sessions summarized)\n"]
    
    if block_msgs:
        summary_lines.append("**Blocks:**\n")
        for msg, count in sorted(block_msgs.items(), key=lambda x: -x[1]):
            summary_lines.append(f"- {msg} ({count}x)\n")
    
    if warn_msgs:
        summary_lines.append("**Warnings:**\n")
        for msg, count in sorted(warn_msgs.items(), key=lambda x: -x[1]):
            summary_lines.append(f"- {msg} ({count}x)\n")
    
    if files_seen:
        file_list = ", ".join(sorted(files_seen)[:5])
        if len(files_seen) > 5:
            file_list += f" (+{len(files_seen) - 5})"
        summary_lines.append(f"**Files touched:** {file_list}\n")
    
    summary_entry = "".join(summary_lines)
    
    return "\n---\n".join([header, summary_entry] + recent)


def auto_write_learnings(session_id: str) -> list:
    """Automatically generate concise learnings for activated skills.
    
    Tightness: Requires >= 1 meaningful event per skill. Stubs are rejected.
    Efficiency: Concise format, deduplicated, compressed to ~10-15 lines total.
    
    Returns list of skills that were successfully auto-written.
    """
    state = load_state_locked(session_id)
    activated = state.get("activated_skills", [])
    recorded = state.get("learnings_recorded", [])
    events = state.get("events", [])
    missing = [s for s in activated if s not in recorded]
    
    if not missing:
        return []
    
    auto_written = []
    home = Path.home()
    date_stamp = time.strftime("%Y-%m-%d")
    changed = state.get("changed_files", [])
    
    for skill_name in missing:
        # Filter events for this skill (or general events if untagged)
        skill_events = [e for e in events if e.get("skill") == skill_name or not e.get("skill")]
        
        # TIGHTNESS: Reject stub generation — require at least 1 meaningful event
        meaningful = [e for e in skill_events if e.get("type") in ("block", "warn")]
        if not meaningful:
            # No behavioral data captured — auto-generation FAILS
            continue
        
        blocks = [e for e in meaningful if e.get("type") == "block"]
        warnings = [e for e in meaningful if e.get("type") == "warn"]
        
        # Deduplication: skip if last entry has same fingerprint
        current_fingerprint = _hash_entry(skill_name, meaningful)
        skill_dir = home / ".kimi" / "skills" / skill_name
        learnings_path = skill_dir / "learnings.md"
        
        if learnings_path.exists():
            existing = learnings_path.read_text(encoding="utf-8")
            # Extract last entry's fingerprint roughly
            last_entries = existing.split("\n---\n")[-1:]
            if last_entries and current_fingerprint in last_entries[0]:
                # Duplicate of last entry — skip but mark as recorded
                if skill_name not in recorded:
                    recorded.append(skill_name)
                auto_written.append(skill_name)
                continue
        
        # Build concise entry (AI-optimized format)
        block_count = len(blocks)
        warn_count = len(warnings)
        
        lines = [
            f"\n---\n",
            f"## {date_stamp} | {skill_name} | B:{block_count} W:{warn_count}\n",
        ]
        
        # Collapse repeated patterns: show unique messages only
        unique_blocks = sorted(set(e.get("message", "") for e in blocks))
        unique_warns = sorted(set(e.get("message", "") for e in warnings))
        
        for msg in unique_blocks:
            lines.append(f"- **Block:** {msg}\n")
        for msg in unique_warns:
            lines.append(f"- **Warn:** {msg}\n")
        
        # Files (max 3, concise)
        if changed:
            file_list = ", ".join(changed[:3])
            if len(changed) > 3:
                file_list += f" (+{len(changed) - 3})"
            lines.append(f"- **Files:** {file_list}\n")
        
        entry = "".join(lines)
        
        try:
            skill_dir.mkdir(parents=True, exist_ok=True)
            if learnings_path.exists():
                existing = learnings_path.read_text(encoding="utf-8")
                combined = existing + entry
                # Compress: keep last 3 detailed + summary of older
                compressed = _compress_learnings(combined)
                learnings_path.write_text(compressed, encoding="utf-8")
            else:
                header = f"# Learnings: {skill_name}\n\n> Auto-captured. Review and expand.\n"
                learnings_path.write_text(header + entry, encoding="utf-8")
            
            if skill_name not in recorded:
                recorded.append(skill_name)
            auto_written.append(skill_name)
        except Exception:
            continue
    
    state["learnings_recorded"] = recorded
    save_state_locked(session_id, state)
    return auto_written


def track_production_write(session_id: str, filepath: str) -> None:
    """Record a production file write and check if E2E validation is now required.
    Idempotent: same file written twice only counts once."""
    if not is_production_file(filepath):
        return
    state = load_state_locked(session_id)
    if filepath not in state["changed_files"]:
        state["changed_files"].append(filepath)
        state["pending_writes"] += 1
    if state["pending_writes"] >= E2E_BUFFER:
        state["validation_required"] = True
    save_state_locked(session_id, state)


def record_test_run(session_id: str) -> None:
    """Clear E2E validation state after tests are run."""
    state = load_state_locked(session_id)
    state["pending_writes"] = 0
    state["changed_files"] = []
    state["last_test_run"] = time.time()
    state["validation_required"] = False
    save_state_locked(session_id, state)


def check_e2e_gate(session_id: str, context: str = "write") -> None:
    """Block if E2E validation is required and hasn't been performed."""
    state = load_state_locked(session_id)
    if not state.get("validation_required"):
        return
    files = state.get("changed_files", [])
    file_list = ", ".join(files[:5])
    if len(files) > 5:
        file_list += f" and {len(files) - 5} more"
    log_event(session_id, "block", f"E2E validation required: {state['pending_writes']} files pending", "")
    block(
        f"E2E VALIDATION REQUIRED before {context}. "
        f"{state['pending_writes']} production file(s) changed since last test run: {file_list}. "
        f"Run Playwright/pytest/jest/vitest E2E tests now."
    )


def check_git_gate(session_id: str, command: str) -> None:
    """Enhanced git block that includes E2E requirement when pending writes exist."""
    state = load_state_locked(session_id)
    pending = state.get("pending_writes", 0)
    if pending > 0:
        files = state.get("changed_files", [])
        file_list = ", ".join(files[:5])
        if len(files) > 5:
            file_list += f" and {len(files) - 5} more"
        log_event(session_id, "block", f"Git mutation blocked: {pending} untested files", "")
        block(
            f"Git mutation blocked: {pending} untested production file(s) pending E2E validation: {file_list}. "
            f"Run E2E tests first, then ask user for explicit confirmation before git operations."
        )
    else:
        log_event(session_id, "block", "Git mutation blocked without pending files", "")
        block("Git mutations are blocked. Ask user for explicit confirmation first.")


# ── Swarm Stage Tracking ──────────────────────────────────────────────────────

def _find_swarm_artifacts() -> list:
    """Scan artifact paths for swarm status markers. Returns list of completed stages."""
    completed = set()
    cwd = Path.cwd()
    for rel_path in SWARM_ARTIFACT_PATHS:
        artifact_dir = cwd / rel_path
        if not artifact_dir.exists():
            continue
        for filepath in artifact_dir.rglob("*"):
            if not filepath.is_file():
                continue
            # Only scan text files
            if filepath.suffix not in (".md", ".txt", ".json", ".jsonl", ""):
                continue
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                for marker, stage in SWARM_STATUS_MARKERS.items():
                    if marker in content:
                        completed.add(stage)
            except Exception:
                continue
    return list(completed)


def _is_swarm_required(state: dict) -> bool:
    """Determine if swarm stages are required for this session."""
    changed = state.get("changed_files", [])
    # Swarm required if more than 1 production file changed
    if len(changed) > 1:
        return True
    # Swarm required if any changed file touches sensitive areas
    for filepath in changed:
        for pattern in SWARM_SENSITIVE_PATTERNS:
            if pattern.search(filepath):
                return True
    return False


def update_swarm_state(session_id: str) -> None:
    """Scan for swarm artifacts and update state. Called after production writes."""
    state = load_state_locked(session_id)
    # Check if swarm is now required
    if not state.get("swarm_required", False):
        state["swarm_required"] = _is_swarm_required(state)
    # Scan for completed stages
    completed = _find_swarm_artifacts()
    existing = set(state.get("swarm_stages_completed", []))
    for stage in completed:
        if stage not in existing:
            existing.add(stage)
    state["swarm_stages_completed"] = list(existing)
    save_state_locked(session_id, state)


def check_swarm_gate(session_id: str) -> None:
    """Warn if swarm is required but stages are incomplete."""
    state = load_state_locked(session_id)
    if not state.get("swarm_required", False):
        return
    completed = set(state.get("swarm_stages_completed", []))
    # Minimum required stages: plan, test
    required = ["plan", "test"]
    missing = [s for s in required if s not in completed]
    if missing:
        stage_list = ", ".join(missing)
        log_event(session_id, "warn", f"Swarm stages missing: {stage_list}", "")
        warn(
            f"SWARM GOVERNANCE: Non-trivial changes require staged review. "
            f"Missing stages: {stage_list}. "
            f"Required markers: PLAN STATUS, TEST STATUS. "
            f"Write these markers to .kimi/plans/ or .kimi/sessions/ before ending session."
        )


# ── TDD Hard Gate State Machine ───────────────────────────────────────────────

def track_tdd_state(session_id: str, filepath: str) -> None:
    """Track test-first discipline. Updates TDD state based on file write order.
    
    State machine:
    - idle: No active TDD cycle
    - red:  Test file written, waiting for production code
    - green: Production code written after test, cycle complete
    """
    if not filepath:
        return
    
    state = load_state_locked(session_id)
    tdd_state = state.get("tdd_state", "idle")
    
    if is_test_file(filepath):
        # Test file written → enter RED phase (or reset if starting new cycle)
        is_new_test = filepath not in state.get("test_files_written", [])
        if is_new_test:
            state["test_files_written"] = state.get("test_files_written", []) + [filepath]
        if tdd_state == "idle" or (tdd_state == "green" and is_new_test):
            # Reset to red when a NEW test is written after green (new TDD cycle)
            # or when first test is written from idle
            state["tdd_state"] = "red"
        # If red and writing another test, stay red
        save_state_locked(session_id, state)
        return
    
    if is_production_file(filepath):
        # Production file written
        if filepath not in state.get("prod_files_written", []):
            state["prod_files_written"] = state.get("prod_files_written", []) + [filepath]
        if tdd_state == "red":
            # First production write after test → enter GREEN
            state["tdd_state"] = "green"
        # If already green, stay green (refactor phase)
        save_state_locked(session_id, state)
        return
    
    save_state_locked(session_id, state)


def check_tdd_gate(session_id: str, filepath: str) -> None:
    """BLOCK production writes that violate test-first discipline.
    
    For non-trivial changes (>1 prod file or swarm required or sensitive file):
    - First production write MUST be preceded by a test file write in this session
    - If no test written yet → BLOCK
    
    For trivial changes (single file, no swarm, non-sensitive):
    - WARN but do not block
    """
    if not filepath or not is_production_file(filepath):
        return
    
    state = load_state_locked(session_id)
    tdd_state = state.get("tdd_state", "idle")
    
    # Determine if this is non-trivial
    is_non_trivial = state.get("swarm_required", False)
    prod_count = len(state.get("prod_files_written", []))
    if prod_count >= 1:
        is_non_trivial = True
    # Single sensitive files are always non-trivial
    for pattern in SWARM_SENSITIVE_PATTERNS:
        if pattern.search(filepath):
            is_non_trivial = True
            break
    
    if tdd_state == "idle":
        # No test written yet in this session
        if is_non_trivial:
            block(
                f"TDD HARD GATE: Production code '{filepath}' written without a failing test first. "
                f"RED PHASE REQUIRED: Write a test file BEFORE production code. "
                f"Test files must contain '.test.', '.spec.', or be in a /test/ directory. "
                f"This is non-trivial work ({prod_count + 1} production file(s))."
            )
        else:
            warn(
                f"TDD WARNING: Production code written without a preceding test. "
                f"Consider writing a test first, even for small changes."
            )


def track_alignment_state(session_id: str) -> None:
    """Scan for alignment/grill-me artifacts and update state."""
    state = load_state_locked(session_id)
    if not state.get("alignment_artifact_found", False):
        state["alignment_artifact_found"] = _find_alignment_artifacts()
    # Alignment is "completed" if artifact found OR swarm plan stage is completed
    if state.get("alignment_artifact_found", False):
        state["alignment_completed"] = True
    else:
        # Also check if PLAN STATUS was found via swarm scanning
        completed = set(state.get("swarm_stages_completed", []))
        if "plan" in completed:
            state["alignment_completed"] = True
    save_state_locked(session_id, state)


def check_alignment_gate(session_id: str, filepath: str) -> None:
    """BLOCK production writes for non-trivial work without alignment.
    
    If swarm is required (non-trivial) and no alignment artifact exists,
    block the first production write. Sensitive single files are also non-trivial.
    """
    if not filepath or not is_production_file(filepath):
        return
    
    state = load_state_locked(session_id)
    is_non_trivial = state.get("swarm_required", False)
    prod_count = len(state.get("prod_files_written", []))
    if prod_count >= 1:
        is_non_trivial = True
    # Single sensitive files are always non-trivial
    for pattern in SWARM_SENSITIVE_PATTERNS:
        if pattern.search(filepath):
            is_non_trivial = True
            break
    
    if not is_non_trivial:
        return
    
    alignment_done = state.get("alignment_completed", False)
    if not alignment_done:
        log_event(session_id, "block", f"Alignment missing for {filepath}", "grill-me")
        block(
            f"ALIGNMENT HARD GATE: Non-trivial work requires alignment BEFORE coding. "
            f"Write an alignment artifact to .kimi/plans/ containing 'ALIGNMENT COMPLETE' or 'GRILL STATUS: PASS'. "
            f"Use /skill:grill-me to interview the user about requirements, scope, and acceptance criteria. "
            f"File attempted: {filepath}"
        )



# ── The 4 Principles — Hard Mechanical Gates ──────────────────────────────────

# Dependency files that trigger simplicity review when modified
DEPENDENCY_FILES = {
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "requirements.txt", "requirements-dev.txt", "Pipfile", "Pipfile.lock",
    "poetry.lock", "setup.py", "setup.cfg", "pyproject.toml",
    "Cargo.toml", "Cargo.lock", "Gemfile", "Gemfile.lock",
    "go.mod", "go.sum", "composer.json", "composer.lock",
    "build.gradle", "pom.xml", "CMakeLists.txt", "Makefile",
}


def _find_plan_artifacts() -> bool:
    """Scan for evidence of planning (any non-empty markdown in plans/sessions)."""
    cwd = Path.cwd()
    for rel_path in (".kimi/plans/", ".kimi/sessions/"):
        plan_dir = cwd / rel_path
        if not plan_dir.exists():
            continue
        for filepath in plan_dir.rglob("*.md"):
            if not filepath.is_file():
                continue
            try:
                text = filepath.read_text(encoding="utf-8", errors="ignore")
                if len(text.strip()) > 50:
                    return True
            except Exception:
                continue
    return False


def _has_scope_justification() -> bool:
    """Check if a scope justification exists in plan artifacts."""
    cwd = Path.cwd()
    for rel_path in (".kimi/plans/", ".kimi/sessions/"):
        plan_dir = cwd / rel_path
        if not plan_dir.exists():
            continue
        for filepath in plan_dir.rglob("*.md"):
            if not filepath.is_file():
                continue
            try:
                text = filepath.read_text(encoding="utf-8", errors="ignore")
                markers = ["SCOPE JUSTIFICATION", "SCOPE DECLARATION", "FILES TOUCHED", "CHANGE RATIONALE"]
                if any(m in text for m in markers):
                    return True
            except Exception:
                continue
    return False


def check_think_gate(session_id: str, filepath: str) -> None:
    """PRINCIPLE 1: Think Before Coding — Hard Gate.
    
    Blocks the FIRST production file write unless evidence of planning exists.
    Exemptions: test files (RED phase), files ≤10 lines, or existing plan artifacts.
    """
    if not filepath or not is_production_file(filepath):
        return
    
    state = load_state_locked(session_id)
    # Only gate the first production write
    if len(state.get("prod_files_written", [])) > 0:
        return
    if len(state.get("changed_files", [])) > 0:
        return
    
    # Exempt test files (TDD red phase is the plan)
    if is_test_file(filepath):
        return
    
    # Check for existing plan/alignment artifacts
    if state.get("alignment_completed", False):
        return
    if _find_plan_artifacts():
        return
    
    log_event(session_id, "block", "Think gate: first production write without planning", "")
    block(
        f"THINK HARD GATE (Principle 1): Production code '{filepath}' written without evidence of planning. "
        f"Before coding, you MUST either: "
        f"(1) Write a plan to .kimi/plans/ (50+ chars), "
        f"(2) Run /skill:grill-me to align on requirements, OR "
        f"(3) Write a test file first (RED phase). "
        f"State assumptions, present tradeoffs, and define acceptance criteria before implementation."
    )


def check_simplicity_gate(session_id: str, filepath: str, file_content: str) -> None:
    """PRINCIPLE 2: Simplicity First — Hard Gate.
    
    Warns on large file writes. Blocks dependency changes without justification.
    """
    if not filepath:
        return
    
    # Line count check
    if file_content:
        line_count = len(file_content.splitlines())
        if line_count > 200:
            log_event(session_id, "block", f"Simplicity gate: {filepath} exceeds 200 lines", "")
            block(
                f"SIMPLICITY HARD GATE (Principle 2): File '{filepath}' is {line_count} lines. "
                f"Maximum allowed is 200 lines per write. Break into smaller, focused units. "
                f"No speculative generality. No premature abstraction."
            )
        elif line_count > 100:
            log_event(session_id, "warn", f"Simplicity warning: {filepath} is {line_count} lines", "")
            warn(
                f"SIMPLICITY WARNING (Principle 2): File '{filepath}' is {line_count} lines. "
                f"Consider breaking into smaller units if it exceeds 150 lines."
            )
    
    # Dependency change check
    filename = Path(filepath).name
    if filename in DEPENDENCY_FILES:
        if not _has_scope_justification():
            log_event(session_id, "block", f"Simplicity gate: dependency file {filename} changed without justification", "")
            block(
                f"SIMPLICITY HARD GATE (Principle 2): Dependency file '{filename}' modified without justification. "
                f"Adding/removing dependencies requires a SCOPE JUSTIFICATION marker in .kimi/plans/. "
                f"Ask: 'Would a senior engineer say this dependency is necessary?'"
            )


def check_surgical_gate(session_id: str, filepath: str) -> None:
    """PRINCIPLE 3: Surgical Changes — Hard Gate.
    
    Warns at 4+ files modified. Blocks at 6+ files without scope justification.
    """
    if not filepath or not is_production_file(filepath):
        return
    
    state = load_state_locked(session_id)
    changed = state.get("changed_files", [])
    # Projected total including current write (changed_files is PostToolUse lagged)
    projected = len(changed) + 1
    
    if projected >= 6:
        if not _has_scope_justification():
            log_event(session_id, "block", f"Surgical gate: {projected} files modified without scope justification", "")
            block(
                f"SURGICAL HARD GATE (Principle 3): {projected} production files modified without scope justification. "
                f"Every changed line must trace directly to the user's request. "
                f"Write a SCOPE JUSTIFICATION to .kimi/plans/ explaining why each file is necessary. "
                f"Do NOT 'improve' adjacent code, comments, or formatting."
            )
    elif projected >= 4:
        log_event(session_id, "warn", f"Surgical warning: {projected} files modified", "")
        warn(
            f"SURGICAL WARNING (Principle 3): {projected} files modified. "
            f"Ensure each change traces directly to the request. Avoid scope creep."
        )

# ── Anti-Slop Gates ────────────────────────────────────────────────────────────


def _get_checkpoint_interval(state: dict) -> int:
    """Return adaptive checkpoint interval based on session conditions."""
    interval = state.get("checkpoint_interval", DEFAULT_CHECKPOINT_INTERVAL)
    if state.get("swarm_required"):
        return 12
    if state.get("pending_writes", 0) >= 5:
        return 10
    return interval


def _find_checkpoint_artifacts() -> bool:
    """Search for checkpoint artifacts in checkpoint directories."""
    for dirname in CHECKPOINT_DIRS:
        d = Path(dirname)
        if d.exists() and d.is_dir():
            for f in d.glob("*.md"):
                try:
                    text = f.read_text()
                    if CHECKPOINT_MARKER in text:
                        return True
                except Exception:
                    pass
    return False


def track_tool_use(session_id: str, tool_name: str, filepath: str = "") -> None:
    """Track tool usage for anti-slop gates.

    - Increments tool_use_count for all tools
    - Tracks consecutive_writes_without_read
    - Clears error_recovery_mode on read operations
    """
    state = load_state_locked(session_id)
    state["tool_use_count"] = state.get("tool_use_count", 0) + 1

    if tool_name in WRITE_TOOLS:
        state["consecutive_writes_without_read"] = state.get("consecutive_writes_without_read", 0) + 1
    elif tool_name in READ_TOOLS:
        state["consecutive_writes_without_read"] = 0
        # Clear error recovery on any read/diagnostic action
        if state.get("error_recovery_mode"):
            state["error_recovery_mode"] = False
            state["error_recovery_set_at"] = None
            state["last_error_brief"] = ""

    save_state_locked(session_id, state)


def set_error_recovery(session_id: str, error_brief: str) -> None:
    """Enter error recovery mode after a shell error."""
    state = load_state_locked(session_id)
    state["error_recovery_mode"] = True
    state["error_recovery_set_at"] = time.time()
    state["last_error_brief"] = error_brief
    save_state_locked(session_id, state)


def clear_error_recovery(session_id: str) -> None:
    """Explicitly clear error recovery mode."""
    state = load_state_locked(session_id)
    state["error_recovery_mode"] = False
    state["error_recovery_set_at"] = None
    state["last_error_brief"] = ""
    save_state_locked(session_id, state)


def check_cognitive_checkpoint_gate(session_id: str, filepath: str) -> None:
    """PRINCIPLE 5: Goal-Driven Execution — Cognitive Checkpoint Gate.

    Forces a stop-and-think checkpoint every N tool uses when there is
    pending work. The agent must write a checkpoint artifact before
    continuing.
    """
    if not filepath:
        return
    path_lower = filepath.lower()
    # Exempt session/plan files and test files
    if ".kimi/sessions/" in path_lower or ".kimi/plans/" in path_lower:
        return
    if is_test_file(filepath):
        return

    state = load_state_locked(session_id)
    tool_use_count = state.get("tool_use_count", 0)
    last_checkpoint = state.get("last_checkpoint_at", 0)
    pending = state.get("pending_writes", 0)
    interval = _get_checkpoint_interval(state)

    if pending == 0:
        return
    if tool_use_count - last_checkpoint < interval:
        return
    if _find_checkpoint_artifacts():
        # Artifact found — update last_checkpoint_at to current count
        state["last_checkpoint_at"] = tool_use_count
        save_state_locked(session_id, state)
        return

    log_event(
        session_id,
        "block",
        f"Cognitive checkpoint gate: {tool_use_count - last_checkpoint} tools since last checkpoint",
        "",
    )
    block(
        f"COGNITIVE CHECKPOINT GATE (Principle 5): {tool_use_count - last_checkpoint} tool uses "
        f"since last checkpoint (interval: {interval}). "
        f"You MUST stop and think before continuing. Write a checkpoint artifact to "
        f".kimi/sessions/ or .kimi/plans/ containing '{CHECKPOINT_MARKER}'. "
        f"Reflect on: (1) Are you still aligned with the goal? (2) What assumptions have changed? "
        f"(3) What is the next smallest step?"
    )


def check_error_recovery_gate(session_id: str, tool_name: str, filepath: str = "") -> None:
    """PRINCIPLE 5: Error Recovery Gate.

    After a Shell error, blocks WriteFile/StrReplaceFile until the agent
    performs a diagnostic read (ReadFile, Grep, Glob, Agent, Shell).
    """
    state = load_state_locked(session_id)
    if not state.get("error_recovery_mode"):
        return

    # Exempt session/plan files and test files
    if filepath:
        path_lower = filepath.lower()
        if ".kimi/sessions/" in path_lower or ".kimi/plans/" in path_lower:
            return
        for seg in EXCLUDED_PATH_SEGMENTS:
            if seg in path_lower:
                return

    # Allow read/diagnostic tools during recovery
    if tool_name in READ_TOOLS or tool_name in ("Agent",):
        return

    # Block writes during error recovery
    if tool_name in WRITE_TOOLS:
        log_event(
            session_id,
            "block",
            f"Error recovery gate: blocked {tool_name} during recovery ({state.get('last_error_brief', '')})",
            "",
        )
        block(
            f"ERROR RECOVERY GATE (Principle 5): A previous Shell command failed: "
            f"'{state.get('last_error_brief', 'unknown error')}'. "
            f"You MUST diagnose the failure BEFORE writing more code. Use ReadFile, Grep, "
            f"or Shell to investigate. Do NOT patch blindly."
        )


def check_blind_patch_gate(session_id: str, filepath: str) -> None:
    """PRINCIPLE 5: Blind Patch Gate.

    Warns at 2 consecutive writes without a read. Blocks at 3+.
    Prevents the agent from repeatedly guessing without looking.
    """
    if not filepath:
        return
    path_lower = filepath.lower()
    # Exempt session/plan files and test files
    if ".kimi/sessions/" in path_lower or ".kimi/plans/" in path_lower:
        return
    if is_test_file(filepath):
        return

    state = load_state_locked(session_id)
    count = state.get("consecutive_writes_without_read", 0)

    # Escalate to block if error recovery is active (even 2nd write is blocked)
    if state.get("error_recovery_mode") and count >= 1:
        log_event(
            session_id,
            "block",
            f"Blind patch gate: {count} consecutive writes + error recovery active",
            "",
        )
        block(
            f"BLIND PATCH GATE (Principle 5): {count} consecutive writes without reading. "
            f"Error recovery is ALSO active. You are patching blindly. STOP. "
            f"Use ReadFile or Grep to understand the current state before writing again."
        )
    elif count >= 2:
        log_event(
            session_id,
            "block",
            f"Blind patch gate: {count} consecutive writes without reading",
            "",
        )
        block(
            f"BLIND PATCH GATE (Principle 5): {count} consecutive writes without a read. "
            f"You are patching blindly. STOP and use ReadFile or Grep to understand "
            f"the current state before writing again."
        )
    elif count == 1:
        log_event(
            session_id,
            "warn",
            f"Blind patch warning: {count} consecutive writes without reading",
            "",
        )
        warn(
            f"BLIND PATCH WARNING (Principle 5): {count} consecutive writes without a read. "
            f"You may be patching blindly. Consider using ReadFile or Grep to verify "
            f"state before the next write."
        )


# ── Main ─────────────────────────────────────────────────────────────────────--


# ── UI/UX Hard Gates ──────────────────────────────────────────────────────────

FRONTEND_EXTENSIONS = {
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte",
    ".tpl", ".blade.php", ".twig",
}


def _is_frontend_file(filepath: str) -> bool:
    """Check if filepath is a frontend/UI file subject to UX gates."""
    if not filepath:
        return False
    path_lower = filepath.lower()
    for ext in FRONTEND_EXTENSIONS:
        if path_lower.endswith(ext):
            return True
    return False


def _has_img_without_alt(content: str) -> bool:
    """Check for <img> tags missing alt attribute."""
    pattern = re.compile(r'<img\b(?![^>]*\balt=)[^>]*>', re.IGNORECASE)
    return bool(pattern.search(content))


def _has_positive_tabindex(content: str) -> bool:
    """Check for positive tabindex values (anti-pattern)."""
    pattern = re.compile(r'tabindex=["\']?[1-9]["\']?', re.IGNORECASE)
    return bool(pattern.search(content))


def _has_user_scalable_no(content: str) -> bool:
    """Check for user-scalable=no in viewport meta."""
    pattern = re.compile(r'user-scalable\s*=\s*["\']?no["\']?', re.IGNORECASE)
    return bool(pattern.search(content))


def _has_maximum_scale_one(content: str) -> bool:
    """Check for maximum-scale=1.0 which prevents zoom."""
    pattern = re.compile(r'maximum-scale\s*=\s*["\']?1(?:\.0)?["\']?', re.IGNORECASE)
    return bool(pattern.search(content))


def _has_input_without_type(content: str) -> bool:
    """Check for <input> tags missing type attribute."""
    pattern = re.compile(r'<input\b(?![^>]*\btype=)[^>]*>', re.IGNORECASE)
    return bool(pattern.search(content))


def _has_outline_none(content: str) -> bool:
    """Check for outline:none or outline:0 without focus replacement."""
    pattern = re.compile(r'outline\s*:\s*none|outline\s*:\s*0\b', re.IGNORECASE)
    return bool(pattern.search(content))


def _has_html_without_lang(content: str) -> bool:
    """Check for <html> tag missing lang attribute."""
    pattern = re.compile(r'<html\b(?![^>]*\blang=)[^>]*>', re.IGNORECASE)
    return bool(pattern.search(content))


def _has_missing_viewport(content: str) -> bool:
    """Check for missing viewport meta tag in HTML files."""
    if '<meta' not in content.lower():
        return False
    pattern = re.compile(r'<meta\s+name=["\']viewport["\']', re.IGNORECASE)
    return not bool(pattern.search(content))


def _has_click_on_non_interactive(content: str) -> bool:
    """Heuristic: onClick handlers on div or span elements."""
    pattern = re.compile(r'onClick\s*=\s*["\'][^"\']*["\'][^>]*>(?![^<]*</(?:button|a|input|select|textarea))', re.IGNORECASE)
    return bool(pattern.search(content))


def _has_autoplay_without_muted(content: str) -> bool:
    """Check for autoplay video without muted attribute."""
    pattern = re.compile(r'<video\b[^>]*\bautoplay\b', re.IGNORECASE)
    for match in pattern.finditer(content):
        tag = match.group(0)
        if 'muted' not in tag.lower():
            return True
    return False


def check_ux_gate(session_id: str, filepath: str, content: str) -> None:
    """PRINCIPLE: UI/UX quality — Hard Gate for frontend files.
    
    Enforces accessibility, mobile, and interaction design standards
    on all frontend file writes.
    """
    if not filepath or not _is_frontend_file(filepath):
        return
    if not content:
        return
    
    # ── BLOCK patterns (severe accessibility violations) ──
    
    if _has_img_without_alt(content):
        log_event(session_id, "block", "UX: <img> without alt text", "ui-ux")
        block(
            "UX HARD GATE (Accessibility): <img> tag without alt text detected. "
            "All images MUST have meaningful alt text for screen readers. "
            "Principle: Perceivability (WCAG 2.2 AA)."
        )
    
    if _has_positive_tabindex(content):
        log_event(session_id, "block", "UX: positive tabindex", "ui-ux")
        block(
            "UX HARD GATE (Accessibility): Positive tabindex detected. "
            "tabindex > 0 breaks natural tab order and creates keyboard traps. "
            "Use source order or tabindex=\"0\" only. Principle: Operability."
        )
    
    if _has_user_scalable_no(content):
        log_event(session_id, "block", "UX: user-scalable=no", "ui-ux")
        block(
            "UX HARD GATE (Mobile Accessibility): user-scalable=no prevents zoom. "
            "Users with low vision MUST be able to zoom. "
            "Remove user-scalable=no and maximum-scale restrictions."
        )
    
    if _has_maximum_scale_one(content):
        log_event(session_id, "block", "UX: maximum-scale=1", "ui-ux")
        block(
            "UX HARD GATE (Mobile Accessibility): maximum-scale=1.0 prevents zoom. "
            "Users MUST be able to zoom to 200%+. "
            "Remove maximum-scale restrictions."
        )
    
    if _has_input_without_type(content):
        log_event(session_id, "block", "UX: <input> without type", "ui-ux")
        block(
            "UX HARD GATE (Mobile Forms): <input> without type attribute. "
            "Missing type prevents the correct mobile keyboard from appearing. "
            "Use type=\"email\", \"tel\", \"number\", \"search\", etc."
        )
    
    # ── WARN patterns (UX quality issues) ──
    
    if filepath.lower().endswith((".html", ".htm")):
        if _has_html_without_lang(content):
            log_event(session_id, "warn", "UX: <html> without lang attribute", "ui-ux")
            warn(
                "UX WARNING (Accessibility): <html> tag missing lang attribute. "
                "Add lang=\"en\" (or appropriate language) for correct screen reader pronunciation."
            )
        
        if _has_missing_viewport(content):
            log_event(session_id, "warn", "UX: missing viewport meta", "ui-ux")
            warn(
                "UX WARNING (Mobile): Missing viewport meta tag. "
                "Add: <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            )
    
    if _has_outline_none(content):
        log_event(session_id, "warn", "UX: outline:none detected", "ui-ux")
        warn(
            "UX WARNING (Accessibility): outline:none or outline:0 detected. "
            "Removing focus indicators makes keyboard navigation invisible. "
            "If you must remove default outline, replace it with a custom :focus-visible style."
        )
    
    if _has_click_on_non_interactive(content):
        log_event(session_id, "warn", "UX: onClick on non-interactive element", "ui-ux")
        warn(
            "UX WARNING (Interaction): onClick handler on a non-interactive element (div/span). "
            "Use <button> or <a> for clickable actions — they provide keyboard accessibility, "
            "focus management, and semantic meaning by default."
        )
    
    if _has_autoplay_without_muted(content):
        log_event(session_id, "warn", "UX: autoplay video without muted", "ui-ux")
        warn(
            "UX WARNING (Accessibility): <video autoplay> without muted attribute. "
            "Auto-playing audio violates WCAG and annoys users. "
            "Add muted if autoplay is required, or let users opt in."
        )


def main() -> None:
    if BYPASS:
        allow()

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        allow()

    event = data.get("hook_event_name", "")
    session_id = data.get("session_id", "")
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    tool_output = data.get("tool_output", "")

    if event == "PreToolUse":
        if tool_name in ("WriteFile", "StrReplaceFile"):
            filepath = tool_input.get("path", "")
            content = tool_input.get("content", "")
            if not content:
                edit = tool_input.get("edit", {})
                if isinstance(edit, list):
                    for e in edit:
                        validate_file_content(e.get("new", ""), filepath)
                elif isinstance(edit, dict):
                    validate_file_content(edit.get("new", ""), filepath)
            else:
                validate_file_content(content, filepath)

            # TDD HARD GATE: block production writes without failing test first
            check_tdd_gate(session_id, filepath)

            # ALIGNMENT HARD GATE: block non-trivial work without grill-me alignment
            check_alignment_gate(session_id, filepath)

            # THINK HARD GATE (Principle 1): no production code without planning
            check_think_gate(session_id, filepath)

            # SIMPLICITY HARD GATE (Principle 2): large writes + dependency changes
            check_simplicity_gate(session_id, filepath, content)

            # SURGICAL HARD GATE (Principle 3): scope creep detection
            check_surgical_gate(session_id, filepath)

            # UX HARD GATE: enforce accessibility and interaction design on frontend files
            check_ux_gate(session_id, filepath, content)

            # E2E gate: block further writes if validation is pending
            check_e2e_gate(session_id, context=f"writing {filepath or 'file'}")

            # COGNITIVE CHECKPOINT GATE (Principle 5): stop-and-think
            check_cognitive_checkpoint_gate(session_id, filepath)

            # ERROR RECOVERY GATE (Principle 5): block writes after shell errors
            check_error_recovery_gate(session_id, tool_name, filepath)

            # BLIND PATCH GATE (Principle 5): warn/block consecutive writes without read
            check_blind_patch_gate(session_id, filepath)

        elif tool_name == "Shell":
            command = tool_input.get("command", "")
            validate_shell_command(command)

            # Track skill activations for Learnings Loop
            track_skill_activation(session_id, command)

            # E2E gate: enhanced git block
            if is_git_mutation(command):
                check_git_gate(session_id, command)

            # Record test runs to clear E2E state
            if is_test_command(command):
                record_test_run(session_id)

        # Track tool usage for anti-slop gates (all tools)
        track_tool_use(session_id, tool_name, tool_input.get("path", ""))

        allow()

    elif event == "PostToolUse":
        validate_post_tool(tool_name, tool_input, tool_output)

        # Track production file writes after successful execution
        if tool_name in ("WriteFile", "StrReplaceFile"):
            filepath = tool_input.get("path", "")
            track_production_write(session_id, filepath)
            track_learnings_write(session_id, filepath)
            # Update swarm artifact detection after writes
            update_swarm_state(session_id)
            # TDD state machine: track test-first discipline
            track_tdd_state(session_id, filepath)
            # Alignment state: scan for grill-me artifacts
            track_alignment_state(session_id)
            if is_production_file(filepath):
                warn(
                    f"Production file {filepath} modified. "
                    f"Run E2E tests after completing related changes."
                )

        # Detect shell errors and enter error recovery mode
        if tool_name == "Shell":
            output = str(tool_output) if tool_output else ""
            for pattern in ERROR_RECOVERY_INDICATORS:
                if re.search(pattern, output):
                    # Extract a brief error message (first line matching or first 80 chars)
                    lines = output.splitlines()
                    brief = lines[0] if lines else output
                    if len(brief) > 80:
                        brief = brief[:80] + "..."
                    set_error_recovery(session_id, brief)
                    break

        allow()

    elif event == "SessionEnd":
        # Learnings Loop: warn if skills were used without learnings
        check_learnings_gate(session_id)
        # Swarm governance: warn if non-trivial changes lack stage artifacts
        check_swarm_gate(session_id)
        # NOTE: State cleanup is handled by check-complete.sh to avoid race
        allow()

    else:
        allow()


if __name__ == "__main__":
    main()
