#!/bin/bash
# check-complete.sh
# Stop hook for Kimi Code — verifies task completion before ending session
# Place at: ~/.kimi/hooks/check-complete.sh
# Make executable: chmod +x ~/.kimi/hooks/check-complete.sh

set -euo pipefail

INPUT=$(cat)

# Extract session state
if command -v jq &> /dev/null; then
    SESSION_STATE=$(echo "$INPUT" | jq -r '.session_state // empty')
else
    SESSION_STATE=$(echo "$INPUT" | grep -o '"session_state"[^,]*' | head -1 | cut -d'"' -f4)
fi

# Check for uncommitted changes
if git rev-parse --git-dir > /dev/null 2>&1; then
    UNCOMMITTED=$(git status --short)
    if [ -n "$UNCOMMITTED" ]; then
        echo "⚠️  You have uncommitted changes:" >&2
        echo "$UNCOMMITTED" >&2
        echo "" >&2
        echo "Consider committing before ending the session:" >&2
        echo "  git add ." >&2
        echo "  git commit -m 'WIP: [description]'" >&2
    fi
fi

# Check for failing tests (if test script exists)
if [ -f "package.json" ] && grep -q '"test"' package.json; then
    if command -v npm &> /dev/null; then
        echo "Running tests before session end..." >&2
        npm test 2>&1 | tail -5 >&2
    fi
fi

exit 0
