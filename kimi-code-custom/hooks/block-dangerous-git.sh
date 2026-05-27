#!/bin/bash
# block-dangerous-git.sh
# PreToolUse hook for Kimi Code — blocks dangerous git commands
# Place at: ~/.kimi/hooks/block-dangerous-git.sh
# Make executable: chmod +x ~/.kimi/hooks/block-dangerous-git.sh

set -euo pipefail

# Read JSON from stdin
INPUT=$(cat)

# Extract tool name and command using jq if available, fallback to grep/sed
if command -v jq &> /dev/null; then
    TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
    COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
else
    TOOL_NAME=$(echo "$INPUT" | grep -o '"tool_name"[^,]*' | head -1 | cut -d'"' -f4)
    COMMAND=$(echo "$INPUT" | grep -o '"command"[^}]*' | head -1 | sed 's/.*"command":"\([^"]*\)".*/\1/')
fi

# If not Shell tool, allow
if [ "$TOOL_NAME" != "Shell" ]; then
    exit 0
fi

# If no command found, allow
if [ -z "$COMMAND" ]; then
    exit 0
fi

# Blocklist patterns (regex)
BLOCKED_PATTERNS=(
    'git push .*main\b'
    'git push .*master\b'
    'git push .*--force'
    'git push .*-f '
    'git reset .*--hard'
    'git clean .*-f'
    'git branch .*-D .*main\b'
    'git checkout .*-B .*main\b'
    'git push .*production\b'
    'git push .*release/'
)

# Check each pattern
for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        echo "❌ BLOCKED: '$COMMAND' is not allowed." >&2
        echo "   This command could damage the repository or overwrite history." >&2
        echo "" >&2
        echo "   Safe alternatives:" >&2
        echo "   - Instead of 'git push origin main', create a feature branch:" >&2
        echo "     git checkout -b feature/my-change" >&2
        echo "     git push origin feature/my-change" >&2
        echo "     Then open a Pull Request." >&2
        echo "" >&2
        echo "   - Instead of 'git reset --hard', use:" >&2
        echo "     git reset --soft HEAD~1  (keep changes in working tree)" >&2
        echo "     git stash push -m 'wip'  (save changes for later)" >&2
        echo "" >&2
        echo "   - Instead of 'git clean -f', use:" >&2
        echo "     git clean -i  (interactive, asks before each deletion)" >&2
        echo "     git clean -n  (dry-run, shows what would be deleted)" >&2
        exit 2
    fi
done

# Command is safe
exit 0
