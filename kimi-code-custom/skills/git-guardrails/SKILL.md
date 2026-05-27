---
name: git-guardrails
description: Set up Kimi Code hooks to block dangerous git commands (push, reset --hard, clean, etc.) before they execute. Runtime safety net.
---

# /git-guardrails — Dangerous Command Blocker

> "With great power comes great responsibility." — But AI agents don't have responsibility, so we add guardrails.

## When to Use

- Once per machine (global setup)
- When working on production codebases
- When multiple agents share a repository
- When you want to prevent "oops, I pushed to main" moments

## What This Skill Does

1. Creates a `PreToolUse` hook script at `~/.kimi/hooks/block-dangerous-git.sh`
2. Configures `~/.kimi/config.toml` to run the hook before every `Shell` tool call
3. The hook intercepts dangerous git commands and blocks them
4. Kimi receives the block message and adapts its plan

## Dangerous Commands Blocked

| Command | Why It's Blocked | Safe Alternative |
|---|---|---|
| `git push origin main` | Direct push to protected branch | Create PR from feature branch |
| `git push origin master` | Direct push to protected branch | Create PR from feature branch |
| `git push --force` | Overwrites remote history | Use `git push --force-with-lease` or PR |
| `git push -f` | Same as --force | Same as above |
| `git reset --hard` | Destroys uncommitted work | Use `git reset --soft` or stash first |
| `git clean -f` | Deletes untracked files permanently | Review files manually, then `git clean -i` |
| `git clean -fd` | Deletes untracked files AND directories | Same as above |
| `git branch -D main` | Deletes protected branch | Don't delete main |
| `git checkout -B main` | Forces branch recreation | Use regular checkout |

## How the Hook Works

### Hook Script (`~/.kimi/hooks/block-dangerous-git.sh`)

The hook receives JSON via stdin from Kimi's `PreToolUse` event:

```json
{
  "tool_name": "Shell",
  "tool_input": {
    "command": "git push origin main",
    "description": "Push changes to remote"
  }
}
```

The script:
1. Parses the JSON
2. Checks if `tool_name` is "Shell"
3. Extracts the command string
4. Matches against blocklist regex patterns
5. If blocked, prints a message to stderr and exits with code 2
6. If allowed, exits with code 0 (success)

### Kimi Behavior on Block

When the hook exits with code 2, Kimi receives the stderr output and:
1. Stops the current plan execution
2. Displays the block message to the user
3. Asks for confirmation or suggests an alternative
4. Never executes the dangerous command

## Installation

### Step 1: Create Hook Directory

```bash
mkdir -p ~/.kimi/hooks
chmod 755 ~/.kimi/hooks
```

### Step 2: Create the Hook Script

Save `~/.kimi/hooks/block-dangerous-git.sh`:

```bash
#!/bin/bash
# block-dangerous-git.sh
# PreToolUse hook for Kimi Code — blocks dangerous git commands

set -euo pipefail

# Read JSON from stdin
INPUT=$(cat)

# Extract tool name and command
TOOL_NAME=$(echo "$INPUT" | grep -o '"tool_name"[^,]*' | cut -d'"' -f4)
COMMAND=$(echo "$INPUT" | grep -o '"command"[^}]*' | sed 's/.*"command":"\([^"]*\)".*//')

# If not Shell tool, allow
if [ "$TOOL_NAME" != "Shell" ]; then
    exit 0
fi

# Blocklist patterns (regex)
BLOCKED_PATTERNS=(
    'git push .*main'
    'git push .*master'
    'git push .*--force'
    'git push .*-f '
    'git reset .*--hard'
    'git clean .*-f'
    'git branch .*-D .*main'
    'git checkout .*-B .*main'
)

# Check each pattern
for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        echo "❌ BLOCKED: '$COMMAND' is not allowed." >&2
        echo "   This command could damage the repository or overwrite history." >&2
        echo "" >&2
        echo "   Safe alternatives:" >&2
        echo "   - Instead of 'git push origin main', create a feature branch and open a PR." >&2
        echo "   - Instead of 'git reset --hard', use 'git reset --soft' or stash first." >&2
        echo "   - Instead of 'git clean -f', use 'git clean -i' (interactive) or review files." >&2
        exit 2
    fi
done

# Command is safe
exit 0
```

Make it executable:
```bash
chmod +x ~/.kimi/hooks/block-dangerous-git.sh
```

### Step 3: Configure Kimi

Add to `~/.kimi/config.toml`:

```toml
[[hooks]]
event = "PreToolUse"
matcher = "Shell"
command = "~/.kimi/hooks/block-dangerous-git.sh"
timeout = 10
```

### Step 4: Test the Hook

```bash
# Test 1: Should BLOCK
echo '{"tool_name":"Shell","tool_input":{"command":"git push origin main"}}' | ~/.kimi/hooks/block-dangerous-git.sh
echo "Exit code: $?"  # Should be 2

# Test 2: Should ALLOW
echo '{"tool_name":"Shell","tool_input":{"command":"git status"}}' | ~/.kimi/hooks/block-dangerous-git.sh
echo "Exit code: $?"  # Should be 0

# Test 3: Should ALLOW (not Shell tool)
echo '{"tool_name":"WriteFile","tool_input":{"file_path":"test.txt"}}' | ~/.kimi/hooks/block-dangerous-git.sh
echo "Exit code: $?"  # Should be 0
```

## Customization

### Add More Blocked Patterns

Edit the `BLOCKED_PATTERNS` array in the hook script:

```bash
# Add your team's protected branches
'git push .*production'
'git push .*release/'

# Add destructive operations specific to your stack
'npm run db:drop'
'terraform destroy'
```

### Whitelist Specific Commands

Add a whitelist section before the blocklist check:

```bash
# Whitelist: always allow these exact commands
WHITELIST=(
    'git push origin main --dry-run'
    'git push origin main --no-verify'
)

for safe in "${WHITELIST[@]}"; do
    if [ "$COMMAND" = "$safe" ]; then
        exit 0
    fi
done
```

### Per-Project Overrides

Some projects may have different protected branches. Create per-project hooks:

```bash
# .kimi/hooks/block-dangerous-git.sh (project-level)
# This overrides the global hook for this project only
```

## Success Criteria

This skill succeeded if:
- `git push origin main` is blocked in a test
- `git status` is allowed in a test
- The hook runs within 10 seconds (timeout configured)
- Kimi adapts its plan when a command is blocked (suggests PR instead)
