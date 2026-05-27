#!/bin/bash
# check-complete.sh
# Stop hook for Kimi Code — verifies task completion before ending session

set -euo pipefail

# Emergency bypass
if [ "${KIMI_GATEKEEPER_BYPASS:-}" = "1" ] || [ "${KIMI_GATEKEEPER_BYPASS:-}" = "true" ]; then
    exit 0
fi

INPUT=$(cat)

# Extract session ID
SESSION_ID=""
if command -v jq &> /dev/null; then
    SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
fi

# ── Learnings Loop Hard Gate (with auto-generation) ───────────────────────────
if [ -n "$SESSION_ID" ]; then
    STATE_FILE_OLD="/tmp/kimi_gatekeeper_${SESSION_ID}.json"
    STATE_FILE_NEW="${HOME}/.kimi/.gatekeeper/kimi_gatekeeper_${SESSION_ID}.json"
    if [ -f "$STATE_FILE_NEW" ]; then
        STATE_FILE="$STATE_FILE_NEW"
    else
        STATE_FILE="$STATE_FILE_OLD"
    fi
    if [ -f "$STATE_FILE" ] && command -v jq &> /dev/null; then
        # Attempt auto-generation of learnings via gatekeeper.py
        if command -v python3 &> /dev/null; then
            HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
            AUTO_WRITTEN=$(cd "$HOOK_DIR" && python3 -c "
import sys, json
sys.path.insert(0, '.')
import gatekeeper as gk
sid = '$SESSION_ID'
auto = gk.auto_write_learnings(sid)
print(', '.join(auto))
" 2>/dev/null || echo "")
            if [ -n "$AUTO_WRITTEN" ]; then
                echo "📝 AUTO-LEARNINGS: Generated learnings for $AUTO_WRITTEN" >&2
                echo "   Review and expand at ~/.kimi/skills/[skill]/learnings.md" >&2
            fi
        fi

        # CORRECTED: Use set difference (.activated_skills - .learnings_recorded)
        MISSING=$(jq -r '(.activated_skills // []) - (.learnings_recorded // []) | join(", ")' "$STATE_FILE" 2>/dev/null || echo "")

        if [ -n "$MISSING" ]; then
            ACTIVATED=$(jq -r '(.activated_skills // []) | join(", ")' "$STATE_FILE")
            RECORDED=$(jq -r '(.learnings_recorded // []) | join(", ")' "$STATE_FILE")
            EVENT_COUNT=$(jq -r '(.events // []) | length' "$STATE_FILE" 2>/dev/null || echo "0")
            echo "🔒 LEARNINGS HARD GATE — Session cannot end." >&2
            echo "   Skills activated: $ACTIVATED" >&2
            echo "   Learnings recorded: ${RECORDED:-(none)}" >&2
            echo "   MISSING learnings for: $MISSING" >&2
            echo "   Events captured: $EVENT_COUNT" >&2
            echo "" >&2
            if [ "$EVENT_COUNT" -eq 0 ]; then
                echo "   Auto-generation FAILED: Zero gate events (blocks/warnings) captured." >&2
                echo "   The agent did not trigger any workflow gates during this session." >&2
                echo "   Either go through the gates (TDD, alignment, etc.) OR write" >&2
                echo "   substantive learnings manually with specific mistakes and fixes." >&2
            else
                echo "   Auto-generation failed. You MUST manually write learnings to:" >&2
                echo "   ~/.kimi/skills/[skill]/learnings.md" >&2
            fi
            echo "" >&2
            echo "   To bypass in emergencies: export KIMI_GATEKEEPER_BYPASS=1" >&2
            exit 2
        else
            ACTIVATED=$(jq -r '(.activated_skills // []) | join(", ")' "$STATE_FILE")
            if [ -n "$ACTIVATED" ]; then
                echo "✅ Learnings Loop: All activated skills have recorded learnings." >&2
            fi
        fi
    fi
fi

# ── Swarm Governance Check ────────────────────────────────────────────────────
if [ -n "$SESSION_ID" ]; then
    STATE_FILE_OLD="/tmp/kimi_gatekeeper_${SESSION_ID}.json"
    STATE_FILE_NEW="${HOME}/.kimi/.gatekeeper/kimi_gatekeeper_${SESSION_ID}.json"
    if [ -f "$STATE_FILE_NEW" ]; then
        STATE_FILE="$STATE_FILE_NEW"
    else
        STATE_FILE="$STATE_FILE_OLD"
    fi
    if [ -f "$STATE_FILE" ] && command -v jq &> /dev/null; then
        SWARM_REQUIRED=$(jq -r '.swarm_required // false' "$STATE_FILE" 2>/dev/null || echo "false")
        if [ "$SWARM_REQUIRED" = "true" ]; then
            COMPLETED=$(jq -r '(.swarm_stages_completed // []) | join(", ")' "$STATE_FILE" 2>/dev/null || echo "")
            # Check for minimum required stages: plan, test
            HAS_PLAN=$(echo "$COMPLETED" | grep -o "plan" || echo "")
            HAS_TEST=$(echo "$COMPLETED" | grep -o "test" || echo "")
            if [ -z "$HAS_PLAN" ] || [ -z "$HAS_TEST" ]; then
                echo "🔒 SWARM GOVERNANCE GATE — Session cannot end." >&2
                echo "   Non-trivial changes require staged review artifacts." >&2
                echo "   Completed stages: ${COMPLETED:-(none)}" >&2
                echo "   MISSING: PLAN STATUS and/or TEST STATUS markers." >&2
                echo "" >&2
                echo "   Write these markers to .kimi/plans/ or .kimi/sessions/:" >&2
                echo "   - PLAN STATUS (from board-lead-planner stage)" >&2
                echo "   - TEST STATUS (from board-test-specialist stage)" >&2
                echo "" >&2
                echo "   To bypass in emergencies: export KIMI_GATEKEEPER_BYPASS=1" >&2
                exit 2
            else
                echo "✅ Swarm Governance: All required stages completed." >&2
            fi
        fi
    fi
fi

# ── TDD Hard Gate Check ───────────────────────────────────────────────────────
if [ -n "$SESSION_ID" ]; then
    STATE_FILE_OLD="/tmp/kimi_gatekeeper_${SESSION_ID}.json"
    STATE_FILE_NEW="${HOME}/.kimi/.gatekeeper/kimi_gatekeeper_${SESSION_ID}.json"
    if [ -f "$STATE_FILE_NEW" ]; then
        STATE_FILE="$STATE_FILE_NEW"
    else
        STATE_FILE="$STATE_FILE_OLD"
    fi
    if [ -f "$STATE_FILE" ] && command -v jq &> /dev/null; then
        TDD_STATE=$(jq -r '.tdd_state // "idle"' "$STATE_FILE" 2>/dev/null || echo "idle")
        SWARM_REQUIRED=$(jq -r '.swarm_required // false' "$STATE_FILE" 2>/dev/null || echo "false")
        PROD_COUNT=$(jq -r '(.prod_files_written // []) | length' "$STATE_FILE" 2>/dev/null || echo "0")
        TEST_COUNT=$(jq -r '(.test_files_written // []) | length' "$STATE_FILE" 2>/dev/null || echo "0")
        
        if [ "$SWARM_REQUIRED" = "true" ] || [ "$PROD_COUNT" -gt 0 ]; then
            if [ "$TDD_STATE" = "idle" ] && [ "$TEST_COUNT" -eq 0 ]; then
                echo "🔒 TDD HARD GATE — Session cannot end." >&2
                echo "   Production code was written without a failing test first." >&2
                echo "   Files changed: $PROD_COUNT production, $TEST_COUNT test" >&2
                echo "" >&2
                echo "   RED PHASE REQUIRED: Every production file must be preceded by a test file." >&2
                echo "   Write a test containing '.test.', '.spec.', or in a /test/ directory FIRST." >&2
                echo "" >&2
                echo "   To bypass in emergencies: export KIMI_GATEKEEPER_BYPASS=1" >&2
                exit 2
            elif [ "$TDD_STATE" = "red" ]; then
                echo "⚠️  TDD WARNING: Test was written but no production code followed." >&2
                echo "   Either complete the implementation or remove the unused test." >&2
            else
                echo "✅ TDD: Test-first discipline verified ($TEST_COUNT test(s), $PROD_COUNT prod file(s))." >&2
            fi
        fi
    fi
fi

# ── Alignment (grill-me) Hard Gate Check ──────────────────────────────────────
if [ -n "$SESSION_ID" ]; then
    STATE_FILE_OLD="/tmp/kimi_gatekeeper_${SESSION_ID}.json"
    STATE_FILE_NEW="${HOME}/.kimi/.gatekeeper/kimi_gatekeeper_${SESSION_ID}.json"
    if [ -f "$STATE_FILE_NEW" ]; then
        STATE_FILE="$STATE_FILE_NEW"
    else
        STATE_FILE="$STATE_FILE_OLD"
    fi
    if [ -f "$STATE_FILE" ] && command -v jq &> /dev/null; then
        ALIGNMENT_DONE=$(jq -r '.alignment_completed // false' "$STATE_FILE" 2>/dev/null || echo "false")
        SWARM_REQUIRED=$(jq -r '.swarm_required // false' "$STATE_FILE" 2>/dev/null || echo "false")
        
        if [ "$SWARM_REQUIRED" = "true" ] && [ "$ALIGNMENT_DONE" != "true" ]; then
            echo "🔒 ALIGNMENT HARD GATE — Session cannot end." >&2
            echo "   Non-trivial work requires alignment BEFORE coding." >&2
            echo "" >&2
            echo "   Write an alignment artifact to .kimi/plans/ containing:" >&2
            echo "   - ALIGNMENT COMPLETE" >&2
            echo "   - GRILL STATUS: PASS" >&2
            echo "" >&2
            echo "   Use /skill:grill-me to interview the user first." >&2
            echo "" >&2
            echo "   To bypass in emergencies: export KIMI_GATEKEEPER_BYPASS=1" >&2
            exit 2
        elif [ "$ALIGNMENT_DONE" = "true" ]; then
            echo "✅ Alignment: Requirements aligned before coding." >&2
        fi
    fi
fi

# ── Anti-Slop Session-End Validation ────────────────────────────────────────────
if [ -n "$SESSION_ID" ]; then
    STATE_FILE_OLD="/tmp/kimi_gatekeeper_${SESSION_ID}.json"
    STATE_FILE_NEW="${HOME}/.kimi/.gatekeeper/kimi_gatekeeper_${SESSION_ID}.json"
    if [ -f "$STATE_FILE_NEW" ]; then
        STATE_FILE="$STATE_FILE_NEW"
    else
        STATE_FILE="$STATE_FILE_OLD"
    fi
    if [ -f "$STATE_FILE" ] && command -v jq &> /dev/null; then
        ERROR_RECOVERY=$(jq -r '.error_recovery_mode // false' "$STATE_FILE" 2>/dev/null || echo "false")
        CONSEC_WRITES=$(jq -r '.consecutive_writes_without_read // 0' "$STATE_FILE" 2>/dev/null || echo "0")
        TOOL_COUNT=$(jq -r '.tool_use_count // 0' "$STATE_FILE" 2>/dev/null || echo "0")
        LAST_CKPT=$(jq -r '.last_checkpoint_at // 0' "$STATE_FILE" 2>/dev/null || echo "0")
        
        if [ "$ERROR_RECOVERY" = "true" ]; then
            LAST_ERROR=$(jq -r '.last_error_brief // "unknown"' "$STATE_FILE" 2>/dev/null || echo "unknown")
            echo "⚠️  ANTI-SLOP WARNING: Session ended while in error recovery mode." >&2
            echo "   Last error: $LAST_ERROR" >&2
            echo "   The agent did not resolve the failure before ending." >&2
            echo "" >&2
        fi
        
        if [ "$CONSEC_WRITES" -ge 3 ]; then
            echo "⚠️  ANTI-SLOP WARNING: Session ended after $CONSEC_WRITES consecutive writes without reading." >&2
            echo "   The agent may have been patching blindly at the end." >&2
            echo "" >&2
        fi
        
        # Check if checkpoint interval was ever exceeded
        if [ "$TOOL_COUNT" -gt 0 ] && [ "$LAST_CKPT" -gt 0 ]; then
            CKPT_INTERVAL=$(jq -r '.checkpoint_interval // 15' "$STATE_FILE" 2>/dev/null || echo "15")
            if [ "$((TOOL_COUNT - LAST_CKPT))" -gt "$CKPT_INTERVAL" ]; then
                echo "⚠️  ANTI-SLOP WARNING: Last checkpoint was $((TOOL_COUNT - LAST_CKPT)) tool uses ago (interval: $CKPT_INTERVAL)." >&2
                echo "   Consider writing a cognitive checkpoint artifact before ending." >&2
                echo "" >&2
            fi
        fi
    fi
fi

# ── Uncommitted Changes Check ─────────────────────────────────────────────────
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

# ── State Cleanup (only after all gates pass) ─────────────────────────────────
if [ -n "$SESSION_ID" ]; then
    STATE_FILE_OLD="/tmp/kimi_gatekeeper_${SESSION_ID}.json"
    STATE_FILE_NEW="${HOME}/.kimi/.gatekeeper/kimi_gatekeeper_${SESSION_ID}.json"
    if [ -f "$STATE_FILE_NEW" ]; then
        STATE_FILE="$STATE_FILE_NEW"
    else
        STATE_FILE="$STATE_FILE_OLD"
    fi
    # Also check new state directory location
    STATE_FILE_NEW="${HOME}/.kimi/.gatekeeper/kimi_gatekeeper_${SESSION_ID}.json"
    rm -f "$STATE_FILE" "$STATE_FILE_NEW" 2>/dev/null || true
fi

# ── Failing Tests Check (idempotent: run once per session) ────────────────────
TEST_FLAG="/tmp/kimi_tests_run_${SESSION_ID}"
if [ ! -f "$TEST_FLAG" ] && [ -f "package.json" ] && grep -q '"test"' package.json; then
    if command -v npm &> /dev/null; then
        echo "Running tests before session end..." >&2
        npm test 2>&1 | tail -5 >&2
        touch "$TEST_FLAG"
    fi
fi

exit 0
