#!/usr/bin/env bash
# Checklist runner for SHUTDOWN.md. Does not enforce anything by itself (a shell
# script can't judge whether your reasoning is recorded correctly) — it flags the
# mechanical things that are easy to forget, so the actual shutdown procedure in
# SHUTDOWN.md gets followed in full.
#
# Usage: .ai/scripts/end_session.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(cd "$AI_DIR/.." && pwd)"
cd "$REPO_ROOT"

WARNINGS=0
note() { echo "  - $1"; WARNINGS=$((WARNINGS + 1)); }

echo "=== Shutdown checklist (see .ai/SHUTDOWN.md for the full procedure) ==="
echo

# 1. Is there a session file for today?
TODAY="$(date +%Y-%m-%d)"
if ! find "$AI_DIR/sessions" -maxdepth 1 -name "${TODAY}-*.md" -newer "$AI_DIR/PROJECT.md" 2>/dev/null | grep -q .; then
  if ! find "$AI_DIR/sessions" -maxdepth 1 -name "${TODAY}-*.md" | grep -q .; then
    note "No session file found for today ($TODAY) under .ai/sessions/. Run new_session.sh, or create one now from templates/session.md."
  fi
fi

# 2. Does SESSION_LOG.md mention today's date?
if ! grep -q "$TODAY" "$AI_DIR/SESSION_LOG.md" 2>/dev/null; then
  note "SESSION_LOG.md has no row for today ($TODAY). Add one (SHUTDOWN.md step 7)."
fi

# 3. Are there uncommitted changes to code without matching .ai/ updates?
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  CODE_CHANGED=$(git status --porcelain -- src tests 2>/dev/null | wc -l | tr -d ' ')
  AI_CHANGED=$(git status --porcelain -- .ai 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$CODE_CHANGED" -gt 0 && "$AI_CHANGED" -eq 0 ]]; then
    note "src/ or tests/ have uncommitted changes but .ai/ has none. Did you update TASKS.md / FILE_INDEX.md / CHANGELOG.md?"
  fi
fi

# 4. Quick STATE.md / TASKS.md sanity: both should have been touched together if either was.
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  STATE_CHANGED=$(git status --porcelain -- .ai/STATE.md 2>/dev/null | wc -l | tr -d ' ')
  TASKS_CHANGED=$(git status --porcelain -- .ai/TASKS.md 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$STATE_CHANGED" -gt 0 && "$TASKS_CHANGED" -eq 0 ]]; then
    note "STATE.md changed but TASKS.md didn't. Confirm they still agree (SHUTDOWN.md step 8)."
  fi
fi

echo
if [[ "$WARNINGS" -eq 0 ]]; then
  echo "No mechanical issues found. Still confirm by hand:"
else
  echo "$WARNINGS item(s) flagged above. Also confirm by hand:"
fi
echo "  - FILE_INDEX.md has a row for every file you created this session"
echo "  - CHANGELOG.md's Unreleased section has an entry for this session's changes"
echo "  - Your session file's 'Left for next session' and 'Warnings' sections are filled in"
echo "  - A commit message is ready, with an 'AI-Session: sessions/<file>.md' trailer"
echo
echo "Run 'python3 .ai/scripts/validate.py' to check FILE_INDEX.md against the filesystem."
