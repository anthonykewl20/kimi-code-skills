#!/bin/bash
# protect-env.sh
# PreToolUse hook for Kimi Code — blocks writes to .env files
# Place at: ~/.kimi/hooks/protect-env.sh
# Make executable: chmod +x ~/.kimi/hooks/protect-env.sh

set -euo pipefail

# Emergency bypass
if [ "${KIMI_GATEKEEPER_BYPASS:-}" = "1" ] || [ "${KIMI_GATEKEEPER_BYPASS:-}" = "true" ]; then
    exit 0
fi

INPUT=$(cat)

# Extract tool name and file path
if command -v jq &> /dev/null; then
    TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
    # CORRECTED: Kimi CLI uses 'path' not 'file_path' for WriteFile/StrReplaceFile
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.path // empty')
else
    TOOL_NAME=$(echo "$INPUT" | grep -o '"tool_name"[^,]*' | head -1 | cut -d'"' -f4)
    FILE_PATH=$(echo "$INPUT" | grep -o '"path"[^,]*' | head -1 | sed 's/.*"path":"\([^"]*\)".*/\1/')
fi

# Only check WriteFile and StrReplaceFile tools
if [ "$TOOL_NAME" != "WriteFile" ] && [ "$TOOL_NAME" != "StrReplaceFile" ]; then
    exit 0
fi

# Check if file path matches .env pattern
if echo "$FILE_PATH" | grep -qE '\.env(\.|$)'; then
    echo "⚠️  WARNING: Writing to '$FILE_PATH' is discouraged." >&2
    echo "   Environment files may contain secrets." >&2
    echo "   If you must edit this file, use a manual editor instead." >&2
    echo "" >&2
    echo "   Safe alternatives:" >&2
    echo "   - Add new env vars to .env.example (template, no secrets)" >&2
    echo "   - Use a secrets manager (AWS Secrets Manager, 1Password, etc.)" >&2
    echo "   - Edit .env manually with a text editor" >&2
    exit 2
fi

exit 0
