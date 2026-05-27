# Kimi Code Skills — Quick Reference Card

## Installation
```bash
git clone <repo-url> kimi-code-skills
cd kimi-code-skills
./install.sh
```

## Per-Project Setup
```bash
cd your-project
cp /path/to/kimi-code-skills/AGENTS.md ./AGENTS.md
kimi
/skill:setup-kimi-skills
```

## Daily Workflow Commands

| When | Command | What It Does |
|---|---|---|
| Starting a feature | `/skill:grill-with-docs` | Align + build domain language |
| After alignment | `/skill:to-prd` | Write PRD as GitHub issue |
| After PRD | `/skill:to-issues` | Break into vertical slices |
| Implementing | `/skill:tdd` | Red-green-refactor discipline |
| Bug appears | `/skill:diagnose` | Reproduce → minimize → fix |
| Code review | `/skill:zoom-out` | Understand module context |
| Long session | `/skill:caveman` | Compress communication |
| Switching agents | `/skill:handoff` | Compact for next agent |
| Weekly maintenance | `/skill:improve-codebase-architecture` | Rescue entropy |
| Planning sprint | `/skill:triage` | Organize and prioritize issues |
| Design uncertainty | `/skill:prototype` | Test approaches before committing |

## Hooks (Auto-Active)

| Hook | Triggers On | Protection |
|---|---|---|
| `block-dangerous-git.sh` | `git push main`, `git reset --hard`, etc. | Blocks destructive git commands |
| `protect-env.sh` | Writing to `.env` files | Warns about secret exposure |
| `check-complete.sh` | Session end | Reminds about uncommitted changes |

## File Locations

| File | Path | Purpose |
|---|---|---|
| Global skills | `~/.kimi/skills/` | All installed skills |
| Project skills | `.kimi/skills/` | Project-specific overrides |
| Hooks | `~/.kimi/hooks/` | Safety scripts |
| Config | `~/.kimi/config.toml` | Hook registrations |
| Behavioral guidelines | `AGENTS.md` (project root) | Karpathy principles |
| Domain language | `CONTEXT.md` (project root) | Ubiquitous language |
| Decisions | `docs/adr/` | Architecture Decision Records |

## Troubleshooting

```bash
# List discovered skills
kimi /skill:list

# Test a hook manually
echo '{"tool_name":"Shell","tool_input":{"command":"git push origin main"}}' | ~/.kimi/hooks/block-dangerous-git.sh

# Check config loaded
kimi /hooks

# Force skills directory
kimi --skills-dir ~/.kimi/skills
```