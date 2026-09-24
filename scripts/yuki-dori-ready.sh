#!/usr/bin/env bash
# yuki-dori-ready.sh - Prepare session for both Yuki and Project-Dori systems
#
# This script integrates Project-Yuki and Project-Dori to ensure every session
# starts with both systems ready for use.
#
# Usage:
#   ./scripts/yuki-dori-ready.sh          # Full preparation
#   ./scripts/yuki-dori-ready.sh --quick  # Skip time-consuming steps
#   ./scripts/yuki-dori-ready.sh --help   # Show help

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_CONTEXT="$REPO_ROOT/.ai-context"
YUKI_INDEX="$REPO_ROOT/.file_index"
QUICK_MODE=false

show_help() {
    echo "yuki-dori-ready.sh - Prepare session for Yuki and Project-Dori systems"
    echo ""
    echo "Usage:"
    echo "  ./scripts/yuki-dori-ready.sh          # Full preparation (recommended)"
    echo "  ./scripts/yuki-dori-ready.sh --quick  # Skip time-consuming steps"
    echo "  ./scripts/yuki-dori-ready.sh --help   # Show help"
    echo ""
    echo "What it does:"
    echo "  1. Updates Project-Dori state (scan for changes)"
    echo "  2. Ensures Yuki file index is current"
    echo "  3. Provides integrated session briefing"
    echo "  4. Validates both systems are ready"
    echo ""
    echo "Yuki Components: Prompt optimization, Knowledge graph, Best practices, File indexing"
    echo "Project-Dori Components: PROJECT_INDEX, STATE.json, CHANGELOG, ROADMAP, TASKS"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Error: Unknown option '$1'"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "🚀 Preparing session for Yuki and Project-Dori systems..."

# 1. Project-Dori Preparation
echo "📋 Updating Project-Dori project state..."
if [[ ! -d "$AI_CONTEXT" ]]; then
    echo "⚠️  .ai-context directory not found. Initializing Project-Dori..."
    python "$REPO_ROOT/scripts/scan_index.py" --root "$REPO_ROOT"
else
    # Update file fingerprints and state
    python "$REPO_ROOT/scripts/scan_index.py" --root "$REPO_ROOT" ${QUICK_MODE:+--quiet}
fi

# 2. Yuki File Index Preparation
echo "🔍 Updating Yuki file index..."
if [[ "$QUICK_MODE" == false ]]; then
    # Full rebuild - ensures completeness
    "$REPO_ROOT/scripts/file_index.sh" --build
else
    # Quick check - only rebuild if index is missing or very old
    if [[ ! -f "$YUKI_INDEX" ]] || [[ $(find "$REPO_ROOT" -type f -newer "$YUKI_INDEX" 2>/dev/null | wc -l) -gt 0 ]]; then
        echo "🔄 File index outdated or missing - rebuilding..."
        "$REPO_ROOT/scripts/file_index.sh" --build
    else
        echo "✅ File index is current"
    fi
fi

# 3. Integrated Session Briefing
echo "📖 Generating integrated session briefing..."
# Calculate values for briefing
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
STATE_TIME="unknown"
if [[ -f "$AI_CONTEXT/STATE.json" ]]; then
    STATE_TIME=$(date -r "$AI_CONTEXT/STATE.json" '+%H:%M:%S' 2>/dev/null || echo "unknown")
fi

INDEXED_COUNT="0"
if [[ -f "$YUKI_INDEX" ]]; then
    INDEXED_COUNT=$(wc -l < "$YUKI_INDEX" 2>/dev/null || echo "0")
fi

LAST_CHANGE="unknown"
if git rev-parse --git-dir > /dev/null 2>&1; then
    LAST_CHANGE=$(git log -1 --format="%cd" --date=short 2>/dev/null || echo "unknown")
fi

TODAY_FOCUS="• Check TASKS.md for open items"
if [[ -f "$AI_CONTEXT/TASKS.md" ]]; then
    TODAY_FOCUS=$(grep -E '^\* \[ \]' "$AI_CONTEXT/TASKS.md" | head -3)
    if [[ -z "$TODAY_FOCUS" ]]; then
        TODAY_FOCUS="• Check TASKS.md for open items"
    fi
fi

# Generate briefing with calculated values
cat > "$REPO_ROOT/.yuki-dori-briefing.md" << EOF
# 🚀 Yuki-Dori Session Briefing
## $CURRENT_TIME

### 📊 Project Status (Project-Dori)
- **State updated**: $STATE_TIME
- **Indexed files**: $INDEXED_COUNT files tracked
- **Last change**: $LAST_CHANGE

### 🎯 Today's Focus (from TODOs)
$TODAY_FOCUS

### 🔧 Yuki Systems Ready
- **File indexing**: → ./scripts/file_index.sh --search "<pattern>"
- **Prompt optimization**: Use Yuki principles for clear intent formulation
- **Knowledge graph**: Available if graphify-out/ exists
- **Best practices**: Apply karpathy-guidelines throughout session

### 📚 Quick Reference
EOF

# Add project-specific info if available
if [[ -f "$AI_CONTEXT/PROJECT_INDEX.md" ]]; then
    echo "" >> "$REPO_ROOT/.yuki-dori-briefing.md"
    echo "### 🏗️ Project Overview" >> "$REPO_ROOT/.yuki-dori-briefing.md"
    grep -A 10 "^# [^#]" "$AI_CONTEXT/PROJECT_INDEX.md" | head -5 >> "$REPO_ROOT/.yuki-dori-briefing.md" || true
fi

# Add recent changelog entries
if [[ -f "$AI_CONTEXT/CHANGELOG.md" ]] && [[ -s "$AI_CONTEXT/CHANGELOG.md" ]]; then
    echo "" >> "$REPO_ROOT/.yuki-dori-briefing.md"
    echo "### 📝 Recent Changes" >> "$REPO_ROOT/.yuki-dori-briefing.md"
    tail -5 "$AI_CONTEXT/CHANGELOG.md" >> "$REPO_ROOT/.yuki-dori-briefing.md" || true
fi

echo ""
echo "✅ Session preparation complete!"
echo ""
echo "📖 Briefing saved to: .yuki-dori-briefing.md"
echo "🔍 To search files: ./scripts/file_index.sh --search \"<pattern>\""
echo "📋 To see tasks: cat .ai-context/TASKS.md"
echo "📊 To check state: ls -la .ai-context/"
echo ""
echo "💡 Tip: Add this to your shell profile or IDE terminal startup:"
echo "   alias yd-ready='./scripts/yuki-dori-ready.sh'"
exit 0
EOF