#!/bin/bash
# install.sh
# One-command installer for Kimi Code Skills
# Usage: ./install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Kimi Code Skills Installer${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Detect OS
OS="$(uname -s)"
case "$OS" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=Mac;;
    CYGWIN*)    PLATFORM=Cygwin;;
    MINGW*)     PLATFORM=MinGw;;
    *)          PLATFORM="UNKNOWN:$OS";;
esac

echo -e "${BLUE}Detected platform: $PLATFORM${NC}"

# Detect Kimi Code installation
KIMI_DIR=""

# Check for Kimi Code CLI
if command -v kimi &> /dev/null; then
    echo -e "${GREEN}✓ Kimi Code CLI found${NC}"

    # Try to find config directory
    if [ -d "$HOME/.kimi" ]; then
        KIMI_DIR="$HOME/.kimi"
    elif [ -d "$HOME/.config/kimi" ]; then
        KIMI_DIR="$HOME/.config/kimi"
    elif [ -d "$HOME/Library/Application Support/kimi" ]; then
        KIMI_DIR="$HOME/Library/Application Support/kimi"
    fi
else
    echo -e "${YELLOW}⚠ Kimi Code CLI not found in PATH${NC}"
    echo "   Please install Kimi Code first: https://kimi.moonshot.cn"
    echo "   Continuing with manual directory setup..."
fi

# Fallback to standard directories
if [ -z "$KIMI_DIR" ]; then
    if [ "$PLATFORM" = "Mac" ]; then
        KIMI_DIR="$HOME/Library/Application Support/kimi"
    elif [ "$PLATFORM" = "Linux" ]; then
        KIMI_DIR="$HOME/.config/kimi"
    else
        KIMI_DIR="$HOME/.kimi"
    fi
fi

echo -e "${BLUE}Installing to: $KIMI_DIR${NC}"

# Create directories
echo ""
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p "$KIMI_DIR/skills"
mkdir -p "$KIMI_DIR/hooks"
mkdir -p "$KIMI_DIR/flows"

echo -e "${GREEN}✓ ~/.kimi/skills/${NC}"
echo -e "${GREEN}✓ ~/.kimi/hooks/${NC}"
echo -e "${GREEN}✓ ~/.kimi/flows/${NC}"

# Install skills
echo ""
echo -e "${BLUE}Installing skills...${NC}"

SKILL_COUNT=0
for skill_dir in "$SCRIPT_DIR"/skills/*/; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        target_dir="$KIMI_DIR/skills/$skill_name"

        # Remove old version if exists
        if [ -d "$target_dir" ]; then
            rm -rf "$target_dir"
        fi

        # Copy new version
        cp -r "$skill_dir" "$target_dir"

        echo -e "${GREEN}  ✓ $skill_name${NC}"
        ((SKILL_COUNT++)) || true
    fi
done

echo -e "${GREEN}✓ Installed $SKILL_COUNT skills${NC}"

# Install hooks
echo ""
echo -e "${BLUE}Installing hooks...${NC}"

HOOK_COUNT=0
for hook_file in "$SCRIPT_DIR"/hooks/*.sh; do
    if [ -f "$hook_file" ]; then
        hook_name=$(basename "$hook_file")
        target_file="$KIMI_DIR/hooks/$hook_name"

        cp "$hook_file" "$target_file"
        chmod +x "$target_file"

        echo -e "${GREEN}  ✓ $hook_name${NC}"
        ((HOOK_COUNT++)) || true
    fi
done

echo -e "${GREEN}✓ Installed $HOOK_COUNT hooks${NC}"

# Configure config.toml
echo ""
echo -e "${BLUE}Configuring hooks in config.toml...${NC}"

CONFIG_FILE="$KIMI_DIR/config.toml"

# Create config if it doesn't exist
if [ ! -f "$CONFIG_FILE" ]; then
    touch "$CONFIG_FILE"
fi

# Check if our hooks are already configured
if ! grep -q "KIMI CODE SKILLS — HOOKS" "$CONFIG_FILE" 2>/dev/null; then
    cat >> "$CONFIG_FILE" << 'EOF'

# ============================================
# KIMI CODE SKILLS — HOOKS CONFIGURATION
# ============================================
# Auto-installed by kimi-code-skills installer
# Edit with caution — these hooks protect your codebase

# Auto-format after file edits
[[hooks]]
event = "PostToolUse"
matcher = "WriteFile|StrReplaceFile"
command = "jq -r '.tool_input.file_path' | xargs -I {} sh -c 'if command -v prettier >/dev/null 2>&1; then prettier --write \"{}\" 2>/dev/null; fi'"
timeout = 30

# Block dangerous git commands
[[hooks]]
event = "PreToolUse"
matcher = "Shell"
command = "~/.kimi/hooks/block-dangerous-git.sh"
timeout = 10

# Block edits to .env files
[[hooks]]
event = "PreToolUse"
matcher = "WriteFile|StrReplaceFile"
command = "~/.kimi/hooks/protect-env.sh"
timeout = 10

# Desktop notification when approval needed (macOS)
[[hooks]]
event = "Notification"
matcher = "permission_prompt"
command = "osascript -e 'display notification \"Kimi needs your approval\" with title \"Kimi CLI\"' 2>/dev/null || true"

# Verify tasks complete before stopping
[[hooks]]
event = "Stop"
command = "~/.kimi/hooks/check-complete.sh"
timeout = 30
EOF
    echo -e "${GREEN}✓ Hooks configured in config.toml${NC}"
else
    echo -e "${YELLOW}⚠ Hooks already configured in config.toml (skipping)${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Installed skills:${NC}"
ls -1 "$KIMI_DIR/skills/" | sed 's/^/  • /'
echo ""
echo -e "${BLUE}Installed hooks:${NC}"
ls -1 "$KIMI_DIR/hooks/" | sed 's/^/  • /'
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Add AGENTS.md to your project root:"
echo "     cp $SCRIPT_DIR/AGENTS.md ./AGENTS.md"
echo ""
echo "  2. Start Kimi Code in your project:"
echo "     cd your-project"
echo "     kimi"
echo ""
echo "  3. Run setup skill:"
echo "     /skill:setup-kimi-skills"
echo ""
echo "  4. Start building with discipline:"
echo "     /skill:grill-with-docs"
echo "     /skill:tdd"
echo ""
echo -e "${YELLOW}Note: If Kimi Code doesn't discover skills, try:${NC}"
echo -e "${YELLOW}  kimi --skills-dir $KIMI_DIR/skills${NC}"
echo ""
